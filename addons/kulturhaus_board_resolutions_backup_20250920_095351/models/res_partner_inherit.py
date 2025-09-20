# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    board_member = fields.Boolean(
        'Board Member',
        help='Check this box if this contact is a board member of the association.'
    )
    
    # Statistics
    resolutions_count = fields.Integer(
        'Resolutions Count',
        compute='_compute_resolutions_count',
        help='Number of resolutions this member participated in.'
    )
    
    resolutions_attended = fields.Integer(
        'Resolutions Attended',
        compute='_compute_resolutions_attended',
        help='Number of resolutions this member attended.'
    )
    
    def _compute_resolutions_count(self):
        for partner in self:
            if partner.board_member:
                partner.resolutions_count = self.env['board.resolution'].search_count([
                    ('state', 'in', ['voted', 'to_approve', 'approved', 'archived'])
                ])
            else:
                partner.resolutions_count = 0
    
    def _compute_resolutions_attended(self):
        for partner in self:
            if partner.board_member:
                partner.resolutions_attended = self.env['board.resolution'].search_count([
                    ('present_members', 'in', [partner.id]),
                    ('state', 'in', ['voted', 'to_approve', 'approved', 'archived'])
                ])
            else:
                partner.resolutions_attended = 0
    
    def action_view_resolutions(self):
        """View all resolutions where this board member was present"""
        action = self.env["ir.actions.actions"]._for_xml_id("kulturhaus_board_resolutions.action_board_resolution")
        if self.board_member:
            action['domain'] = [('present_members', 'in', [self.id])]
        else:
            action['domain'] = [('id', '=', False)]  # Show no records if not a board member
        return action