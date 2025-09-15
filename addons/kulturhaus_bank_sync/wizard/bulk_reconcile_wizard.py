# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class BulkReconcileWizard(models.TransientModel):
    _name = 'bulk.reconcile.wizard'
    _description = 'Massen-Abstimmung Assistent'
    
    statement_id = fields.Many2one(
        'account.bank.statement',
        string='Bank Auszug',
        required=True
    )
    
    line_ids = fields.Many2many(
        'account.bank.statement.line',
        string='Auszugspositionen',
        domain="[('statement_id', '=', statement_id), ('is_reconciled', '=', False)]"
    )
    
    reconciliation_method = fields.Selection([
        ('auto', 'Automatisch (Regeln anwenden)'),
        ('partner', 'Nach Partner zuordnen'),
        ('amount', 'Nach Betrag zuordnen'),
        ('manual', 'Manuelles Konto zuweisen'),
    ], string='Abstimmungsmethode', required=True, default='auto')
    
    account_id = fields.Many2one(
        'account.account',
        string='Gegenkonto',
        help='Konto für manuelle Abstimmung'
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        help='Partner für Zuordnung'
    )
    
    create_invoices = fields.Boolean(
        string='Fehlende Rechnungen erstellen',
        default=False
    )
    
    @api.onchange('statement_id')
    def _onchange_statement_id(self):
        if self.statement_id:
            self.line_ids = self.statement_id.line_ids.filtered(
                lambda l: not l.is_reconciled
            )
    
    def action_reconcile(self):
        """Execute bulk reconciliation"""
        self.ensure_one()
        
        reconciled_count = 0
        
        if self.reconciliation_method == 'auto':
            # Apply reconciliation rules
            rules = self.env['bank.reconciliation.rule'].search([], order='sequence')
            for line in self.line_ids:
                for rule in rules:
                    if rule.apply_rule(line):
                        reconciled_count += 1
                        break
        
        elif self.reconciliation_method == 'partner':
            # Reconcile by partner
            if not self.partner_id:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Fehler'),
                        'message': _('Bitte wählen Sie einen Partner aus.'),
                        'type': 'danger',
                    }
                }
            
            for line in self.line_ids:
                line.partner_id = self.partner_id
                # Find matching invoices
                invoice = self.env['account.move'].search([
                    ('partner_id', '=', self.partner_id.id),
                    ('move_type', 'in', ['out_invoice', 'out_refund']),
                    ('state', '=', 'posted'),
                    ('payment_state', 'in', ['not_paid', 'partial']),
                    ('amount_residual', '=', abs(line.amount)),
                ], limit=1)
                
                if invoice:
                    self._reconcile_with_invoice(line, invoice)
                    reconciled_count += 1
                elif self.create_invoices:
                    invoice = self._create_invoice_for_line(line)
                    self._reconcile_with_invoice(line, invoice)
                    reconciled_count += 1
        
        elif self.reconciliation_method == 'amount':
            # Reconcile by amount matching
            for line in self.line_ids:
                if not line.partner_id:
                    continue
                
                invoice = self.env['account.move'].search([
                    ('partner_id', '=', line.partner_id.id),
                    ('move_type', 'in', ['out_invoice', 'out_refund']),
                    ('state', '=', 'posted'),
                    ('payment_state', 'in', ['not_paid', 'partial']),
                    ('amount_residual', '=', abs(line.amount)),
                ], limit=1)
                
                if invoice:
                    self._reconcile_with_invoice(line, invoice)
                    reconciled_count += 1
        
        elif self.reconciliation_method == 'manual':
            # Manual account assignment
            if not self.account_id:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Fehler'),
                        'message': _('Bitte wählen Sie ein Gegenkonto aus.'),
                        'type': 'danger',
                    }
                }
            
            for line in self.line_ids:
                self._create_manual_entry(line, self.account_id)
                reconciled_count += 1
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Abstimmung abgeschlossen'),
                'message': _('%d von %d Posten wurden abgestimmt.') % (reconciled_count, len(self.line_ids)),
                'type': 'success',
            }
        }
    
    def _reconcile_with_invoice(self, line, invoice):
        """Helper to reconcile line with invoice"""
        payment_vals = {
            'payment_type': 'inbound' if line.amount > 0 else 'outbound',
            'partner_id': invoice.partner_id.id,
            'amount': abs(line.amount),
            'currency_id': line.currency_id.id,
            'date': line.date,
            'journal_id': line.statement_id.journal_id.id,
            'payment_reference': line.payment_ref,
        }
        payment = self.env['account.payment'].create(payment_vals)
        payment.action_post()
        
        # Reconcile
        lines_to_reconcile = (invoice.line_ids + payment.line_ids).filtered(
            lambda l: l.account_id.account_type in ['asset_receivable', 'liability_payable']
        )
        lines_to_reconcile.reconcile()
        
        line.is_reconciled = True
    
    def _create_invoice_for_line(self, line):
        """Create invoice for unmatched payment"""
        invoice_vals = {
            'move_type': 'out_invoice' if line.amount > 0 else 'in_invoice',
            'partner_id': line.partner_id.id,
            'invoice_date': line.date,
            'ref': line.payment_ref,
            'invoice_line_ids': [(0, 0, {
                'name': line.narration or 'Zahlung ohne Rechnung',
                'quantity': 1,
                'price_unit': abs(line.amount),
            })],
        }
        invoice = self.env['account.move'].create(invoice_vals)
        invoice.action_post()
        return invoice
    
    def _create_manual_entry(self, line, account):
        """Create manual journal entry"""
        move_vals = {
            'date': line.date,
            'journal_id': line.statement_id.journal_id.id,
            'ref': line.payment_ref,
            'line_ids': [
                (0, 0, {
                    'account_id': line.statement_id.journal_id.default_account_id.id,
                    'debit': line.amount if line.amount > 0 else 0,
                    'credit': -line.amount if line.amount < 0 else 0,
                    'partner_id': line.partner_id.id,
                }),
                (0, 0, {
                    'account_id': account.id,
                    'debit': -line.amount if line.amount < 0 else 0,
                    'credit': line.amount if line.amount > 0 else 0,
                    'partner_id': line.partner_id.id,
                }),
            ],
        }
        
        move = self.env['account.move'].create(move_vals)
        move.action_post()
        line.is_reconciled = True