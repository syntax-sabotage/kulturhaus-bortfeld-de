# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    is_nonprofit = fields.Boolean(
        string='Gemeinnützige Organisation',
        default=True,
        help='Aktiviert spezielle Funktionen für gemeinnützige Vereine'
    )
    
    nonprofit_register_number = fields.Char(
        string='Vereinsregisternummer',
        help='Registernummer des Vereins (z.B. VR 1234)'
    )
    
    tax_office = fields.Char(
        string='Finanzamt',
        help='Zuständiges Finanzamt'
    )
    
    tax_number = fields.Char(
        string='Steuernummer',
        help='Steuernummer des Vereins'
    )
    
    nonprofit_certificate_date = fields.Date(
        string='Datum Gemeinnützigkeitsbescheid',
        help='Datum des letzten Freistellungsbescheids'
    )