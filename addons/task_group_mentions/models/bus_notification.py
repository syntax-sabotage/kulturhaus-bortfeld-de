# -*- coding: utf-8 -*-
"""
Advanced real-time notification system using Odoo's bus
"""
from odoo import models, fields, api, _
from odoo.addons.bus.models.bus import channel_with_db
import json


class BusNotification(models.Model):
    _inherit = 'bus.bus'
    
    @api.model
    def _sendmany(self, notifications):
        """Override to handle group notifications"""
        # Process notifications for group mentions
        for notification in notifications:
            if isinstance(notification, dict) and notification.get('type') == 'group_mention':
                self._process_group_mention(notification)
        
        return super()._sendmany(notifications)
    
    def _process_group_mention(self, notification):
        """Process group mention notifications"""
        task_id = notification.get('task_id')
        mention_type = notification.get('mention_type')  # 'all' or 'vorstand'
        
        if not task_id:
            return
        
        task = self.env['project.task'].browse(task_id)
        if not task.exists():
            return
        
        # Determine recipients
        if mention_type == 'all':
            partners = task.message_follower_ids.mapped('partner_id')
        elif mention_type == 'vorstand':
            partners = task.board_member_ids
        else:
            return
        
        # Send real-time notifications
        for partner in partners:
            if partner.user_ids:
                for user in partner.user_ids:
                    channel = (self._cr.dbname, 'res.partner', partner.id)
                    self._sendone(channel, 'mail.message/insert', {
                        'id': notification.get('message_id'),
                        'model': 'project.task',
                        'res_id': task_id,
                        'body': notification.get('body', ''),
                        'type': 'group_mention_notification',
                    })


class ProjectTaskBus(models.Model):
    _inherit = 'project.task'
    
    def _notify_group_mention_realtime(self, mention_type, message):
        """Send real-time notification for group mentions"""
        notification = {
            'type': 'group_mention',
            'task_id': self.id,
            'mention_type': mention_type,
            'message_id': message.id,
            'body': message.body,
        }
        
        # Trigger bus notification
        self.env['bus.bus']._sendmany([notification])
        
        return True