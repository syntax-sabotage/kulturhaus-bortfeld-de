# -*- coding: utf-8 -*-
import json
import logging
import stripe
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class StripeWebhook(http.Controller):
    
    @http.route('/stripe/webhook', type='json', auth='public', methods=['POST'], csrf=False)
    def stripe_webhook(self, **kwargs):
        """Handle Stripe webhook events"""
        payload = request.httprequest.data
        sig_header = request.httprequest.headers.get('Stripe-Signature')
        
        webhook_secret = request.env['ir.config_parameter'].sudo().get_param(
            'kulturhaus_stripe_reconcile.stripe_webhook_secret'
        )
        
        if not webhook_secret:
            _logger.error("Stripe webhook secret not configured")
            return {'status': 'error', 'message': 'Webhook secret not configured'}
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError:
            _logger.error("Invalid payload")
            return {'status': 'error', 'message': 'Invalid payload'}
        except stripe.error.SignatureVerificationError:
            _logger.error("Invalid signature")
            return {'status': 'error', 'message': 'Invalid signature'}
        
        # Process the event
        _logger.info(f"Processing Stripe event: {event['type']}")
        
        try:
            if event['type'] in ['payment_intent.succeeded', 'charge.succeeded', 'charge.refunded']:
                request.env['stripe.payment'].sudo().create_from_webhook(event)
            
            return {'status': 'success'}
            
        except Exception as e:
            _logger.error(f"Error processing webhook: {e}")
            return {'status': 'error', 'message': str(e)}