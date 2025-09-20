# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api, _
from odoo.tools import html2plaintext
import logging

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = 'project.task'
    
    # Track board members (Vorstand) separately for easy access
    board_member_ids = fields.Many2many(
        'res.partner',
        'project_task_board_members_rel',
        'task_id',
        'partner_id',
        string='Board Members',
        compute='_compute_board_members',
        store=True,
        help='Partners who are board members and followers of this task'
    )
    
    @api.depends('message_follower_ids.partner_id')
    def _compute_board_members(self):
        """Compute board members from followers who have 'Vorstand' tag or group"""
        for task in self:
            # Find board members - customize this logic based on your setup
            # Option 1: Check for a specific user group
            board_group = self.env.ref('base.group_system', raise_if_not_found=False)  # Replace with your board group
            if board_group:
                board_partners = task.message_follower_ids.mapped('partner_id').filtered(
                    lambda p: p.user_ids and any(board_group in u.groups_id for u in p.user_ids)
                )
            else:
                # Option 2: Check for partners with 'Vorstand' in their function/title
                board_partners = task.message_follower_ids.mapped('partner_id').filtered(
                    lambda p: p.function and 'vorstand' in p.function.lower()
                )
            
            task.board_member_ids = [(6, 0, board_partners.ids)]
    
    def _message_compute_author(self, author_id=None, email_from=None, raise_on_email=False):
        """Override to handle group mentions detection"""
        return super()._message_compute_author(author_id, email_from, raise_on_email)
    
    @api.model
    def _extract_group_mentions(self, body_html):
        """Extract @all and @Vorstand mentions from message body"""
        if not body_html:
            return {'has_all': False, 'has_vorstand': False}
        
        # Convert to plain text for easier parsing
        body_text = html2plaintext(body_html or '').lower()
        
        # Pattern to match @all or @vorstand (case insensitive)
        all_pattern = r'@all\b'
        vorstand_pattern = r'@vorstand\b'
        
        return {
            'has_all': bool(re.search(all_pattern, body_text)),
            'has_vorstand': bool(re.search(vorstand_pattern, body_text))
        }
    
    def message_post(self, **kwargs):
        """Override message_post to handle group mentions"""
        # Extract body from kwargs
        body = kwargs.get('body', '')
        
        # Check for group mentions
        mentions = self._extract_group_mentions(body)
        
        # Store original partner_ids
        original_partner_ids = kwargs.get('partner_ids', [])
        
        if mentions['has_all'] or mentions['has_vorstand']:
            # Get all followers
            all_follower_partners = self.message_follower_ids.mapped('partner_id')
            
            # Determine which partners to notify
            partners_to_notify = self.env['res.partner']
            
            if mentions['has_all']:
                # Notify all followers
                partners_to_notify |= all_follower_partners
                _logger.info(f"Task {self.id}: @all mention detected, notifying {len(all_follower_partners)} followers")
                
            if mentions['has_vorstand']:
                # Notify board members only
                board_partners = self.board_member_ids
                if not board_partners and all_follower_partners:
                    # Fallback: If no specific board members, try to find them
                    board_partners = all_follower_partners.filtered(
                        lambda p: p.function and 'vorstand' in p.function.lower()
                    )
                partners_to_notify |= board_partners
                _logger.info(f"Task {self.id}: @Vorstand mention detected, notifying {len(board_partners)} board members")
            
            # Add these partners to the notification list
            if partners_to_notify:
                # Convert existing partner_ids to list if needed
                if isinstance(original_partner_ids, list):
                    partner_ids_list = list(original_partner_ids)
                else:
                    partner_ids_list = []
                
                # Add new partners
                partner_ids_list.extend(partners_to_notify.ids)
                
                # Remove duplicates while preserving order
                seen = set()
                unique_partner_ids = []
                for pid in partner_ids_list:
                    if pid not in seen:
                        seen.add(pid)
                        unique_partner_ids.append(pid)
                
                kwargs['partner_ids'] = unique_partner_ids
                
                # Add visual indicator in the message
                if mentions['has_all']:
                    body = body.replace('@all', '<span class="o_mail_mention_all badge text-bg-info">@all</span>')
                if mentions['has_vorstand']:
                    body = body.replace('@Vorstand', '<span class="o_mail_mention_vorstand badge text-bg-warning">@Vorstand</span>')
                    body = body.replace('@vorstand', '<span class="o_mail_mention_vorstand badge text-bg-warning">@Vorstand</span>')
                
                kwargs['body'] = body
        
        # Call super with modified kwargs
        message = super().message_post(**kwargs)
        
        # Log the notification
        if mentions['has_all'] or mentions['has_vorstand']:
            notified_count = len(kwargs.get('partner_ids', []))
            _logger.info(f"Task {self.id}: Group mention notification sent to {notified_count} partners")
        
        return message
    
    def action_notify_all_followers(self):
        """Manual action to notify all followers"""
        if not self.message_follower_ids:
            return {'warning': {
                'title': _('No Followers'),
                'message': _('This task has no followers to notify.')
            }}
        
        partners = self.message_follower_ids.mapped('partner_id')
        
        self.message_post(
            body=_('<p>📢 <strong>Notification to all followers</strong></p>'),
            partner_ids=partners.ids,
            message_type='notification',
            subtype_xmlid='mail.mt_comment'
        )
        
        return {'type': 'ir.actions.client', 'tag': 'display_notification', 'params': {
            'message': _('All %d followers have been notified') % len(partners),
            'type': 'success',
            'sticky': False,
        }}
    
    def action_notify_board_members(self):
        """Manual action to notify board members"""
        if not self.board_member_ids:
            return {'warning': {
                'title': _('No Board Members'),
                'message': _('No board members found among the followers.')
            }}
        
        self.message_post(
            body=_('<p>👥 <strong>Notification to board members</strong></p>'),
            partner_ids=self.board_member_ids.ids,
            message_type='notification',
            subtype_xmlid='mail.mt_comment'
        )
        
        return {'type': 'ir.actions.client', 'tag': 'display_notification', 'params': {
            'message': _('%d board members have been notified') % len(self.board_member_ids),
            'type': 'success',
            'sticky': False,
        }}