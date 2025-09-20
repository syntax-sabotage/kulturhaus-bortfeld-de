from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    global_notification_preference_ids = fields.One2many(
        'user.notification.preference',
        'user_id',
        string='Global Notification Preferences',
    )
    
    # Global master toggles
    global_notify_email = fields.Boolean(
        string='Email Notifications',
        default=True,
        help='Receive email notifications for followed records',
    )
    
    global_notify_inbox = fields.Boolean(
        string='Inbox Notifications',
        default=True,
        help='Receive notifications in Odoo inbox',
    )
    
    global_notify_push = fields.Boolean(
        string='Push Notifications',
        default=True,
        help='Receive push notifications (if configured)',
    )
    
    # Quick preference options
    notification_preference_mode = fields.Selection([
        ('default', 'Default (All notifications)'),
        ('important', 'Important only (Messages & Assignments)'),
        ('minimal', 'Minimal (Direct messages only)'),
        ('custom', 'Custom per model'),
    ], string='Notification Mode', default='default')
    
    def action_configure_notification_preferences(self):
        """Open a wizard to configure notification preferences"""
        self.ensure_one()
        return {
            'name': 'Configure Notification Preferences',
            'type': 'ir.actions.act_window',
            'res_model': 'user.notification.preference',
            'view_mode': 'list,form',
            'domain': [('user_id', '=', self.id)],
            'context': {
                'default_user_id': self.id,
            },
        }
    
    @api.model
    def create(self, vals):
        """When creating a user, set up default notification preferences"""
        user = super().create(vals)
        user._setup_default_notification_preferences()
        return user
    
    def _setup_default_notification_preferences(self):
        """Set up default notification preferences for common models"""
        self.ensure_one()
        
        # Skip setup for special users
        if self.id in [1, 2]:  # Admin and OdooBot
            return
        
        NotificationPref = self.env['user.notification.preference']
        
        # Default models to configure
        default_models = [
            'project.task',
            'project.project',
            'sale.order',
            'purchase.order',
            'account.move',
        ]
        
        for model_name in default_models:
            model = self.env['ir.model'].search([('model', '=', model_name)], limit=1)
            if not model:
                continue
            
            # Check if preference already exists
            existing = NotificationPref.search([
                ('user_id', '=', self.id),
                ('model_id', '=', model.id)
            ])
            
            if not existing:
                # Create default preferences based on notification_preference_mode
                NotificationPref.create({
                    'user_id': self.id,
                    'model_id': model.id,
                    'notify_on_messages': True,
                    'notify_on_notes': self.notification_preference_mode == 'default',
                    'notify_on_state_changes': self.notification_preference_mode in ['default', 'important'],
                    'notify_on_assignments': True,
                })
    
    @api.onchange('notification_preference_mode')
    def _onchange_notification_preference_mode(self):
        """Update all notification preferences based on selected mode"""
        if self.notification_preference_mode == 'custom':
            return  # Don't change anything in custom mode
        
        for pref in self.global_notification_preference_ids:
            if self.notification_preference_mode == 'default':
                pref.notify_on_all = True
            elif self.notification_preference_mode == 'important':
                pref.notify_on_messages = True
                pref.notify_on_notes = False
                pref.notify_on_state_changes = True
                pref.notify_on_assignments = True
            elif self.notification_preference_mode == 'minimal':
                pref.notify_on_messages = True
                pref.notify_on_notes = False
                pref.notify_on_state_changes = False
                pref.notify_on_assignments = True
    
    def get_notification_subtypes_for_model(self, model_name):
        """Get the notification subtypes this user wants for a specific model"""
        self.ensure_one()
        
        # Check if master toggles are off
        if not self.global_notify_email and not self.global_notify_inbox:
            return self.env['mail.message.subtype']
        
        # Get user's preference for this model
        preference = self.global_notification_preference_ids.filtered(
            lambda p: p.model_name == model_name
        )
        
        if preference:
            return preference[0].subtype_ids
        
        # Return default subtypes based on notification mode
        return self._get_default_subtypes_by_mode(model_name)
    
    def _get_default_subtypes_by_mode(self, model_name):
        """Get default subtypes based on user's notification mode"""
        all_subtypes = self.env['mail.message.subtype'].search([
            '|',
            ('res_model', '=', model_name),
            ('res_model', '=', False),
        ])
        
        if self.notification_preference_mode == 'default':
            return all_subtypes
        
        elif self.notification_preference_mode == 'important':
            # Filter for important subtypes (messages, assignments, state changes)
            important_keywords = ['message', 'comment', 'assign', 'stage', 'state']
            domain = ['|'] * (len(important_keywords) - 1)
            for keyword in important_keywords:
                domain.append(('name', 'ilike', keyword))
            
            return all_subtypes.filtered_domain(domain)
        
        elif self.notification_preference_mode == 'minimal':
            # Only direct messages
            return all_subtypes.filtered(
                lambda s: 'message' in s.name.lower() or 'comment' in s.name.lower()
            )
        
        return all_subtypes