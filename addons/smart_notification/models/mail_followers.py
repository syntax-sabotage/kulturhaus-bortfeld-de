# -*- coding: utf-8 -*-
# Part of Smart Notification. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class MailFollowers(models.Model):
    """Extend mail.followers to track smart notification usage"""
    _inherit = 'mail.followers'
    
    uses_smart_defaults = fields.Boolean(
        string='Uses Smart Defaults',
        compute='_compute_uses_smart_defaults',
        help="This subscription uses the user's smart notification preferences"
    )
    
    can_override = fields.Boolean(
        string='Can Override',
        default=True,
        help="User can override global preferences for this specific record"
    )
    
    @api.depends('partner_id')
    def _compute_uses_smart_defaults(self):
        for follower in self:
            user = self.env['res.users'].search([
                ('partner_id', '=', follower.partner_id.id),
                ('smart_notifications_enabled', '=', True)
            ], limit=1)
            follower.uses_smart_defaults = bool(user)
    
    def action_apply_smart_defaults(self):
        """Apply user's smart defaults to this follower record"""
        for follower in self:
            user = self.env['res.users'].search([
                ('partner_id', '=', follower.partner_id.id),
                ('smart_notifications_enabled', '=', True)
            ], limit=1)
            
            if user:
                # Get user's preferred subtypes for this model
                subtypes = user.get_notification_subtypes(follower.res_model)
                if subtypes:
                    follower.subtype_ids = [(6, 0, subtypes)]
                    
                    # Show success notification
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': _('Smart Defaults Applied'),
                            'message': _('Notification preferences have been updated.'),
                            'type': 'success',
                            'sticky': False,
                        }
                    }
        
        return True
    
    def action_override_preferences(self):
        """Open a wizard to override preferences for this specific follower"""
        self.ensure_one()
        
        # This would open a wizard to customize notifications for this specific record
        # Implementation would depend on specific requirements
        
        return {
            'name': _('Override Notification Preferences'),
            'type': 'ir.actions.act_window',
            'res_model': 'mail.wizard.follower.override',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_follower_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_res_model': self.res_model,
                'default_res_id': self.res_id,
            }
        }
    
    @api.model_create_multi
    def create(self, vals_list):
        """Track when smart defaults are applied during creation"""
        followers = super().create(vals_list)
        
        # Log smart notification applications
        for follower in followers:
            if follower.uses_smart_defaults:
                self._log_smart_notification_usage(follower)
        
        return followers
    
    def _log_smart_notification_usage(self, follower):
        """Log usage of smart notifications for analytics"""
        # This could be extended to track usage patterns
        # For now, just log it
        _logger = logging.getLogger(__name__)
        _logger.info(
            "Smart notification applied for %s on %s:%s",
            follower.partner_id.name,
            follower.res_model,
            follower.res_id
        )


import logging