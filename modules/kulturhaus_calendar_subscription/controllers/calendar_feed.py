# -*- coding: utf-8 -*-
import hashlib
import logging
import pytz
from datetime import datetime, timedelta
from werkzeug.exceptions import NotFound

from odoo import http, fields
from odoo.http import request

try:
    from icalendar import Calendar, Event, vCalAddress, vText, Timezone
    from icalendar.prop import vDDDTypes
except ImportError:
    Calendar = Event = vCalAddress = vText = Timezone = vDDDTypes = None
    logging.getLogger(__name__).warning('icalendar library not installed. Calendar subscription will not work.')

_logger = logging.getLogger(__name__)


class CalendarFeedController(http.Controller):
    
    @http.route('/calendar/ics/<string:token>.ics', type='http', auth='public', sitemap=False, csrf=False)
    def calendar_feed(self, token, **kwargs):
        """
        Public endpoint to serve iCal calendar feeds.
        Uses token-based authentication for security.
        """
        if not Calendar:
            return request.not_found()
        
        # Find token using hash for security
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        subscription = request.env['calendar.subscription.token'].sudo().search([
            ('token_hash', '=', token_hash),
            ('active', '=', True)
        ], limit=1)
        
        if not subscription:
            _logger.warning(f'Invalid or inactive calendar token accessed: {token[:8]}...')
            raise NotFound()
        
        # Get user agent for tracking
        user_agent = request.httprequest.headers.get('User-Agent', '')
        
        # Update access tracking
        subscription.sudo().write({
            'last_accessed': fields.Datetime.now(),
            'access_count': subscription.access_count + 1,
            'last_user_agent': user_agent[:200],  # Limit length
        })
        
        # Generate iCal content
        try:
            cal_content = self._generate_ical(subscription, user_agent)
        except Exception as e:
            _logger.error(f'Error generating calendar for token {subscription.id}: {str(e)}')
            return request.not_found()
        
        # Prepare response headers
        headers = [
            ('Content-Type', 'text/calendar; charset=utf-8'),
            ('Content-Disposition', f'inline; filename="kulturhaus_calendar_{subscription.id}.ics"'),
            ('Cache-Control', 'no-cache, no-store, must-revalidate'),
            ('Pragma', 'no-cache'),
            ('Expires', '0'),
            ('X-Robots-Tag', 'noindex, nofollow'),
        ]
        
        # Add caching headers to help calendar clients
        if cal_content:
            # Add ETag for cache validation
            content_hash = hashlib.md5(cal_content).hexdigest()
            headers.append(('ETag', f'"{content_hash}"'))
            
            # Add Last-Modified header
            last_modified = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
            headers.append(('Last-Modified', last_modified))
            
            # Suggest refresh interval (not all clients respect this)
            headers.append(('X-PUBLISHED-TTL', 'PT30M'))  # 30 minutes
        
        return request.make_response(cal_content, headers=headers)
    
    def _generate_ical(self, subscription, user_agent=''):
        """Generate iCal content for the subscription"""
        cal = Calendar()
        
        # Calendar properties
        cal.add('prodid', '-//Kulturhaus Bortfeld//Odoo Calendar Feed//DE')
        cal.add('version', '2.0')
        cal.add('calscale', 'GREGORIAN')
        cal.add('method', 'PUBLISH')
        cal.add('x-wr-calname', f'Kulturhaus - {subscription.name}')
        cal.add('x-wr-caldesc', f'Calendar subscription for {subscription.user_id.name}')
        cal.add('x-wr-timezone', 'Europe/Berlin')
        
        # Add proper VTIMEZONE component for Apple Calendar compatibility
        berlin_tz = self._create_berlin_timezone()
        cal.add_component(berlin_tz)
        
        # Refresh interval hint based on client
        if 'Darwin' in user_agent or 'iOS' in user_agent:
            cal.add('x-apple-calendar-color', '#2196F3')  # Blue color for Apple Calendar
            cal.add('refresh-interval;value=duration', 'PT15M')  # 15 minutes for Apple
        elif 'Google' in user_agent:
            cal.add('refresh-interval;value=duration', 'PT1H')  # 1 hour for Google (they cache heavily anyway)
        else:
            cal.add('refresh-interval;value=duration', 'PT30M')  # 30 minutes default
        
        # Get calendar events
        domain = subscription.get_calendar_domain()
        events = request.env['calendar.event'].sudo().search(domain, order='start asc')
        
        _logger.info(f'Generating calendar feed for subscription {subscription.id}: {len(events)} events')
        
        # Add events to calendar
        for event in events:
            ical_event = Event()
            
            # Unique ID (important for updates)
            ical_event.add('uid', f'odoo-event-{event.id}@kulturhaus-bortfeld.de')
            
            # Basic properties
            ical_event.add('summary', event.name or 'Untitled Event')
            
            # Handle timezone properly - NO DOUBLE CONVERSION
            if event.allday:
                # All-day events should be date only (no timezone conversion needed)
                ical_event.add('dtstart', event.start_date)
                ical_event.add('dtend', event.stop_date)
            else:
                # Regular events - Odoo stores datetime in UTC, need to convert to Berlin timezone
                try:
                    # Get datetimes from Odoo (stored as UTC)
                    start_dt = event.start
                    stop_dt = event.stop
                    
                    BERLIN_TZ = pytz.timezone('Europe/Berlin')
                    UTC_TZ = pytz.UTC
                    
                    # If timezone-naive (stored as UTC), localize as UTC first
                    if start_dt.tzinfo is None:
                        start_dt = UTC_TZ.localize(start_dt)
                        _logger.debug(f'Event {event.id} start was naive, localized as UTC: {start_dt}')
                    
                    if stop_dt.tzinfo is None:
                        stop_dt = UTC_TZ.localize(stop_dt)
                        _logger.debug(f'Event {event.id} stop was naive, localized as UTC: {stop_dt}')
                    
                    # Convert from UTC to Berlin timezone
                    start_berlin = start_dt.astimezone(BERLIN_TZ)
                    stop_berlin = stop_dt.astimezone(BERLIN_TZ)
                    
                    _logger.debug(f'Event {event.id} converted times: start={start_berlin}, stop={stop_berlin}')
                    
                    # Add events with proper Berlin timezone
                    ical_event.add('dtstart', start_berlin)
                    ical_event['dtstart'].params['TZID'] = 'Europe/Berlin'
                    ical_event.add('dtend', stop_berlin)
                    ical_event['dtend'].params['TZID'] = 'Europe/Berlin'
                    
                except Exception as e:
                    _logger.error(f'Error processing event {event.id} timezone: {str(e)}')
                    # Skip this event to prevent calendar corruption
                    continue
            
            # Timestamps
            ical_event.add('dtstamp', fields.Datetime.from_string(event.write_date or event.create_date))
            ical_event.add('created', fields.Datetime.from_string(event.create_date))
            ical_event.add('last-modified', fields.Datetime.from_string(event.write_date or event.create_date))
            
            # Optional fields
            if event.location:
                ical_event.add('location', event.location)
            
            if event.description:
                # Clean HTML from description
                description = event.description
                # Simple HTML stripping (you might want to use html2text for better results)
                import re
                description = re.sub('<.*?>', '', description)
                ical_event.add('description', description)
            
            # Categories from event types
            if event.categ_ids:
                categories = [cat.name for cat in event.categ_ids]
                ical_event.add('categories', categories)
            
            # Status
            if hasattr(event, 'state'):
                status_map = {
                    'draft': 'TENTATIVE',
                    'confirmed': 'CONFIRMED',
                    'cancelled': 'CANCELLED',
                }
                status = status_map.get(event.state, 'CONFIRMED')
                ical_event.add('status', status)
            
            # Privacy
            if event.privacy:
                class_map = {
                    'public': 'PUBLIC',
                    'private': 'PRIVATE',
                    'confidential': 'CONFIDENTIAL',
                }
                ical_event.add('class', class_map.get(event.privacy, 'PUBLIC'))
            
            # Organizer (event creator)
            if event.user_id and event.user_id.email:
                organizer = vCalAddress(f'MAILTO:{event.user_id.email}')
                organizer.params['cn'] = vText(event.user_id.name)
                ical_event.add('organizer', organizer, encode=0)
            
            # Attendees (only if including private data)
            if subscription.include_private and event.partner_ids:
                for partner in event.partner_ids[:20]:  # Limit to prevent huge files
                    if partner.email:
                        attendee = vCalAddress(f'MAILTO:{partner.email}')
                        attendee.params['cn'] = vText(partner.name)
                        attendee.params['role'] = vText('REQ-PARTICIPANT')
                        ical_event.add('attendee', attendee, encode=0)
            
            # Skip alarms for now - can be added later
            
            cal.add_component(ical_event)
        
        # Return the calendar as bytes
        return cal.to_ical()
    
    def _create_berlin_timezone(self):
        """Create proper VTIMEZONE component for Europe/Berlin with DST rules"""
        from icalendar import Timezone
        from icalendar.prop import vDDDTypes
        from datetime import datetime, timedelta
        
        # Create timezone component
        tz = Timezone()
        tz.add('tzid', 'Europe/Berlin')
        
        # Standard time (CET - Central European Time, UTC+1)
        standard = Event()
        standard.name = "STANDARD"
        standard.add('dtstart', datetime(1970, 10, 25, 3, 0, 0))  # Last Sunday in October at 3 AM
        standard.add('rrule', {'freq': 'yearly', 'bymonth': 10, 'byday': '-1su'})
        standard.add('tzoffsetfrom', timedelta(hours=2))  # From CEST (UTC+2)
        standard.add('tzoffsetto', timedelta(hours=1))    # To CET (UTC+1)
        standard.add('tzname', 'CET')
        
        # Daylight time (CEST - Central European Summer Time, UTC+2)  
        daylight = Event()
        daylight.name = "DAYLIGHT"
        daylight.add('dtstart', datetime(1970, 3, 29, 2, 0, 0))   # Last Sunday in March at 2 AM
        daylight.add('rrule', {'freq': 'yearly', 'bymonth': 3, 'byday': '-1su'})
        daylight.add('tzoffsetfrom', timedelta(hours=1))  # From CET (UTC+1)
        daylight.add('tzoffsetto', timedelta(hours=2))    # To CEST (UTC+2)
        daylight.add('tzname', 'CEST')
        
        # Add components to timezone
        tz.add_component(standard)
        tz.add_component(daylight)
        
        return tz
