# -*- coding: utf-8 -*-

from odoo import models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def create(self, vals):
        result = super(ResCompany, self).create(vals)
        sequence_id = self.env['ir.sequence'].search(
            [('name', '=', 'Equipment Company Sequence'), ('company_id', '=', result.id)])
        if not sequence_id:
            self.env['ir.sequence'].create({
                'name': 'Equipment Company Sequence',
                'prefix': result.id,
                'padding': 5,
                'number_increment': 1,
                'company_id': result.id
            })
        return result
