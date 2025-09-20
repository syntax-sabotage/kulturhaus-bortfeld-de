# -*- coding: utf-8 -*-
# Part of Smart Notification. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ApplyPreferencesWizard(models.TransientModel):
    """Wizard to apply smart notification preferences to existing subscriptions"""
    _name = 'smart.notification.apply.wizard'
    _description = 'Apply Smart Notification Preferences'
    
    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user,
        required=True,
        readonly=True
    )
    
    notification_profile = fields.Selection(
        related='user_id.notification_profile',
        readonly=True
    )
    
    subscription_count = fields.Integer(
        string='Existing Subscriptions',
        compute='_compute_subscription_count'
    )
    
    apply_to_models = fields.Selection([
        ('all', 'All Models'),
        ('selected', 'Selected Models Only'),
    ], string='Apply To', default='all', required=True)
    
    model_ids = fields.Many2many(
        'ir.model',
        string='Models',
        domain=[('is_mail_thread', '=', True)]
    )
    
    @api.depends('user_id')
    def _compute_subscription_count(self):
        for wizard in self:
            wizard.subscription_count = self.env['mail.followers'].search_count([
                ('partner_id', '=', wizard.user_id.partner_id.id)
            ])
    
    def action_apply(self):
        """Apply user's smart notification preferences to existing subscriptions"""
        self.ensure_one()
        
        if not self.user_id.smart_notifications_enabled:
            raise UserError(_('Smart Notifications must be enabled first.'))
        
        # Get all user's subscriptions
        domain = [('partner_id', '=', self.user_id.partner_id.id)]
        
        if self.apply_to_models == 'selected' and self.model_ids:
            model_names = self.model_ids.mapped('model')
            domain.append(('res_model', 'in', model_names))
        
        subscriptions = self.env['mail.followers'].search(domain)
        
        if not subscriptions:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No Subscriptions'),
                    'message': _('You have no existing subscriptions to update.'),
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        # Apply preferences to each subscription
        updated = 0
        for subscription in subscriptions:
            subtypes = self.user_id.get_notification_subtypes(subscription.res_model)
            if subtypes is not None:
                subscription.subtype_ids = [(6, 0, subtypes)]
                updated += 1
        
        # Update last applied timestamp
        self.user_id.notification_last_applied = fields.Datetime.now()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Preferences Applied'),
                'message': _('Updated %d subscriptions with your notification preferences.') % updated,
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_preview(self):
        """Preview what will be changed"""
        self.ensure_one()
        
        # This would open a view showing the changes that will be made
        # For now, just show the subscriptions
        return {
            'name': _('Your Subscriptions'),
            'type': 'ir.actions.act_window',
            'res_model': 'mail.followers',
            'view_mode': 'list',
            'domain': [('partner_id', '=', self.user_id.partner_id.id)],
            'context': {'create': False, 'edit': False},
        }