# -*- coding: utf-8 -*-
from odoo import models, fields, api

class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'
    _order = 'kh_menu_sequence, sequence, id'
    
    kh_menu_sequence = fields.Integer(
        string='Menu Order',
        default=10,
        help='Drag to reorder (lower numbers appear first)'
    )
    
    kh_show_separator = fields.Boolean(
        string='Show Separator After',
        default=False,
        help='Mark to show a separator after this menu (requires theme support)'
    )
    
    kh_menu_category = fields.Selection([
        ('core', 'Core Business'),
        ('operations', 'Operations'),
        ('communication', 'Communication'),
        ('management', 'Management'),
        ('tools', 'Tools & Settings'),
        ('other', 'Other'),
    ], string='Menu Category', default='other', required=True)
    
    kh_is_hidden = fields.Boolean(
        string='Hide Menu',
        default=False,
        help='Hide this menu item temporarily'
    )
    
    @api.model
    def create(self, vals):
        """Set sequence from kh_menu_sequence on create"""
        if 'kh_menu_sequence' in vals and 'sequence' not in vals:
            vals['sequence'] = vals['kh_menu_sequence']
        return super().create(vals)
    
    def write(self, vals):
        """Sync sequence when kh_menu_sequence changes"""
        if 'kh_menu_sequence' in vals:
            vals['sequence'] = vals['kh_menu_sequence']
        
        result = super().write(vals)
        
        # Clear menu cache when order changes
        if any(field in vals for field in ['kh_menu_sequence', 'sequence', 'kh_is_hidden']):
            # In Odoo 18, we need to clear the cache differently
            self.env.registry.clear_cache()
            
        return result
    
    def action_toggle_separator(self):
        """Toggle separator display"""
        self.ensure_one()
        self.kh_show_separator = not self.kh_show_separator
        return True
    
    def action_toggle_visibility(self):
        """Toggle menu visibility"""
        self.ensure_one()
        self.kh_is_hidden = not self.kh_is_hidden
        self.active = not self.kh_is_hidden
        return True
