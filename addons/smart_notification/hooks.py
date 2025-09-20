# -*- coding: utf-8 -*-
# Part of Smart Notification. See LICENSE file for full copyright and licensing details.

from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """
    Post-installation hook to set up initial data and configurations.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Set default profile for users who haven't configured one
    users = env['res.users'].search([
        ('share', '=', False),  # Internal users only
        ('notification_profile', '=', False)
    ])
    
    if users:
        default_profile = env.ref('smart_notification.profile_normal', raise_if_not_found=False)
        if default_profile:
            users.write({'notification_profile': 'normal'})
            _logger.info("Set default notification profile for %d users", len(users))
    
    # Log successful installation
    _logger.info("Smart Notification module installed successfully")
    
    # Display installation message
    return {
        'type': 'ir.actions.client',
        'tag': 'display_notification',
        'params': {
            'title': 'Smart Notification Installed',
            'message': 'Configure your notification preferences in Settings > Users > Smart Notifications',
            'type': 'success',
            'sticky': True,
        }
    }


def uninstall_hook(cr, registry):
    """
    Uninstall hook to clean up module data.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Reset user preferences to defaults
    users = env['res.users'].search([('smart_notifications_enabled', '=', True)])
    if users:
        users.write({
            'smart_notifications_enabled': False,
            'notification_profile': False,
        })
        _logger.info("Reset notification preferences for %d users", len(users))
    
    _logger.info("Smart Notification module uninstalled")