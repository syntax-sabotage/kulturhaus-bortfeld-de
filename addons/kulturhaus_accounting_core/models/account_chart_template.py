# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class AccountChartTemplate(models.Model):
    _inherit = 'account.chart.template'
    
    @api.model
    def _get_skr49_chart_template(self):
        """Get or create SKR49 chart template"""
        template = self.search([('name', '=', 'SKR49 - Gemeinnützige Vereine')], limit=1)
        if not template:
            template = self.create({
                'name': 'SKR49 - Gemeinnützige Vereine',
                'code_digits': 4,
                'currency_id': self.env.ref('base.EUR').id,
                'use_anglo_saxon': False,
                'country_id': self.env.ref('base.de').id,
            })
        return template