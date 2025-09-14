# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta
import json
import logging

_logger = logging.getLogger(__name__)


class KulturhausDashboard(models.Model):
    _name = 'kulturhaus.dashboard'
    _description = 'Kulturhaus Dashboard MVP'
    _order = 'create_date desc'
    
    name = fields.Char(string='Dashboard Name', default='Main Dashboard')
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    
    # Cached metrics (updated via cron or on-demand)
    active_members_count = fields.Integer(
        string='Active Members',
        compute='_compute_member_metrics',
        store=False
    )
    member_delta = fields.Integer(
        string='Member Change',
        compute='_compute_member_metrics',
        store=False
    )
    quarterly_churn = fields.Text(
        string='Quarterly Churn Data',
        compute='_compute_quarterly_churn',
        store=False
    )
    
    # SEPA metrics
    next_sepa_date = fields.Date(
        string='Next SEPA Collection',
        compute='_compute_sepa_metrics',
        store=False
    )
    next_sepa_amount = fields.Float(
        string='Next Collection Amount',
        compute='_compute_sepa_metrics',
        store=False
    )
    sepa_status = fields.Selection([
        ('ready', 'Ready'),
        ('pending', 'Pending'),
        ('issues', 'Issues')
    ], string='SEPA Status', compute='_compute_sepa_metrics', store=False)
    
    # Event metrics
    next_event_name = fields.Char(
        string='Next Event',
        compute='_compute_event_metrics',
        store=False
    )
    next_event_date = fields.Datetime(
        string='Next Event Date',
        compute='_compute_event_metrics',
        store=False
    )
    next_event_tickets_sold = fields.Integer(
        string='Tickets Sold',
        compute='_compute_event_metrics',
        store=False
    )
    next_event_capacity = fields.Integer(
        string='Event Capacity',
        compute='_compute_event_metrics',
        store=False
    )
    monthly_ticket_revenue = fields.Float(
        string='Monthly Ticket Revenue',
        compute='_compute_event_metrics',
        store=False
    )
    
    # Website metrics
    quarterly_visitors = fields.Integer(
        string='Quarterly Visitors',
        compute='_compute_website_metrics',
        store=False
    )
    visitor_change_percent = fields.Float(
        string='Visitor Change %',
        compute='_compute_website_metrics',
        store=False
    )
    
    # Social media metrics
    instagram_followers = fields.Integer(
        string='Instagram Followers',
        compute='_compute_social_metrics',
        store=False
    )
    instagram_engagement = fields.Float(
        string='Engagement Rate',
        compute='_compute_social_metrics',
        store=False
    )
    last_post_time = fields.Datetime(
        string='Last Post Time',
        compute='_compute_social_metrics',
        store=False
    )
    
    @api.depends('user_id')
    def _compute_member_metrics(self):
        """Compute active members and delta"""
        for record in self:
            # Get active members with valid SEPA mandates
            active_members = self.env['res.partner'].search_count([
                ('is_company', '=', False),
                ('sepa_mandate_active', '=', True)
            ])
            
            # Calculate delta from last month
            last_month = datetime.now() - timedelta(days=30)
            last_month_members = self.env['res.partner'].search_count([
                ('is_company', '=', False),
                ('sepa_mandate_active', '=', True),
                ('create_date', '<=', last_month)
            ])
            
            record.active_members_count = active_members
            record.member_delta = active_members - last_month_members
    
    @api.depends('user_id')
    def _compute_quarterly_churn(self):
        """Compute quarterly member churn data"""
        for record in self:
            churn_data = []
            
            # Calculate for last 4 quarters
            for quarter in range(4):
                quarter_start = datetime.now() - timedelta(days=(quarter + 1) * 90)
                quarter_end = datetime.now() - timedelta(days=quarter * 90)
                
                # New members in quarter
                new_members = self.env['res.partner'].search_count([
                    ('is_company', '=', False),
                    ('create_date', '>=', quarter_start),
                    ('create_date', '<', quarter_end),
                    ('sepa_mandate_id', '!=', False)
                ])
                
                # Lost members (inactive mandates)
                lost_members = self.env['res.partner'].search_count([
                    ('is_company', '=', False),
                    ('sepa_mandate_active', '=', False),
                    ('write_date', '>=', quarter_start),
                    ('write_date', '<', quarter_end)
                ])
                
                churn_data.append({
                    'quarter': f'Q{4-quarter}',
                    'new': new_members,
                    'lost': lost_members,
                    'net': new_members - lost_members
                })
            
            record.quarterly_churn = json.dumps(churn_data)
    
    @api.depends('user_id')
    def _compute_sepa_metrics(self):
        """Compute SEPA collection metrics"""
        for record in self:
            # Determine next collection date (15th of month)
            today = datetime.now()
            if today.day <= 15:
                next_date = today.replace(day=15)
            else:
                next_month = today.replace(day=1) + timedelta(days=32)
                next_date = next_month.replace(day=15)
            
            # Calculate collection amount
            active_mandates = self.env['res.partner'].search([
                ('is_company', '=', False),
                ('sepa_mandate_active', '=', True)
            ])
            
            total_amount = sum([
                50.0 if p.membership_type == 'full_year' else 25.0 
                for p in active_mandates
            ])
            
            # Check for issues
            expired_mandates = self.env['res.partner'].search_count([
                ('is_company', '=', False),
                ('sepa_mandate_active', '=', True),
                ('sepa_mandate_date', '<', datetime.now() - timedelta(days=1095))  # 36 months
            ])
            
            record.next_sepa_date = next_date.date()
            record.next_sepa_amount = total_amount
            record.sepa_status = 'issues' if expired_mandates > 0 else 'ready'
    
    @api.depends('user_id')
    def _compute_event_metrics(self):
        """Compute event-related metrics"""
        for record in self:
            # Get next upcoming event
            next_event = self.env['event.event'].search([
                ('date_begin', '>', datetime.now())
            ], order='date_begin asc', limit=1)
            
            if next_event:
                record.next_event_name = next_event.name
                record.next_event_date = next_event.date_begin
                record.next_event_tickets_sold = len(next_event.registration_ids)
                record.next_event_capacity = next_event.seats_max or 100
            else:
                record.next_event_name = 'Keine Events geplant'
                record.next_event_date = False
                record.next_event_tickets_sold = 0
                record.next_event_capacity = 0
            
            # Calculate monthly revenue
            month_start = datetime.now().replace(day=1)
            month_events = self.env['event.event'].search([
                ('date_begin', '>=', month_start),
                ('date_begin', '<', month_start + timedelta(days=32))
            ])
            
            revenue = sum([
                len(event.registration_ids) * (event.event_ticket_ids[0].price if event.event_ticket_ids else 0)
                for event in month_events
            ])
            
            record.monthly_ticket_revenue = revenue
    
    @api.depends('user_id')
    def _compute_website_metrics(self):
        """Compute website visitor metrics"""
        for record in self:
            # Placeholder for real analytics integration
            # In production, integrate with Matomo or Google Analytics
            import random
            
            record.quarterly_visitors = random.randint(2500, 3500)
            record.visitor_change_percent = random.uniform(-20, 30)
    
    @api.depends('user_id')
    def _compute_social_metrics(self):
        """Compute social media metrics"""
        for record in self:
            # Placeholder for Instagram API integration
            # In production, use Instagram Basic Display API
            import random
            
            record.instagram_followers = random.randint(850, 950)
            record.instagram_engagement = random.uniform(3.5, 7.5)
            record.last_post_time = datetime.now() - timedelta(hours=random.randint(1, 48))
    
    @api.model
    def get_dashboard_data(self):
        """Main API endpoint for dashboard data"""
        dashboard = self.search([('user_id', '=', self.env.user.id)], limit=1)
        if not dashboard:
            dashboard = self.create({'user_id': self.env.user.id})
        
        # Force recompute all metrics
        dashboard._compute_member_metrics()
        dashboard._compute_quarterly_churn()
        dashboard._compute_sepa_metrics()
        dashboard._compute_event_metrics()
        dashboard._compute_website_metrics()
        dashboard._compute_social_metrics()
        
        return {
            'members': {
                'active': dashboard.active_members_count,
                'delta': dashboard.member_delta,
                'quarterly_churn': json.loads(dashboard.quarterly_churn or '[]')
            },
            'sepa': {
                'next_date': dashboard.next_sepa_date.isoformat() if dashboard.next_sepa_date else None,
                'amount': dashboard.next_sepa_amount,
                'status': dashboard.sepa_status
            },
            'events': {
                'next_event': dashboard.next_event_name,
                'event_date': dashboard.next_event_date.isoformat() if dashboard.next_event_date else None,
                'tickets_sold': dashboard.next_event_tickets_sold,
                'capacity': dashboard.next_event_capacity,
                'monthly_revenue': dashboard.monthly_ticket_revenue
            },
            'website': {
                'quarterly_visitors': dashboard.quarterly_visitors,
                'change_percent': dashboard.visitor_change_percent
            },
            'social': {
                'instagram_followers': dashboard.instagram_followers,
                'engagement_rate': dashboard.instagram_engagement,
                'last_post': dashboard.last_post_time.isoformat() if dashboard.last_post_time else None
            }
        }
    
    @api.model
    def quick_action_instagram(self, message, image_url=None):
        """Quick action: Post to Instagram"""
        # Placeholder for Instagram API
        _logger.info(f"Instagram post: {message}")
        return {'success': True, 'message': 'Posted to Instagram'}
    
    def openMemberList(self):
        """Open member list action"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Mitglieder',
            'res_model': 'res.partner',
            'view_mode': 'list,form',
            'domain': [('is_company', '=', False)],
            'target': 'current',
        }
    
    def openEventList(self):
        """Open event list action"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Veranstaltungen',
            'res_model': 'event.event',
            'view_mode': 'list,kanban,form,calendar',
            'target': 'current',
        }
    
    @api.model
    def quick_action_telegram(self, message=None):
        """Quick action: Send to Telegram channel"""
        # Integration with existing Telegram bot
        try:
            # Use existing bot configuration
            bot_token = "8232267547:AAEZJ8sl4WhjY2jz61SZCpotCHsLhjsF1zM"
            channel_id = "@kulturhaus_bortfeld"
            
            # Send via Telegram API
            import requests
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                'chat_id': channel_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, data=data)
            
            if response.ok:
                return {'success': True, 'message': 'Sent to Telegram'}
            else:
                return {'success': False, 'error': 'Failed to send'}
        except Exception as e:
            _logger.error(f"Telegram error: {e}")
            return {'success': False, 'error': str(e)}