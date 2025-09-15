# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class AccountFiscalYear(models.Model):
    _name = 'account.fiscal.year'
    _description = 'Geschäftsjahr'
    _order = 'date_from desc'
    
    name = fields.Char(
        string='Bezeichnung',
        required=True
    )
    
    code = fields.Char(
        string='Code',
        required=True,
        help='Kurzbezeichnung des Geschäftsjahres (z.B. 2024)'
    )
    
    date_from = fields.Date(
        string='Startdatum',
        required=True
    )
    
    date_to = fields.Date(
        string='Enddatum',
        required=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Unternehmen',
        required=True,
        default=lambda self: self.env.company
    )
    
    state = fields.Selection([
        ('draft', 'Entwurf'),
        ('open', 'Offen'),
        ('closed', 'Geschlossen')
    ], string='Status', default='draft')
    
    period_ids = fields.One2many(
        'account.fiscal.period',
        'fiscal_year_id',
        string='Perioden'
    )
    
    @api.model
    def create(self, vals):
        fiscal_year = super().create(vals)
        fiscal_year._create_periods()
        return fiscal_year
    
    def _create_periods(self):
        """Create monthly periods for the fiscal year"""
        for fy in self:
            period_start = fy.date_from
            period_number = 1
            
            while period_start < fy.date_to:
                period_end = min(
                    period_start + relativedelta(months=1, days=-1),
                    fy.date_to
                )
                
                self.env['account.fiscal.period'].create({
                    'name': f"{fy.code}/{period_number:02d}",
                    'code': f"{fy.code}{period_number:02d}",
                    'date_from': period_start,
                    'date_to': period_end,
                    'fiscal_year_id': fy.id,
                    'company_id': fy.company_id.id,
                })
                
                period_start = period_end + relativedelta(days=1)
                period_number += 1
    
    def action_open(self):
        """Open the fiscal year"""
        self.write({'state': 'open'})
    
    def action_close(self):
        """Close the fiscal year"""
        self.write({'state': 'closed'})


class AccountFiscalPeriod(models.Model):
    _name = 'account.fiscal.period'
    _description = 'Buchhaltungsperiode'
    _order = 'date_from'
    
    name = fields.Char(
        string='Bezeichnung',
        required=True
    )
    
    code = fields.Char(
        string='Code',
        required=True
    )
    
    date_from = fields.Date(
        string='Startdatum',
        required=True
    )
    
    date_to = fields.Date(
        string='Enddatum',
        required=True
    )
    
    fiscal_year_id = fields.Many2one(
        'account.fiscal.year',
        string='Geschäftsjahr',
        required=True,
        ondelete='cascade'
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Unternehmen',
        required=True
    )
    
    state = fields.Selection([
        ('draft', 'Entwurf'),
        ('open', 'Offen'),
        ('closed', 'Geschlossen')
    ], string='Status', default='draft')