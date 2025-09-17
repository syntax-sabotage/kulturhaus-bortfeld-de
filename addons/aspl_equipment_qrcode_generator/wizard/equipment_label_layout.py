# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models


class EquipmentLabelLayout(models.TransientModel):
    _name = 'equipment.label.layout'
    _description = 'Choose the sheet layout to print the labels'

    print_format = fields.Selection([
        ('2x5', '2 x 5'),
        ('2x7', '2 x 7'),
        ('4x7', '4 x 7')], string="Format", default='2x5', required=True)
    equipment_ids = fields.Many2many('maintenance.equipment')
    rows = fields.Integer(compute='_compute_dimensions')
    columns = fields.Integer(compute='_compute_dimensions')

    @api.depends('print_format')
    def _compute_dimensions(self):
        for wizard in self:
            if 'x' in wizard.print_format:
                columns, rows = wizard.print_format.split('x')[:2]
                wizard.columns = int(columns)
                wizard.rows = int(rows)
            else:
                wizard.columns, wizard.rows = 1, 1


    def process_label(self):
        xml_id = 'aspl_equipment_qrcode_generator.report_equipment_label'
        data = {
            'equipment_label_layout_id':self.id
        }
        
        return self.env.ref(xml_id).report_action(None, data=data)