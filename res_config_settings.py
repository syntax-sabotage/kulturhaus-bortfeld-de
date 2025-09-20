# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    default_meeting_type_id = fields.Many2one(
        'board.meeting.type',
        string='Default Meeting Type',
        default_model='board.resolution',
        help='Default meeting type for new board resolutions'
    )