# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import requests
import json
import logging
from urllib.parse import urlencode

_logger = logging.getLogger(__name__)

class InstagramOAuthController(http.Controller):
    
    # Facebook App Credentials
    FACEBOOK_APP_ID = "1123308493238410"
    FACEBOOK_APP_SECRET = "802d2f3001db751111487afef63207f5"
    
    # Use local redirect for development
    def _get_redirect_uri(self):
        # Check if we're in local development
        if 'localhost' in request.httprequest.host or '127.0.0.1' in request.httprequest.host:
            return "http://localhost:8070/instagram/callback"
        return "https://kulturhaus-bortfeld.de/instagram/callback"
    
    @http.route('/instagram/auth', auth='user', website=True)
    def instagram_auth(self, **kw):
        """Initiate Instagram OAuth flow"""
        # Build Facebook OAuth URL
        oauth_url = "https://www.facebook.com/v18.0/dialog/oauth"
        params = {
            'client_id': self.FACEBOOK_APP_ID,
            'redirect_uri': self._get_redirect_uri(),
            'scope': 'instagram_basic,pages_show_list,pages_read_engagement,business_management',
            'response_type': 'code',
            'state': str(request.env.user.id)  # For security
        }
        
        # Build the complete URL with proper encoding
        auth_url = f"{oauth_url}?{urlencode(params)}"
        
        _logger.info(f"Redirecting to Facebook OAuth: {auth_url}")
        
        return request.redirect(auth_url)
    
    @http.route('/instagram/callback', auth='public', website=True, csrf=False)
    def instagram_callback(self, code=None, error=None, **kw):
        """Handle OAuth callback from Facebook"""
        
        if error:
            _logger.error(f"Instagram OAuth Error: {error}")
            return request.redirect('/web#action=kulturhaus_dashboard.action_instagram_config')
        
        if not code:
            _logger.error("No authorization code received")
            return request.redirect('/web#action=kulturhaus_dashboard.action_instagram_config')
        
        try:
            # Get the Instagram config record
            instagram_config = request.env['kulturhaus.instagram.config'].sudo().search([], limit=1)
            if not instagram_config:
                instagram_config = request.env['kulturhaus.instagram.config'].sudo().create({
                    'account_name': 'kulturhaus_bortfeld'
                })
            
            # Exchange code for access token
            token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
            
            # Use hardcoded app secret
            app_secret = self.FACEBOOK_APP_SECRET
            
            token_params = {
                'client_id': self.FACEBOOK_APP_ID,
                'client_secret': app_secret,
                'redirect_uri': self._get_redirect_uri(),
                'code': code
            }
            
            response = requests.get(token_url, params=token_params)
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get('access_token')
                
                if access_token:
                    # Store the access token
                    instagram_config.write({
                        'facebook_app_id': self.FACEBOOK_APP_ID,
                        'facebook_access_token': access_token,
                        'api_connected': True
                    })
                    
                    # Get Instagram Business Account ID
                    self._get_instagram_business_account(instagram_config, access_token)
                    
                    _logger.info("Instagram OAuth successful!")
                    message = "Instagram erfolgreich verbunden!"
                else:
                    _logger.error("No access token in response")
                    message = "Fehler: Kein Access Token erhalten"
            else:
                _logger.error(f"Token exchange failed: {response.text}")
                message = f"Fehler beim Token-Austausch: {response.status_code}"
                
        except Exception as e:
            _logger.error(f"OAuth callback error: {str(e)}")
            message = f"Fehler: {str(e)}"
        
        # Redirect back to Instagram config with message
        return request.redirect(f'/web#action=kulturhaus_dashboard.action_instagram_config&message={message}')
    
    def _get_instagram_business_account(self, config, access_token):
        """Get Instagram Business Account ID from Facebook Pages"""
        try:
            # Get Facebook Pages
            pages_url = "https://graph.facebook.com/v18.0/me/accounts"
            pages_response = requests.get(pages_url, params={'access_token': access_token})
            
            if pages_response.status_code == 200:
                pages_data = pages_response.json()
                
                for page in pages_data.get('data', []):
                    page_id = page.get('id')
                    page_access_token = page.get('access_token')
                    
                    # Get Instagram Business Account for this page
                    ig_url = f"https://graph.facebook.com/v18.0/{page_id}?fields=instagram_business_account&access_token={page_access_token}"
                    ig_response = requests.get(ig_url)
                    
                    if ig_response.status_code == 200:
                        ig_data = ig_response.json()
                        ig_account = ig_data.get('instagram_business_account')
                        
                        if ig_account:
                            ig_id = ig_account.get('id')
                            config.write({
                                'instagram_business_id': ig_id,
                                'facebook_page_id': page_id
                            })
                            _logger.info(f"Instagram Business Account found: {ig_id}")
                            
                            # Fetch initial data
                            config.fetch_instagram_data()
                            break
                            
        except Exception as e:
            _logger.error(f"Error getting Instagram Business Account: {str(e)}")
    
    @http.route('/instagram/test', auth='public', website=True)
    def instagram_test(self, **kw):
        """Test endpoint to check if Instagram API is working"""
        try:
            config = request.env['kulturhaus.instagram.config'].sudo().search([], limit=1)
            if config and config.api_connected:
                data = {
                    'status': 'connected',
                    'app_id': config.facebook_app_id,
                    'instagram_id': config.instagram_business_id,
                    'followers': config.followers_count
                }
            else:
                data = {
                    'status': 'not_connected',
                    'message': 'Instagram API not configured'
                }
        except Exception as e:
            data = {
                'status': 'error',
                'message': str(e)
            }
        
        return request.make_response(
            json.dumps(data),
            headers=[('Content-Type', 'application/json')]
        )