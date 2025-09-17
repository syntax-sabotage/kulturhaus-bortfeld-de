# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    # Basic dashboard toggle
    use_dashboard = fields.Boolean(
        string='Use Dashboard Home',
        default=False,
        help='Replace standard Odoo home with Kulturhaus Dashboard'
    )
    
    # Dashboard configuration fields
    dashboard_card_ids = fields.One2many(
        'dashboard.card.config', 'user_id', 
        string='Dashboard Cards'
    )
    
    dashboard_theme = fields.Selection([
        ('blue', 'Blue Theme'),
        ('green', 'Green Theme'),
        ('purple', 'Purple Theme'),
        ('orange', 'Orange Theme'),
        ('dark', 'Dark Theme'),
    ], string='Dashboard Theme', default='blue')
    
    dashboard_layout = fields.Selection([
        ('grid', 'Grid Layout'),
        ('list', 'List Layout'),
        ('compact', 'Compact Layout'),
    ], string='Dashboard Layout', default='grid')
    
    show_kpis = fields.Boolean(
        string='Show KPI Widgets',
        default=True,
        help='Show/hide KPI widgets on the dashboard'
    )
    
    @api.model
    def get_home_action(self):
        """Override home action to show dashboard if enabled"""
        if self.use_dashboard:
            return {
                'type': 'ir.actions.client',
                'tag': 'kulturhaus_dashboard',
                'name': 'Kulturhaus Dashboard',
                'target': 'main',
            }
        return super().get_home_action()
    
    def setup_default_cards(self):
        """Setup default dashboard cards for this user"""
        self.ensure_one()
        card_model = self.env['dashboard.card.config']
        return card_model.create_default_cards_for_user(self.id)
    
    def reset_dashboard_config(self):
        """Reset dashboard configuration to defaults"""
        self.ensure_one()
        # Remove all existing cards
        self.dashboard_card_ids.unlink()
        # Reset preferences
        self.write({
            'dashboard_theme': 'blue',
            'dashboard_layout': 'grid',
            'show_kpis': True,
        })
        # Setup default cards
        return self.setup_default_cards()
    
    def duplicate_cards_from_admin(self):
        """Copy card configuration from admin user"""
        self.ensure_one()
        admin_user = self.env['res.users'].search([
            ('login', '=', 'admin')
        ], limit=1)
        
        if not admin_user or not admin_user.dashboard_card_ids:
            return False
            
        # Remove existing cards
        self.dashboard_card_ids.unlink()
        
        # Copy cards from admin
        for card in admin_user.dashboard_card_ids:
            card.copy({'user_id': self.id})
            
        return True
    
    def export_dashboard_config(self):
        """Export dashboard configuration for backup"""
        self.ensure_one()
        config_data = {
            'user_login': self.login,
            'dashboard_theme': self.dashboard_theme,
            'dashboard_layout': self.dashboard_layout,
            'show_kpis': self.show_kpis,
            'cards': []
        }
        
        for card in self.dashboard_card_ids:
            card_data = {
                'name': card.name,
                'description': card.description,
                'sequence': card.sequence,
                'icon': card.icon,
                'color': card.color,
                'action_type': card.action_type,
                'is_active': card.is_active,
            }
            
            if card.action_type == 'window' and card.action_window_id:
                card_data['action_xml_id'] = card.action_window_id.xml_id or ''
            elif card.action_type == 'url':
                card_data['action_url'] = card.action_url
            elif card.action_type == 'custom':
                card_data['custom_action_code'] = card.custom_action_code
                
            config_data['cards'].append(card_data)
        
        return config_data