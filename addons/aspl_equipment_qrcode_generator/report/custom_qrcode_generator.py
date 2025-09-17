# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import math
from io import BytesIO

import qrcode
from odoo import models


def generate_qr_code(value):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=20,
        border=4,
    )
    qr.add_data(value)
    qr.make(fit=True)
    img = qr.make_image()
    temp = BytesIO()
    img.save(temp, format="PNG")
    qr_img = base64.b64encode(temp.getvalue())
    return qr_img


def _prepare_data(env, data):
    equipment_label_layout_id = env['equipment.label.layout'].browse(data['equipment_label_layout_id'])
    equipment_dict = {}
    equipment_ids = equipment_label_layout_id.equipment_ids
    for equipment in equipment_ids:
        if not equipment.name:
            continue
        equipment_dict[equipment] = 1
        combine_equipment_detail = ""

        # Generate Equipment Redirect LInk
        url = env['ir.config_parameter'].sudo().get_param('web.base.url')
        menuId = env.ref('maintenance.menu_equipment_form').sudo().id
        actionId = env.ref('maintenance.hr_equipment_action').sudo().id

        equipment_link = url + '/web#id=' + str(equipment.id) + '&menu_id=' + str(menuId) + '&action=' + str(
            actionId) + '&model=maintenance.equipment&view_type=form'

        # Prepare main Equipment Detail
        main_equipment_detail = ""
        main_equipment_detail = main_equipment_detail.join(
            "Name: " + str(equipment.name) + "\n" +
            "Model: " + str(equipment.model) + "\n" +
            "Mfg serial no: " + str(equipment.serial_no) + "\n"
            "Warranty Exp. Date: "  +str(equipment.warranty_date) + "\n"
            "Category: " +str(equipment.category_id.name)
        )
        # main_equipment_detail = equipment_link + '\n' + '\n' + main_equipment_detail

        # Prepare Child Equipment Detail
        combine_equipment_detail = main_equipment_detail

        combine_equipment_detail += '\n' + '\n' + equipment_link

        # Generate Qr Code depends on Details
        qr_image = generate_qr_code(combine_equipment_detail)
        equipment.write({
            'qr_code': qr_image
        })
        env.cr.commit()
    page_numbers = (len(equipment_ids) - 1) // (equipment_label_layout_id.rows * equipment_label_layout_id.columns) + 1
    
    dict_equipment = {
        'rows': equipment_label_layout_id.rows,
        'columns': equipment_label_layout_id.columns,
        'page_numbers': page_numbers,
        'equipment_data': equipment_dict
    }
    return dict_equipment


class ReportProductTemplateLabel(models.AbstractModel):
    _name = 'report.aspl_equipment_qrcode_generator.maintenance_quip'
    _description = 'Equipment QR-code Report'

    def _get_report_values(self, docids, data):
        return _prepare_data(self.env, data)
