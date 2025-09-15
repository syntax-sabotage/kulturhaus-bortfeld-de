# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api, _

class BankReconciliationRule(models.Model):
    _name = 'bank.reconciliation.rule'
    _description = 'Bank-Abstimmungsregel'
    _order = 'sequence, id'
    
    name = fields.Char(
        string='Regelname',
        required=True
    )
    
    sequence = fields.Integer(
        string='Reihenfolge',
        default=10
    )
    
    active = fields.Boolean(
        string='Aktiv',
        default=True
    )
    
    rule_type = fields.Selection([
        ('partner', 'Partner-Zuordnung'),
        ('reference', 'Referenz-Muster'),
        ('amount', 'Betragsmuster'),
        ('stripe', 'Stripe-Zahlung'),
        ('sepa', 'SEPA-Lastschrift'),
        ('invoice', 'Rechnungszuordnung'),
    ], string='Regeltyp', required=True)
    
    # Conditions
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner'
    )
    
    reference_pattern = fields.Char(
        string='Referenz-Muster',
        help='Regulärer Ausdruck für Verwendungszweck'
    )
    
    amount_min = fields.Monetary(
        string='Mindestbetrag',
        currency_field='currency_id'
    )
    
    amount_max = fields.Monetary(
        string='Höchstbetrag',
        currency_field='currency_id'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Währung',
        default=lambda self: self.env.company.currency_id
    )
    
    # Actions
    account_id = fields.Many2one(
        'account.account',
        string='Gegenkonto'
    )
    
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal'
    )
    
    auto_reconcile = fields.Boolean(
        string='Automatisch abstimmen',
        default=True
    )
    
    create_invoice = fields.Boolean(
        string='Rechnung erstellen',
        default=False
    )
    
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Kostenstelle'
    )
    
    def apply_rule(self, statement_line):
        """Apply reconciliation rule to a bank statement line"""
        self.ensure_one()
        
        # Check conditions
        if not self._check_conditions(statement_line):
            return False
        
        # Apply actions
        if self.rule_type == 'stripe':
            return self._reconcile_stripe(statement_line)
        elif self.rule_type == 'sepa':
            return self._reconcile_sepa(statement_line)
        elif self.rule_type == 'invoice':
            return self._reconcile_invoice(statement_line)
        elif self.auto_reconcile and self.account_id:
            return self._create_counterpart_entry(statement_line)
        
        return False
    
    def _check_conditions(self, statement_line):
        """Check if rule conditions match the statement line"""
        # Check partner
        if self.partner_id and statement_line.partner_id != self.partner_id:
            return False
        
        # Check reference pattern
        if self.reference_pattern:
            if not statement_line.payment_ref:
                return False
            if not re.search(self.reference_pattern, statement_line.payment_ref, re.IGNORECASE):
                return False
        
        # Check amount range
        amount = abs(statement_line.amount)
        if self.amount_min and amount < self.amount_min:
            return False
        if self.amount_max and amount > self.amount_max:
            return False
        
        return True
    
    def _reconcile_stripe(self, statement_line):
        """Reconcile with Stripe payment"""
        # Look for Stripe payment reference
        if not statement_line.payment_ref:
            return False
        
        # Extract Stripe payment ID from reference
        match = re.search(r'(pi_[a-zA-Z0-9]+)', statement_line.payment_ref)
        if match:
            stripe_id = match.group(1)
            statement_line.stripe_payment_id = stripe_id
            
            # Find related invoice
            invoice = self.env['account.move'].search([
                ('payment_reference', 'ilike', stripe_id),
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('state', '=', 'posted'),
            ], limit=1)
            
            if invoice:
                # Create payment and reconcile
                payment_vals = {
                    'payment_type': 'inbound' if statement_line.amount > 0 else 'outbound',
                    'partner_id': invoice.partner_id.id,
                    'amount': abs(statement_line.amount),
                    'currency_id': statement_line.currency_id.id,
                    'date': statement_line.date,
                    'journal_id': statement_line.statement_id.journal_id.id,
                    'payment_reference': statement_line.payment_ref,
                }
                payment = self.env['account.payment'].create(payment_vals)
                payment.action_post()
                
                # Reconcile with invoice
                lines_to_reconcile = (invoice.line_ids + payment.line_ids).filtered(
                    lambda l: l.account_id.account_type in ['asset_receivable', 'liability_payable']
                )
                lines_to_reconcile.reconcile()
                
                statement_line.is_reconciled = True
                return True
        
        return False
    
    def _reconcile_sepa(self, statement_line):
        """Reconcile with SEPA direct debit"""
        if not statement_line.payment_ref:
            return False
        
        # Look for mandate reference
        mandate_match = re.search(r'MANDATE[:\s]*([A-Z0-9-]+)', statement_line.payment_ref, re.IGNORECASE)
        if mandate_match:
            mandate_ref = mandate_match.group(1)
            statement_line.sepa_mandate_id = mandate_ref
            
            # Find partner with this mandate
            partner = self.env['res.partner'].search([
                ('sepa_mandate_ids.reference', '=', mandate_ref),
                ('sepa_mandate_ids.state', '=', 'valid'),
            ], limit=1)
            
            if partner:
                statement_line.partner_id = partner
                
                # Find or create membership invoice
                invoice = self.env['account.move'].search([
                    ('partner_id', '=', partner.id),
                    ('move_type', '=', 'out_invoice'),
                    ('state', '=', 'posted'),
                    ('payment_state', 'in', ['not_paid', 'partial']),
                    ('invoice_date', '>=', statement_line.date.replace(day=1)),
                ], limit=1)
                
                if invoice:
                    # Create payment and reconcile
                    return self._create_payment_and_reconcile(statement_line, invoice)
        
        return False
    
    def _reconcile_invoice(self, statement_line):
        """Reconcile with existing invoice"""
        if not statement_line.partner_id:
            return False
        
        # Find matching invoice by amount and partner
        invoice = self.env['account.move'].search([
            ('partner_id', '=', statement_line.partner_id.id),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ['not_paid', 'partial']),
            ('amount_residual', '=', abs(statement_line.amount)),
        ], limit=1)
        
        if invoice:
            return self._create_payment_and_reconcile(statement_line, invoice)
        
        return False
    
    def _create_counterpart_entry(self, statement_line):
        """Create counterpart journal entry"""
        if not self.account_id:
            return False
        
        move_vals = {
            'date': statement_line.date,
            'journal_id': self.journal_id.id if self.journal_id else statement_line.statement_id.journal_id.id,
            'ref': statement_line.payment_ref,
            'line_ids': [
                (0, 0, {
                    'account_id': statement_line.statement_id.journal_id.default_account_id.id,
                    'debit': statement_line.amount if statement_line.amount > 0 else 0,
                    'credit': -statement_line.amount if statement_line.amount < 0 else 0,
                    'partner_id': statement_line.partner_id.id,
                }),
                (0, 0, {
                    'account_id': self.account_id.id,
                    'debit': -statement_line.amount if statement_line.amount < 0 else 0,
                    'credit': statement_line.amount if statement_line.amount > 0 else 0,
                    'partner_id': statement_line.partner_id.id,
                    'analytic_account_id': self.analytic_account_id.id if self.analytic_account_id else False,
                }),
            ],
        }
        
        move = self.env['account.move'].create(move_vals)
        move.action_post()
        
        statement_line.is_reconciled = True
        return True
    
    def _create_payment_and_reconcile(self, statement_line, invoice):
        """Helper to create payment and reconcile with invoice"""
        payment_vals = {
            'payment_type': 'inbound' if statement_line.amount > 0 else 'outbound',
            'partner_id': invoice.partner_id.id,
            'amount': abs(statement_line.amount),
            'currency_id': statement_line.currency_id.id,
            'date': statement_line.date,
            'journal_id': statement_line.statement_id.journal_id.id,
            'payment_reference': statement_line.payment_ref,
        }
        payment = self.env['account.payment'].create(payment_vals)
        payment.action_post()
        
        # Reconcile
        lines_to_reconcile = (invoice.line_ids + payment.line_ids).filtered(
            lambda l: l.account_id.account_type in ['asset_receivable', 'liability_payable']
        )
        lines_to_reconcile.reconcile()
        
        statement_line.is_reconciled = True
        return True