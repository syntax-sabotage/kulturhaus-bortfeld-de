# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json


class DashboardController(http.Controller):

    @http.route('/dashboard/data', type='json', auth='user')
    def get_dashboard_data(self):
        """Return dashboard data including KPIs and user-configured cards"""
        user = request.env.user
        
        # KPI calculation
        kpis = {
            'total_members': self._get_members_count(),
            'upcoming_events': self._get_upcoming_events_count(),
            'website_info': 'Kulturhaus Website'
        }
        
        # Get user-configured cards or fallback to static cards
        try:
            user_sections = self._get_user_cards()
            if user_sections:
                cards = user_sections
            else:
                # Fallback to static cards (convert to sections format)
                static_cards = self._get_static_cards()
                cards = [{
                    'name': 'Main',
                    'sequence': 10,
                    'cards': static_cards
                }] if static_cards else []
        except Exception:
            # If user cards fail, use static cards
            static_cards = self._get_static_cards()
            cards = [{
                'name': 'Main',
                'sequence': 10,
                'cards': static_cards
            }] if static_cards else []
        
        return {
            'kpis': kpis,
            'cards': cards,
            'show_kpis': user.show_kpis,
            'theme': user.dashboard_theme,
            'layout': user.dashboard_layout,
        }
    
    def _get_members_count(self):
        """Get total members count"""
        try:
            # First try to count active membership lines
            if 'membership.membership_line' in request.env:
                membership_count = request.env['membership.membership_line'].search_count([
                    ('state', 'in', ['invoiced', 'paid', 'free'])
                ])
                if membership_count > 0:
                    return membership_count
            
            # Fallback to individual partners (exclude companies and internal users)
            return request.env['res.partner'].search_count([
                ('is_company', '=', False),
                ('category_id', '!=', False)  # Partners with categories (likely members)
            ])
        except:
            # Final fallback: count all individual partners
            try:
                return request.env['res.partner'].search_count([('is_company', '=', False)])
            except:
                return 0
    
    def _get_upcoming_events_count(self):
        """Get upcoming events count (next 6 months)"""
        try:
            from datetime import datetime, timedelta
            
            # Calculate date range for next 6 months
            today = datetime.now().date()
            six_months_later = today + timedelta(days=180)  # Approximately 6 months
            
            if 'event.event' in request.env:
                return request.env['event.event'].search_count([
                    ('date_begin', '>=', today.strftime('%Y-%m-%d')),
                    ('date_begin', '<=', six_months_later.strftime('%Y-%m-%d')),
                    ('stage_id.is_done', '=', False)  # Exclude completed events
                ])
            else:
                return 0
        except:
            return 0
    
    def _get_user_cards(self):
        """Get user-configured dashboard cards grouped by sections"""
        user = request.env.user
        
        # Get user's configured cards ordered by sections
        card_configs = user.dashboard_card_ids.filtered('is_active')
        
        # Group cards by section
        sections = {}
        for card_config in card_configs:
            section_name = card_config.section_name or 'Main'
            section_sequence = card_config.section_sequence or 10
            
            if section_name not in sections:
                sections[section_name] = {
                    'name': section_name,
                    'sequence': section_sequence,
                    'cards': []
                }
            
            card_data = {
                'id': card_config.name.lower().replace(' ', '_'),
                'title': card_config.name,
                'description': card_config.description,
                'icon': card_config.icon,
                'color': card_config.color,
                'section': section_name,
                'action': self._build_action_from_config(card_config)
            }
            sections[section_name]['cards'].append(card_data)
        
        # Convert to list and sort by section sequence
        section_list = []
        for section_data in sections.values():
            section_list.append(section_data)
        section_list.sort(key=lambda x: x['sequence'])
        
        return section_list
    
    def _build_action_from_config(self, card_config):
        """Build action object from card configuration"""
        if card_config.action_type == 'window' and card_config.action_window_id:
            action = card_config.action_window_id
            return {
                'type': 'ir.actions.act_window',
                'name': action.name,
                'res_model': action.res_model,
                'view_mode': action.view_mode,
                'views': action.views or [],
                'target': action.target or 'current',
                'domain': action.domain or [],
            }
        elif card_config.action_type == 'url' and card_config.action_url:
            return {
                'type': 'ir.actions.act_url',
                'url': card_config.action_url,
                'target': 'new',
            }
        elif card_config.action_type == 'custom' and card_config.custom_action_code:
            # For custom actions, return the code to be executed client-side
            return {
                'type': 'custom',
                'code': card_config.custom_action_code,
            }
        
        # Fallback to empty action
        return {}
    
    def _get_static_cards(self):
        """Get static navigation cards (no customization)"""
        user = request.env.user
        cards = []
        
        # Members card
        cards.append({
            'id': 'members',
            'title': 'Mitglieder',
            'description': 'Vereinsmitglieder verwalten',
            'icon': 'fa-users',
            'color': 'success',
            'action': self._get_members_action()
        })
        
        # Events card
        cards.append({
            'id': 'events',
            'title': 'Veranstaltungen', 
            'description': 'Events und Termine verwalten',
            'icon': 'fa-calendar',
            'color': 'warning',
            'action': self._get_events_action()
        })
        
        # Projects card
        cards.append({
            'id': 'projects',
            'title': 'Projekte',
            'description': 'Projekte und Aufgaben verwalten',
            'icon': 'fa-tasks',
            'color': 'info',
            'action': self._get_projects_action()
        })
        
        # Settings card (only for administrators)
        if user.has_group('base.group_system'):
            cards.append({
                'id': 'settings',
                'title': 'Einstellungen',
                'description': 'Systemeinstellungen',
                'icon': 'fa-cog',
                'color': 'secondary',
                'action': self._get_users_action()
            })
            
        return cards
    
    def _get_members_action(self):
        """Get members action definition"""
        try:
            members_action = request.env.ref('membership.action_membership_members')
            return {
                'type': 'ir.actions.act_window',
                'name': members_action.name,
                'res_model': members_action.res_model,
                'view_mode': members_action.view_mode,
                'views': members_action.views or [],
                'target': members_action.target,
                'domain': members_action.domain,
            }
        except:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Mitglieder',
                'res_model': 'res.partner',
                'view_mode': 'kanban,list,form',
                'views': [],
                'target': 'current',
                'domain': [('membership_state', '!=', 'none')],
            }
    
    def _get_events_action(self):
        """Get events action definition"""
        try:
            events_action = request.env.ref('event.action_event_view')
            return {
                'type': 'ir.actions.act_window',
                'name': events_action.name,
                'res_model': events_action.res_model,
                'view_mode': events_action.view_mode,
                'views': events_action.views or [],
                'target': events_action.target,
                'domain': events_action.domain if events_action.domain else [],
            }
        except:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Veranstaltungen',
                'res_model': 'event.event',
                'view_mode': 'kanban,calendar,list,form',
                'views': [],
                'target': 'current',
                'domain': [],
            }
    
    def _get_projects_action(self):
        """Get projects action definition"""
        try:
            projects_action = request.env.ref('project.open_view_project_all')
            return {
                'type': 'ir.actions.act_window',
                'name': projects_action.name,
                'res_model': projects_action.res_model,
                'view_mode': projects_action.view_mode,
                'views': projects_action.views or [],
                'target': projects_action.target,
                'domain': projects_action.domain if projects_action.domain else [],
            }
        except:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Projekte',
                'res_model': 'project.project',
                'view_mode': 'kanban,list,form',
                'views': [],
                'target': 'current',
                'domain': [],
            }
    
    def _get_users_action(self):
        """Get users action definition"""
        try:
            users_action = request.env.ref('base.action_res_users')
            return {
                'type': 'ir.actions.act_window',
                'name': users_action.name,
                'res_model': users_action.res_model,
                'view_mode': users_action.view_mode,
                'views': users_action.views or [],
                'target': users_action.target,
                'domain': users_action.domain if users_action.domain else [],
            }
        except:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Benutzer',
                'res_model': 'res.users',
                'view_mode': 'kanban,list,form',
                'views': [],
                'target': 'current',
                'domain': [],
            }