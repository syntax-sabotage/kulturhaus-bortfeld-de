from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class MailFollowers(models.Model):
    _inherit = 'mail.followers'
    
    use_global_preferences = fields.Boolean(
        string='Use Global Preferences',
        default=True,
        help='Use user\'s global notification preferences instead of per-record settings',
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        """Apply global preferences when creating new followers"""
        followers = super().create(vals_list)
        
        for follower in followers:
            if follower.use_global_preferences:
                follower._apply_global_preferences()
        
        return followers
    
    def _apply_global_preferences(self):
        """Apply user's global notification preferences to this follower"""
        self.ensure_one()
        
        # Only apply for user partners (not external partners)
        if not self.partner_id or not self.partner_id.user_ids:
            return
        
        user = self.partner_id.user_ids[0]
        
        # Get user's preferences for this model
        subtypes = user.get_notification_subtypes_for_model(self.res_model)
        
        if subtypes:
            self.subtype_ids = subtypes
            _logger.info(f"Applied global preferences for user {user.name} on {self.res_model}")
    
    def action_apply_global_preferences(self):
        """Manual action to apply global preferences"""
        for follower in self:
            if follower.partner_id and follower.partner_id.user_ids:
                follower._apply_global_preferences()
        
        return True
    
    def action_override_preferences(self):
        """Action to override global preferences for this specific record"""
        self.ensure_one()
        self.use_global_preferences = False
        
        return {
            'name': 'Configure Notifications',
            'type': 'ir.actions.act_window',
            'res_model': 'mail.followers',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'form_view_ref': 'mail.mail_followers_view_form',
            },
        }
    
    @api.model
    def _add_followers(self, res_model, res_ids, partner_ids, channel_ids=None,
                       check_existing=True, existing_policy='skip'):
        """Override to apply global preferences to new followers"""
        result = super()._add_followers(
            res_model, res_ids, partner_ids, 
            channel_ids=channel_ids,
            check_existing=check_existing,
            existing_policy=existing_policy
        )
        
        # Apply global preferences to newly created followers
        new_followers = self.search([
            ('res_model', '=', res_model),
            ('res_id', 'in', res_ids),
            ('partner_id', 'in', partner_ids),
        ])
        
        for follower in new_followers:
            if follower.use_global_preferences:
                follower._apply_global_preferences()
        
        return result
    
    def _get_subscription_data(self, res_model, res_ids, partner_ids):
        """Override to inject global preferences into subscription data"""
        data = super()._get_subscription_data(res_model, res_ids, partner_ids)
        
        # Enhance with global preferences
        for res_id in res_ids:
            for partner_id in partner_ids:
                partner = self.env['res.partner'].browse(partner_id)
                if partner.user_ids:
                    user = partner.user_ids[0]
                    subtypes = user.get_notification_subtypes_for_model(res_model)
                    if subtypes:
                        key = (res_id, partner_id)
                        if key in data:
                            data[key]['subtype_ids'] = subtypes.ids
        
        return data


class MailThread(models.AbstractModel):
    """Extend mail.thread to support global notification preferences"""
    _inherit = 'mail.thread'
    
    def message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None):
        """Override to apply global preferences when subscribing"""
        # If no specific subtypes provided, use global preferences
        if not subtype_ids and partner_ids:
            partners = self.env['res.partner'].browse(partner_ids)
            for partner in partners.filtered('user_ids'):
                user = partner.user_ids[0]
                global_subtypes = user.get_notification_subtypes_for_model(self._name)
                if global_subtypes and not subtype_ids:
                    subtype_ids = global_subtypes.ids
        
        return super().message_subscribe(
            partner_ids=partner_ids,
            channel_ids=channel_ids,
            subtype_ids=subtype_ids
        )
    
    def message_partner_info_from_emails(self, emails, link_mail=False):
        """Override to apply global preferences for new email subscribers"""
        result = super().message_partner_info_from_emails(emails, link_mail=link_mail)
        
        # Apply global preferences for any newly created partners
        for partner_info in result:
            if partner_info.get('partner_id'):
                partner = self.env['res.partner'].browse(partner_info['partner_id'])
                if partner.user_ids:
                    user = partner.user_ids[0]
                    subtypes = user.get_notification_subtypes_for_model(self._name)
                    if subtypes:
                        # Update the follower with global preferences
                        follower = self.env['mail.followers'].search([
                            ('res_model', '=', self._name),
                            ('res_id', '=', self.id),
                            ('partner_id', '=', partner.id),
                        ], limit=1)
                        if follower:
                            follower.subtype_ids = subtypes
        
        return result