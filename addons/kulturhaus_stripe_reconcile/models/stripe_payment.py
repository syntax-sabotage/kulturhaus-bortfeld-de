# -*- coding: utf-8 -*-
import logging
import stripe as stripe_sdk
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class StripePayment(models.Model):
    _name = 'stripe.payment'
    _description = 'Stripe Zahlung'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'
    
    name = fields.Char(
        string='Stripe ID',
        required=True,
        readonly=True,
        index=True
    )
    
    payment_intent_id = fields.Char(
        string='Payment Intent ID',
        index=True
    )
    
    charge_id = fields.Char(
        string='Charge ID',
        index=True
    )
    
    customer_id = fields.Char(
        string='Stripe Customer ID',
        index=True
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Kunde',
        tracking=True
    )
    
    amount = fields.Monetary(
        string='Betrag',
        currency_field='currency_id',
        required=True,
        tracking=True
    )
    
    fee_amount = fields.Monetary(
        string='Stripe Gebühr',
        currency_field='currency_id',
        tracking=True
    )
    
    net_amount = fields.Monetary(
        string='Nettobetrag',
        currency_field='currency_id',
        compute='_compute_net_amount',
        store=True
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Währung',
        required=True,
        default=lambda self: self.env.company.currency_id
    )
    
    date = fields.Datetime(
        string='Zahlungsdatum',
        required=True,
        tracking=True
    )
    
    description = fields.Text(
        string='Beschreibung'
    )
    
    state = fields.Selection([
        ('pending', 'Ausstehend'),
        ('processing', 'In Bearbeitung'),
        ('succeeded', 'Erfolgreich'),
        ('failed', 'Fehlgeschlagen'),
        ('refunded', 'Erstattet'),
        ('partial_refund', 'Teilweise erstattet'),
        ('reconciled', 'Abgestimmt'),
    ], string='Status', default='pending', tracking=True)
    
    move_id = fields.Many2one(
        'account.move',
        string='Rechnung',
        tracking=True
    )
    
    payment_id = fields.Many2one(
        'account.payment',
        string='Zahlung',
        tracking=True
    )
    
    bank_statement_line_id = fields.Many2one(
        'account.bank.statement.line',
        string='Bankauszugszeile'
    )
    
    refund_amount = fields.Monetary(
        string='Erstattungsbetrag',
        currency_field='currency_id'
    )
    
    metadata = fields.Text(
        string='Stripe Metadata'
    )
    
    reconciled = fields.Boolean(
        string='Abgestimmt',
        compute='_compute_reconciled',
        store=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Unternehmen',
        required=True,
        default=lambda self: self.env.company
    )
    
    @api.depends('amount', 'fee_amount')
    def _compute_net_amount(self):
        for record in self:
            record.net_amount = record.amount - record.fee_amount
    
    @api.depends('payment_id', 'bank_statement_line_id')
    def _compute_reconciled(self):
        for record in self:
            record.reconciled = bool(record.payment_id and record.bank_statement_line_id)
    
    @api.model
    def create_from_webhook(self, stripe_event):
        """Create or update payment from Stripe webhook event"""
        if stripe_event['type'] == 'payment_intent.succeeded':
            payment_intent = stripe_event['data']['object']
            return self._process_payment_intent(payment_intent)
        
        elif stripe_event['type'] == 'charge.succeeded':
            charge = stripe_event['data']['object']
            return self._process_charge(charge)
        
        elif stripe_event['type'] == 'charge.refunded':
            charge = stripe_event['data']['object']
            return self._process_refund(charge)
        
        return False
    
    def _process_payment_intent(self, payment_intent):
        """Process payment intent from Stripe"""
        # Check if already exists
        existing = self.search([('payment_intent_id', '=', payment_intent['id'])], limit=1)
        
        vals = {
            'payment_intent_id': payment_intent['id'],
            'name': payment_intent['id'],
            'amount': payment_intent['amount'] / 100.0,  # Convert from cents
            'currency_id': self._get_currency(payment_intent['currency']).id,
            'date': datetime.fromtimestamp(payment_intent['created']),
            'state': 'succeeded',
            'metadata': str(payment_intent.get('metadata', {})),
        }
        
        # Try to find customer
        if payment_intent.get('customer'):
            vals['customer_id'] = payment_intent['customer']
            partner = self._find_partner_by_stripe_customer(payment_intent['customer'])
            if partner:
                vals['partner_id'] = partner.id
        
        # Try to find invoice
        if payment_intent.get('metadata', {}).get('invoice_id'):
            invoice_id = int(payment_intent['metadata']['invoice_id'])
            invoice = self.env['account.move'].browse(invoice_id)
            if invoice.exists():
                vals['move_id'] = invoice.id
                vals['partner_id'] = invoice.partner_id.id
        
        if existing:
            existing.write(vals)
            return existing
        else:
            return self.create(vals)
    
    def _process_charge(self, charge):
        """Process charge from Stripe"""
        # Check if already exists
        existing = self.search([('charge_id', '=', charge['id'])], limit=1)
        
        vals = {
            'charge_id': charge['id'],
            'name': charge['id'],
            'amount': charge['amount'] / 100.0,
            'currency_id': self._get_currency(charge['currency']).id,
            'date': datetime.fromtimestamp(charge['created']),
            'state': 'succeeded' if charge['paid'] else 'failed',
            'description': charge.get('description', ''),
        }
        
        # Add fees if available
        if charge.get('balance_transaction'):
            # Would need to fetch balance transaction for fee details
            pass
        
        # Link to payment intent if exists
        if charge.get('payment_intent'):
            vals['payment_intent_id'] = charge['payment_intent']
            
            # Check if payment intent record exists
            pi_payment = self.search([('payment_intent_id', '=', charge['payment_intent'])], limit=1)
            if pi_payment:
                pi_payment.write({'charge_id': charge['id']})
                return pi_payment
        
        if charge.get('customer'):
            vals['customer_id'] = charge['customer']
            partner = self._find_partner_by_stripe_customer(charge['customer'])
            if partner:
                vals['partner_id'] = partner.id
        
        if existing:
            existing.write(vals)
            return existing
        else:
            return self.create(vals)
    
    def _process_refund(self, charge):
        """Process refund from Stripe"""
        payment = self.search([('charge_id', '=', charge['id'])], limit=1)
        if payment:
            refunded_amount = charge['amount_refunded'] / 100.0
            if refunded_amount >= payment.amount:
                payment.state = 'refunded'
            else:
                payment.state = 'partial_refund'
            payment.refund_amount = refunded_amount
        return payment
    
    def _get_currency(self, currency_code):
        """Get currency from code"""
        currency = self.env['res.currency'].search([('name', '=', currency_code.upper())], limit=1)
        if not currency:
            currency = self.env.company.currency_id
        return currency
    
    def _find_partner_by_stripe_customer(self, customer_id):
        """Find partner by Stripe customer ID"""
        # First check if stored in partner
        partner = self.env['res.partner'].search([
            ('stripe_customer_id', '=', customer_id)
        ], limit=1)
        
        if not partner:
            # Try to fetch from Stripe and match by email
            try:
                stripe_sdk.api_key = self.env.company.stripe_secret_key
                customer = stripe_sdk.Customer.retrieve(customer_id)
                if customer.get('email'):
                    partner = self.env['res.partner'].search([
                        ('email', '=', customer['email'])
                    ], limit=1)
                    if partner:
                        partner.stripe_customer_id = customer_id
            except Exception as e:
                _logger.error(f"Error fetching Stripe customer: {e}")
        
        return partner
    
    def action_reconcile(self):
        """Reconcile Stripe payment with invoice and bank"""
        self.ensure_one()
        
        if not self.move_id:
            raise UserError(_('Keine verknüpfte Rechnung gefunden.'))
        
        if self.payment_id:
            raise UserError(_('Zahlung bereits abgestimmt.'))
        
        # Create payment
        payment_vals = {
            'payment_type': 'inbound',
            'partner_id': self.partner_id.id,
            'amount': self.net_amount,  # Use net amount after fees
            'currency_id': self.currency_id.id,
            'date': self.date.date(),
            'journal_id': self._get_stripe_journal().id,
            'payment_reference': self.name,
        }
        
        payment = self.env['account.payment'].create(payment_vals)
        payment.action_post()
        
        # Link payment
        self.payment_id = payment
        
        # Reconcile with invoice
        lines_to_reconcile = (self.move_id.line_ids + payment.line_ids).filtered(
            lambda l: l.account_id.account_type in ['asset_receivable', 'liability_payable']
        )
        lines_to_reconcile.reconcile()
        
        # Create fee entry if needed
        if self.fee_amount > 0:
            self._create_fee_entry()
        
        self.state = 'reconciled'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Erfolgreich'),
                'message': _('Zahlung wurde abgestimmt.'),
                'type': 'success',
            }
        }
    
    def _get_stripe_journal(self):
        """Get or create Stripe journal"""
        journal = self.env['account.journal'].search([
            ('code', '=', 'STRIPE'),
            ('type', '=', 'bank'),
            ('company_id', '=', self.company_id.id)
        ], limit=1)
        
        if not journal:
            journal = self.env['account.journal'].create({
                'name': 'Stripe',
                'code': 'STRIPE',
                'type': 'bank',
                'company_id': self.company_id.id,
            })
        
        return journal
    
    def _create_fee_entry(self):
        """Create journal entry for Stripe fees"""
        fee_account = self.env['account.account'].search([
            ('code', '=', '6400'),  # Bank charges account
            ('company_id', '=', self.company_id.id)
        ], limit=1)
        
        if not fee_account:
            fee_account = self.env['account.account'].search([
                ('account_type', '=', 'expense'),
                ('company_id', '=', self.company_id.id)
            ], limit=1)
        
        move_vals = {
            'date': self.date.date(),
            'journal_id': self._get_stripe_journal().id,
            'ref': f'Stripe Gebühr {self.name}',
            'line_ids': [
                (0, 0, {
                    'account_id': fee_account.id,
                    'debit': self.fee_amount,
                    'credit': 0,
                    'name': f'Stripe Gebühr für {self.name}',
                }),
                (0, 0, {
                    'account_id': self._get_stripe_journal().default_account_id.id,
                    'debit': 0,
                    'credit': self.fee_amount,
                    'name': f'Stripe Gebühr für {self.name}',
                }),
            ],
        }
        
        move = self.env['account.move'].create(move_vals)
        move.action_post()
        
        return move
    
    @api.model
    def sync_stripe_payments(self, date_from=None, date_to=None):
        """Sync payments from Stripe API"""
        try:
            stripe_sdk.api_key = self.env.company.stripe_secret_key
            
            # Prepare filters
            filters = {'limit': 100}
            if date_from:
                filters['created'] = {'gte': int(date_from.timestamp())}
            if date_to:
                if 'created' not in filters:
                    filters['created'] = {}
                filters['created']['lte'] = int(date_to.timestamp())
            
            # Fetch charges
            charges = stripe_sdk.Charge.list(**filters)
            
            for charge in charges.data:
                self._process_charge(charge)
            
            return True
            
        except Exception as e:
            _logger.error(f"Error syncing Stripe payments: {e}")
            raise UserError(_('Fehler beim Synchronisieren: %s') % str(e))