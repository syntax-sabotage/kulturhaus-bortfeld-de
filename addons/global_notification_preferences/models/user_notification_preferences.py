from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class UserNotificationPreference(models.Model):
    """Store user's global notification preferences per model and subtype"""
    _name = 'user.notification.preference'
    _description = 'User Global Notification Preferences'
    _rec_name = 'model_id'
    
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        ondelete='cascade',
        index=True,
    )
    
    model_id = fields.Many2one(
        'ir.model',
        string='Model',
        required=True,
        domain=[('is_mail_thread', '=', True)],
        help='Model for which these preferences apply',
    )
    
    model_name = fields.Char(
        related='model_id.model',
        store=True,
        index=True,
    )
    
    subtype_ids = fields.Many2many(
        'mail.message.subtype',
        'user_notification_preference_subtype_rel',
        'preference_id',
        'subtype_id',
        string='Notification Subtypes',
        help='Select which subtypes should trigger notifications for this model',
    )
    
    # Quick toggles for common scenarios
    notify_on_all = fields.Boolean(
        string='Notify on All',
        default=False,
        help='Receive notifications for all subtypes',
    )
    
    notify_on_messages = fields.Boolean(
        string='Messages',
        default=True,
        help='Receive notifications for new messages',
    )
    
    notify_on_notes = fields.Boolean(
        string='Notes',
        default=False,
        help='Receive notifications for internal notes',
    )
    
    notify_on_state_changes = fields.Boolean(
        string='State Changes',
        default=True,
        help='Receive notifications for state/stage changes',
    )
    
    notify_on_assignments = fields.Boolean(
        string='Assignments',
        default=True,
        help='Receive notifications when assigned',
    )
    
    _sql_constraints = [
        ('user_model_unique', 'UNIQUE (user_id, model_id)', 
         'Preferences for this model already exist for this user!')
    ]
    
    @api.onchange('notify_on_all')
    def _onchange_notify_on_all(self):
        """When notify_on_all is toggled, update other fields"""
        if self.notify_on_all:
            self.notify_on_messages = True
            self.notify_on_notes = True
            self.notify_on_state_changes = True
            self.notify_on_assignments = True
    
    @api.onchange('notify_on_messages', 'notify_on_notes', 
                  'notify_on_state_changes', 'notify_on_assignments')
    def _onchange_specific_notifications(self):
        """Update subtype_ids based on toggle fields"""
        if not self.model_id:
            return
        
        subtypes_to_add = self.env['mail.message.subtype']
        
        # Map common subtype names to our toggle fields
        if self.notify_on_messages:
            subtypes_to_add |= self._get_subtypes_by_keywords(['message', 'comment'])
        
        if self.notify_on_notes:
            subtypes_to_add |= self._get_subtypes_by_keywords(['note'])
        
        if self.notify_on_state_changes:
            subtypes_to_add |= self._get_subtypes_by_keywords(['stage', 'state'])
        
        if self.notify_on_assignments:
            subtypes_to_add |= self._get_subtypes_by_keywords(['assign'])
        
        self.subtype_ids = subtypes_to_add
    
    def _get_subtypes_by_keywords(self, keywords):
        """Find subtypes that match given keywords"""
        if not self.model_id:
            return self.env['mail.message.subtype']
        
        domain = [
            ('res_model', '=', self.model_id.model),
            '|', ('res_model', '=', False),
            ('res_model', '=', self.model_id.model)
        ]
        
        keyword_domain = []
        for keyword in keywords:
            keyword_domain.append(('name', 'ilike', keyword))
            if len(keyword_domain) > 1:
                keyword_domain.insert(0, '|')
        
        if keyword_domain:
            domain.extend(['&'] + keyword_domain)
        
        return self.env['mail.message.subtype'].search(domain)
    
    @api.model
    def get_user_subtypes_for_model(self, user_id, model_name):
        """Get the subtypes a user wants to be notified about for a model"""
        preference = self.search([
            ('user_id', '=', user_id),
            ('model_name', '=', model_name)
        ], limit=1)
        
        if preference:
            return preference.subtype_ids
        
        # Return default subtypes if no preference exists
        return self._get_default_subtypes_for_model(model_name)
    
    def _get_default_subtypes_for_model(self, model_name):
        """Get default subtypes for a model when no preference exists"""
        # Default: all subtypes except internal notes
        subtypes = self.env['mail.message.subtype'].search([
            '|',
            ('res_model', '=', model_name),
            ('res_model', '=', False),
            ('internal', '=', False),  # Exclude internal notes by default
        ])
        return subtypes
    
    @api.model
    def apply_global_preferences(self, follower):
        """Apply global preferences to a mail.followers record"""
        if not follower.partner_id or not follower.partner_id.user_ids:
            return
        
        user = follower.partner_id.user_ids[0]
        subtypes = self.get_user_subtypes_for_model(
            user.id, 
            follower.res_model
        )
        
        if subtypes:
            follower.subtype_ids = subtypes