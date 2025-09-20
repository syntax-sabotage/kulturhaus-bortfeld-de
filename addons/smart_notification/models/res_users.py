# -*- coding: utf-8 -*-
# Part of Smart Notification. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    """Extend users with smart notification preferences"""
    _inherit = 'res.users'

    # Main profile selection
    notification_profile = fields.Selection([
        ('minimal', 'Minimal'),
        ('normal', 'Normal'),
        ('manager', 'Manager'),
        ('board', 'Board Member'),
        ('custom', 'Custom'),
    ], string='Notification Profile',
        default='normal',
        help="Quick profile for notification preferences"
    )
    
    notification_profile_id = fields.Many2one(
        'notification.profile',
        string='Advanced Profile',
        help="Use a pre-configured notification profile template"
    )
    
    # Global toggle
    smart_notifications_enabled = fields.Boolean(
        string='Use Smart Notifications',
        default=True,
        help="Apply your notification preferences automatically when following records"
    )
    
    # Quick access preferences for common models
    # Project Task
    notify_task_notes = fields.Boolean(
        string='Task Internal Notes',
        help="Get notified on internal notes in tasks you follow"
    )
    notify_task_messages = fields.Boolean(
        string='Task Messages',
        default=True,
        help="Get notified on messages in tasks you follow"
    )
    notify_task_state = fields.Boolean(
        string='Task State Changes',
        default=True,
        help="Get notified when task state changes"
    )
    notify_task_assignment = fields.Boolean(
        string='Task Assignments',
        default=True,
        help="Get notified when tasks are assigned"
    )
    
    # Sale Order
    notify_sale_notes = fields.Boolean(
        string='Sale Internal Notes',
        help="Get notified on internal notes in sales orders you follow"
    )
    notify_sale_messages = fields.Boolean(
        string='Sale Messages',
        default=True,
        help="Get notified on messages in sales orders you follow"
    )
    notify_sale_confirmation = fields.Boolean(
        string='Sale Confirmations',
        default=True,
        help="Get notified when sales orders are confirmed"
    )
    
    # Account Move
    notify_invoice_notes = fields.Boolean(
        string='Invoice Internal Notes',
        help="Get notified on internal notes in invoices you follow"
    )
    notify_invoice_messages = fields.Boolean(
        string='Invoice Messages',
        default=True,
        help="Get notified on messages in invoices you follow"
    )
    notify_invoice_validation = fields.Boolean(
        string='Invoice Validations',
        default=True,
        help="Get notified when invoices are validated"
    )
    
    # Statistics
    notification_subscriptions_count = fields.Integer(
        string='Active Subscriptions',
        compute='_compute_notification_stats',
        help="Number of records you're following"
    )
    notification_last_applied = fields.Datetime(
        string='Preferences Last Applied',
        help="When your preferences were last applied to followers"
    )
    
    @api.depends('partner_id')
    def _compute_notification_stats(self):
        for user in self:
            user.notification_subscriptions_count = self.env['mail.followers'].search_count([
                ('partner_id', '=', user.partner_id.id)
            ])
    
    @api.onchange('notification_profile')
    def _onchange_notification_profile(self):
        """Apply profile presets"""
        if self.notification_profile == 'minimal':
            self.notify_task_notes = False
            self.notify_task_messages = False
            self.notify_task_state = True
            self.notify_task_assignment = True
            self.notify_sale_notes = False
            self.notify_sale_messages = False
            self.notify_sale_confirmation = True
            self.notify_invoice_notes = False
            self.notify_invoice_messages = False
            self.notify_invoice_validation = True
            
        elif self.notification_profile == 'normal':
            self.notify_task_notes = False
            self.notify_task_messages = True
            self.notify_task_state = True
            self.notify_task_assignment = True
            self.notify_sale_notes = False
            self.notify_sale_messages = True
            self.notify_sale_confirmation = True
            self.notify_invoice_notes = False
            self.notify_invoice_messages = True
            self.notify_invoice_validation = True
            
        elif self.notification_profile == 'manager':
            self.notify_task_notes = False
            self.notify_task_messages = True
            self.notify_task_state = True
            self.notify_task_assignment = True
            self.notify_sale_notes = False
            self.notify_sale_messages = True
            self.notify_sale_confirmation = True
            self.notify_invoice_notes = False
            self.notify_invoice_messages = True
            self.notify_invoice_validation = True
            
        elif self.notification_profile == 'board':
            # Board members want EVERYTHING
            self.notify_task_notes = True
            self.notify_task_messages = True
            self.notify_task_state = True
            self.notify_task_assignment = True
            self.notify_sale_notes = True
            self.notify_sale_messages = True
            self.notify_sale_confirmation = True
            self.notify_invoice_notes = True
            self.notify_invoice_messages = True
            self.notify_invoice_validation = True
    
    @api.onchange('notification_profile_id')
    def _onchange_notification_profile_id(self):
        """Apply advanced profile template"""
        if self.notification_profile_id:
            self.notification_profile = 'custom'
            # Apply settings from the profile template
            # This would need more detailed implementation based on profile structure
    
    def get_notification_subtypes(self, model_name):
        """Get user's preferred subtypes for a model"""
        self.ensure_one()
        
        if not self.smart_notifications_enabled:
            return None  # Use Odoo defaults
        
        subtypes = self.env['mail.message.subtype']
        
        # Map user preferences to actual subtypes
        if model_name == 'project.task':
            if self.notify_task_notes:
                subtypes |= self.env.ref('mail.mt_note', raise_if_not_found=False)
            if self.notify_task_messages:
                subtypes |= self.env.ref('mail.mt_comment', raise_if_not_found=False)
            if self.notify_task_state:
                subtypes |= self.env.ref('project.mt_task_stage', raise_if_not_found=False)
            if self.notify_task_assignment:
                subtypes |= self.env.ref('project.mt_task_assigned', raise_if_not_found=False)
                
        elif model_name == 'sale.order':
            if self.notify_sale_notes:
                subtypes |= self.env.ref('mail.mt_note', raise_if_not_found=False)
            if self.notify_sale_messages:
                subtypes |= self.env.ref('mail.mt_comment', raise_if_not_found=False)
            if self.notify_sale_confirmation:
                subtypes |= self.env.ref('sale.mt_order_confirmed', raise_if_not_found=False)
                
        elif model_name == 'account.move':
            if self.notify_invoice_notes:
                subtypes |= self.env.ref('mail.mt_note', raise_if_not_found=False)
            if self.notify_invoice_messages:
                subtypes |= self.env.ref('mail.mt_comment', raise_if_not_found=False)
            if self.notify_invoice_validation:
                subtypes |= self.env.ref('account.mt_invoice_validated', raise_if_not_found=False)
        
        else:
            # For other models, use conservative defaults
            subtypes |= self.env.ref('mail.mt_comment', raise_if_not_found=False)
            if self.notification_profile == 'board':
                subtypes |= self.env.ref('mail.mt_note', raise_if_not_found=False)
        
        return subtypes.ids if subtypes else None
    
    def action_apply_preferences(self):
        """Apply current preferences to all existing followers"""
        self.ensure_one()
        
        # Open wizard to confirm and apply
        return {
            'name': _('Apply Notification Preferences'),
            'type': 'ir.actions.act_window',
            'res_model': 'smart.notification.apply.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_user_id': self.id}
        }
    
    def action_view_subscriptions(self):
        """View all current subscriptions"""
        self.ensure_one()
        return {
            'name': _('My Subscriptions'),
            'type': 'ir.actions.act_window',
            'res_model': 'mail.followers',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.partner_id.id)],
            'context': {'create': False}
        }
    
    @api.model
    def create(self, vals):
        """Set smart defaults for new users"""
        if 'notification_profile' not in vals:
            # Check if user is in a specific group to set defaults
            if vals.get('groups_id'):
                # Parse groups_id commands to check for board member group
                # This is simplified - would need proper command parsing
                vals['notification_profile'] = 'normal'
        return super().create(vals)
    
    def write(self, vals):
        """Track when preferences change"""
        if any(field in vals for field in [
            'notification_profile', 'notify_task_notes', 'notify_task_messages',
            'notify_task_state', 'notify_task_assignment', 'notify_sale_notes',
            'notify_sale_messages', 'notify_sale_confirmation', 'notify_invoice_notes',
            'notify_invoice_messages', 'notify_invoice_validation'
        ]):
            vals['notification_last_applied'] = False  # Mark as needing reapplication
        return super().write(vals)