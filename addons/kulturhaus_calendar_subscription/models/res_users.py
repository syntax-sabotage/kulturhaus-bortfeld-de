# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    calendar_subscription_ids = fields.One2many(
        'calendar.subscription.token',
        'user_id',
        string='Calendar Subscriptions',
        help='Active calendar subscription tokens for this user'
    )
    calendar_subscription_count = fields.Integer(
        string='Subscription Count',
        compute='_compute_calendar_subscription_count'
    )
    
    @api.depends('calendar_subscription_ids')
    def _compute_calendar_subscription_count(self):
        for user in self:
            user.calendar_subscription_count = len(user.calendar_subscription_ids.filtered('active'))
    
    def action_view_calendar_subscriptions(self):
        """Open calendar subscriptions for this user"""
        self.ensure_one()
        return {
            'name': 'My Calendar Subscriptions',
            'type': 'ir.actions.act_window',
            'res_model': 'calendar.subscription.token',
            'view_mode': 'list,form',
            'domain': [('user_id', '=', self.id)],
            'context': {
                'default_user_id': self.id,
                'create': True,
            }
        }
    
    def action_create_calendar_subscription(self):
        """Quick action to create a new calendar subscription"""
        self.ensure_one()
        return {
            'name': 'New Calendar Subscription',
            'type': 'ir.actions.act_window',
            'res_model': 'calendar.subscription.token',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_user_id': self.id,
                'default_name': f'Calendar Feed - {fields.Date.today()}',
            }
        }