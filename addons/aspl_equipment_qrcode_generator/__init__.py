# -*- coding: utf-8 -*-

from odoo import api, SUPERUSER_ID

from . import models
from . import report
from . import wizard


# TODO: Generate Sequence For each company for Equipment
def pre_init_hook(env):
    company_ids = env['res.company'].search([])
    for company_id in company_ids:
        sequence_id = env['ir.sequence'].search(
            [('name', '=', 'Equipment Company Sequence'), ('company_id', '=', company_id.id)])
        if not sequence_id:
            env['ir.sequence'].create({
                'name': 'Equipment Company Sequence',
                'prefix': company_id.id,
                'padding': 5,
                'number_increment': 1,
                'company_id': company_id.id
            })
