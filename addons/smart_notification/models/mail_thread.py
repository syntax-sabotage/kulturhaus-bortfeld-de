# -*- coding: utf-8 -*-
# Part of Smart Notification. See LICENSE file for full copyright and licensing details.

from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    """Override mail.thread to apply smart notification preferences"""
    _inherit = 'mail.thread'
    
    def message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None):
        """
        Override to apply user's smart notification preferences when subscribing.
        
        This is the magic that makes it all work - when someone follows a record,
        we automatically apply their personal notification preferences.
        """
        # If specific subtypes are already provided, respect them
        if subtype_ids is not None:
            return super().message_subscribe(
                partner_ids=partner_ids,
                channel_ids=channel_ids,
                subtype_ids=subtype_ids
            )
        
        # Apply smart defaults for each partner
        if partner_ids:
            # Process each partner individually to apply their preferences
            for partner_id in partner_ids:
                user = self.env['res.users'].search([
                    ('partner_id', '=', partner_id),
                    ('smart_notifications_enabled', '=', True)
                ], limit=1)
                
                if user:
                    # Get user's preferred subtypes for this model
                    user_subtypes = user.get_notification_subtypes(self._name)
                    
                    if user_subtypes is not None:
                        # Subscribe with user's preferences
                        super().message_subscribe(
                            partner_ids=[partner_id],
                            channel_ids=None,
                            subtype_ids=user_subtypes
                        )
                        
                        _logger.info(
                            "Applied smart notification preferences for user %s on %s record %s",
                            user.name, self._name, self.id
                        )
                    else:
                        # Fall back to default behavior
                        super().message_subscribe(
                            partner_ids=[partner_id],
                            channel_ids=None,
                            subtype_ids=None
                        )
                else:
                    # No user or smart notifications disabled - use default
                    super().message_subscribe(
                        partner_ids=[partner_id],
                        channel_ids=None,
                        subtype_ids=None
                    )
            
            # Handle channels if provided
            if channel_ids:
                super().message_subscribe(
                    partner_ids=None,
                    channel_ids=channel_ids,
                    subtype_ids=None
                )
            
            # Return success
            return True
        
        # No partners provided, use default behavior
        return super().message_subscribe(
            partner_ids=partner_ids,
            channel_ids=channel_ids,
            subtype_ids=subtype_ids
        )
    
    @api.model
    def message_subscribe_users(self, user_ids=None, subtype_ids=None):
        """
        Override to apply smart defaults when subscribing users.
        """
        if subtype_ids is not None:
            return super().message_subscribe_users(user_ids, subtype_ids)
        
        # Apply smart defaults
        if user_ids:
            users = self.env['res.users'].browse(user_ids)
            for user in users.filtered('smart_notifications_enabled'):
                user_subtypes = user.get_notification_subtypes(self._name)
                if user_subtypes is not None:
                    super().message_subscribe(
                        partner_ids=user.partner_id.ids,
                        subtype_ids=user_subtypes
                    )
                else:
                    super().message_subscribe_users(
                        user_ids=user.ids,
                        subtype_ids=None
                    )
            
            # Handle users without smart notifications
            regular_users = users.filtered(lambda u: not u.smart_notifications_enabled)
            if regular_users:
                super().message_subscribe_users(
                    user_ids=regular_users.ids,
                    subtype_ids=None
                )
            
            return True
        
        return super().message_subscribe_users(user_ids, subtype_ids)