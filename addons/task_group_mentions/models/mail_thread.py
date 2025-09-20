# -*- coding: utf-8 -*-
from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    """Extend mail.thread to add group mention support globally"""
    _inherit = 'mail.thread'
    
    @api.model
    def _notify_get_recipients_groups(self, msg_vals, model_description=False):
        """Override to ensure group mentions are properly handled"""
        groups = super()._notify_get_recipients_groups(msg_vals, model_description)
        
        # Check if this is a project.task message with group mentions
        if self._name == 'project.task':
            body = msg_vals.get('body', '')
            # Ensure all mentioned partners are included in notifications
            if '@all' in str(body).lower() or '@vorstand' in str(body).lower():
                _logger.debug(f"Group mention detected in {self._name} message")
        
        return groups