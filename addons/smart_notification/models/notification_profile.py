# -*- coding: utf-8 -*-
# Part of Smart Notification. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class NotificationProfile(models.Model):
    """Pre-configured notification preference templates"""
    _name = 'notification.profile'
    _description = 'Notification Profile Template'
    _order = 'sequence, name'

    name = fields.Char(
        string='Profile Name',
        required=True,
        translate=True,
        help="Descriptive name for this notification profile"
    )
    
    code = fields.Char(
        string='Code',
        required=True,
        help="Internal code for this profile"
    )
    
    description = fields.Text(
        string='Description',
        translate=True,
        help="Detailed description of when to use this profile"
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help="Order in which profiles appear"
    )
    
    active = fields.Boolean(
        string='Active',
        default=True
    )
    
    # Quick settings
    notify_on_all = fields.Boolean(
        string='All Notifications',
        help="Receive all possible notifications"
    )
    
    # Granular settings per notification type
    setting_ids = fields.One2many(
        'notification.profile.setting',
        'profile_id',
        string='Notification Settings'
    )
    
    # Usage tracking
    user_count = fields.Integer(
        string='Users',
        compute='_compute_user_count',
        help="Number of users using this profile"
    )
    
    @api.depends('code')
    def _compute_user_count(self):
        for profile in self:
            profile.user_count = self.env['res.users'].search_count([
                ('notification_profile', '=', profile.code)
            ])
    
    def action_view_users(self):
        """View users using this profile"""
        self.ensure_one()
        return {
            'name': _('Users: %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'res.users',
            'view_mode': 'list,form',
            'domain': [('notification_profile', '=', self.code)],
            'context': {'default_notification_profile': self.code},
        }
    
    @api.model
    def get_profile_settings(self, profile_code, model_name):
        """Get notification settings for a profile and model"""
        profile = self.search([('code', '=', profile_code)], limit=1)
        if not profile:
            return {}
        
        # Check for all notifications override
        if profile.notify_on_all:
            return {'all': True}
        
        # Get model-specific settings
        settings = profile.setting_ids.filtered(
            lambda s: s.model_id.model == model_name
        )
        
        if not settings:
            # Return default settings if no specific configuration
            return self._get_default_settings(model_name)
        
        result = {}
        for setting in settings:
            result[setting.subtype_id.res_model + '.' + setting.subtype_id.name] = setting.enabled
        
        return result
    
    def _get_default_settings(self, model_name):
        """Get default settings for a model when no specific configuration exists"""
        # Conservative defaults - only important notifications
        defaults = {
            'project.task': {
                'mail.mt_comment': True,  # Messages
                'mail.mt_note': False,     # Internal notes
                'project.mt_task_assigned': True,  # Assignment
                'project.mt_task_stage': True,     # Stage change
            },
            'sale.order': {
                'mail.mt_comment': True,
                'mail.mt_note': False,
                'sale.mt_order_confirmed': True,
                'sale.mt_order_sent': True,
            },
            'account.move': {
                'mail.mt_comment': True,
                'mail.mt_note': False,
                'account.mt_invoice_validated': True,
                'account.mt_invoice_paid': True,
            },
        }
        return defaults.get(model_name, {'mail.mt_comment': True, 'mail.mt_note': False})


class NotificationProfileSetting(models.Model):
    """Granular notification settings per model and subtype"""
    _name = 'notification.profile.setting'
    _description = 'Notification Profile Setting'
    _rec_name = 'subtype_id'

    profile_id = fields.Many2one(
        'notification.profile',
        string='Profile',
        required=True,
        ondelete='cascade'
    )
    
    model_id = fields.Many2one(
        'ir.model',
        string='Model',
        required=True,
        domain=[('is_mail_thread', '=', True)],
        help="Model for which this setting applies"
    )
    
    subtype_id = fields.Many2one(
        'mail.message.subtype',
        string='Notification Type',
        required=True,
        help="Type of notification"
    )
    
    enabled = fields.Boolean(
        string='Enabled',
        default=True,
        help="Whether to receive this type of notification"
    )
    
    @api.onchange('model_id')
    def _onchange_model_id(self):
        """Filter subtypes based on selected model"""
        if self.model_id:
            return {
                'domain': {
                    'subtype_id': [
                        '|',
                        ('res_model', '=', False),
                        ('res_model', '=', self.model_id.model)
                    ]
                }
            }
        return {'domain': {'subtype_id': []}}