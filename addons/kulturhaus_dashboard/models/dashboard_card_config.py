# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DashboardCardConfig(models.Model):
    _name = 'dashboard.card.config'
    _description = 'Dashboard Card Configuration'
    _order = 'user_id, section_sequence, section_name, sequence, name'

    # Basic fields
    user_id = fields.Many2one('res.users', string='User', required=True, ondelete='cascade', index=True)
    name = fields.Char(string='Card Name', required=True)
    description = fields.Text(string='Description')
    sequence = fields.Integer(string='Sequence', default=10)
    is_active = fields.Boolean(string='Active', default=True)
    
    # Section organization
    section_name = fields.Char(string='Section', default='Main', help='Group cards into named sections')
    section_sequence = fields.Integer(string='Section Order', default=10, help='Order of sections on dashboard')
    
    # Visual fields
    icon = fields.Char(string='Icon', default='fa-square', help='FontAwesome icon class')
    color = fields.Selection([
        ('primary', 'Primary Blue'),
        ('secondary', 'Secondary Gray'),
        ('success', 'Success Green'),
        ('warning', 'Warning Yellow'),
        ('danger', 'Danger Red'),
        ('info', 'Info Light Blue'),
        ('light', 'Light Gray'),
        ('dark', 'Dark Gray'),
    ], string='Color', default='primary')
    
    # Action configuration
    action_type = fields.Selection([
        ('window', 'Window Action'),
        ('url', 'URL Action'),
        ('custom', 'Custom Action'),
    ], string='Action Type', default='window', required=True)
    
    action_window_id = fields.Many2one('ir.actions.act_window', string='Window Action')
    action_url = fields.Char(string='URL')
    custom_action_code = fields.Text(string='Custom Action Code')
    
    @api.model
    def create_default_cards_for_user(self, user_id):
        """Create default dashboard cards for a user"""
        user = self.env['res.users'].browse(user_id)
        if not user.exists():
            return False
            
        # Remove existing cards first
        existing_cards = self.search([('user_id', '=', user_id)])
        existing_cards.unlink()
        
        # Default cards configuration
        default_cards = [
            {
                'name': 'Mitglieder',
                'description': 'Vereinsmitglieder verwalten',
                'icon': 'fa-users',
                'color': 'success',
                'sequence': 10,
                'section_name': 'Verwaltung',
                'section_sequence': 10,
                'action_type': 'window',
                'action_window_id': self._get_action_id('membership.action_membership_members', 'res.partner'),
            },
            {
                'name': 'Veranstaltungen',
                'description': 'Events und Termine verwalten',
                'icon': 'fa-calendar',
                'color': 'warning',
                'sequence': 10,
                'section_name': 'Events',
                'section_sequence': 20,
                'action_type': 'window',
                'action_window_id': self._get_action_id('event.action_event_view', 'event.event'),
            },
            {
                'name': 'Projekte',
                'description': 'Projekte und Aufgaben verwalten',
                'icon': 'fa-tasks',
                'color': 'info',
                'sequence': 10,
                'section_name': 'Projekte',
                'section_sequence': 30,
                'action_type': 'window',
                'action_window_id': self._get_action_id('project.open_view_project_all', 'project.project'),
            },
        ]
        
        # Add settings card for administrators
        if user.has_group('base.group_system'):
            default_cards.append({
                'name': 'Einstellungen',
                'description': 'Systemeinstellungen',
                'icon': 'fa-cog',
                'color': 'secondary',
                'sequence': 10,
                'section_name': 'Administration',
                'section_sequence': 40,
                'action_type': 'window',
                'action_window_id': self._get_action_id('base.action_res_users', 'res.users'),
            })
        
        # Create the cards
        for card_data in default_cards:
            card_data['user_id'] = user_id
            self.create(card_data)
            
        return True
    
    def _get_action_id(self, xml_id, fallback_model=None):
        """Get action ID by XML ID with fallback"""
        try:
            action = self.env.ref(xml_id, raise_if_not_found=False)
            if action and action._name == 'ir.actions.act_window':
                return action.id
        except:
            pass
            
        # Fallback: find action by model
        if fallback_model:
            action = self.env['ir.actions.act_window'].search([
                ('res_model', '=', fallback_model)
            ], limit=1)
            if action:
                return action.id
                
        return False