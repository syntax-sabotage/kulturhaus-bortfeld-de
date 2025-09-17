# -*- coding: utf-8 -*-

from odoo import models, fields


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    qr_code = fields.Binary("QR Code")
    comp_serial_no = fields.Char("Inventory Serial No", tracking=True)
    serial_no = fields.Char('Mfg. Serial Number', copy=False)
    
    def action_print_qrcode_layout(self):
        action = self.env['ir.actions.act_window']._for_xml_id('aspl_equipment_qrcode_generator.action_open_label_layout_equipment')
        action['context'] = {'default_equipment_ids': self.ids}
        return action

    def generate_serial_no(self):
        for equipment_id in self:
            if not equipment_id.comp_serial_no:
                company_id = equipment_id.company_id.id
                sequence_id = self.env['ir.sequence'].search(
                    [('name', '=', 'Equipment Company Sequence'), ('company_id', '=', company_id)])
                if sequence_id:
                    data = sequence_id._next()
                    equipment_id.write({
                        'comp_serial_no': data
                    })
