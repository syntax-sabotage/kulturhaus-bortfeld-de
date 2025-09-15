# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import requests
import json

class InstagramManualController(http.Controller):
    
    @http.route('/instagram/manual-token', auth='public', website=True)
    def manual_token_form(self, **kw):
        """Show a form to manually enter access token"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Instagram Token Setup</title>
            <style>
                body { font-family: Arial; padding: 20px; max-width: 800px; margin: 0 auto; }
                .container { background: #f5f5f5; padding: 20px; border-radius: 8px; }
                input, textarea { width: 100%; padding: 10px; margin: 10px 0; }
                button { background: #1877f2; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
                .info { background: #e3f2fd; padding: 15px; border-radius: 4px; margin: 20px 0; }
                .success { background: #c8e6c9; padding: 15px; border-radius: 4px; margin: 20px 0; }
                .error { background: #ffcdd2; padding: 15px; border-radius: 4px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Instagram Business API - Manual Token Setup</h1>
                
                <div class="info">
                    <h3>So bekommst du einen Access Token:</h3>
                    <ol>
                        <li>Öffne diesen Link in einem neuen Tab: 
                            <a href="https://www.facebook.com/v18.0/dialog/oauth?client_id=1123308493238410&redirect_uri=https://www.facebook.com/&scope=pages_show_list,instagram_basic,pages_read_engagement&response_type=token" target="_blank">
                                Token generieren
                            </a>
                        </li>
                        <li>Melde dich mit deinem Facebook-Account an</li>
                        <li>Nach der Autorisierung wirst du zu Facebook weitergeleitet</li>
                        <li>Kopiere den <strong>access_token</strong> aus der URL (nach #access_token=...)</li>
                        <li>Füge ihn unten ein</li>
                    </ol>
                </div>
                
                <form method="post" action="/instagram/save-token">
                    <label>Access Token:</label>
                    <textarea name="access_token" rows="4" placeholder="Füge hier deinen Access Token ein..."></textarea>
                    
                    <label>Instagram Business Account ID (optional):</label>
                    <input type="text" name="instagram_id" placeholder="17841464815983915" value="17841464815983915">
                    
                    <button type="submit">Token speichern und testen</button>
                </form>
                
                <div class="info">
                    <strong>Alternative:</strong> Verwende den Graph API Explorer:
                    <a href="https://developers.facebook.com/tools/explorer/?method=GET&path=me%2Faccounts&version=v18.0" target="_blank">
                        Graph API Explorer öffnen
                    </a>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    @http.route('/instagram/save-token', auth='public', website=True, methods=['POST'], csrf=False)
    def save_token(self, access_token=None, instagram_id=None, **kw):
        """Save the manually entered token"""
        if not access_token:
            return "Fehler: Kein Token angegeben"
        
        try:
            # Get or create Instagram config
            instagram_config = request.env['kulturhaus.instagram.config'].sudo().search([], limit=1)
            if not instagram_config:
                instagram_config = request.env['kulturhaus.instagram.config'].sudo().create({
                    'account_name': 'kulturhaus_bortfeld'
                })
            
            # Save token
            instagram_config.write({
                'facebook_app_id': '1123308493238410',
                'facebook_access_token': access_token,
                'api_connected': True
            })
            
            if instagram_id:
                instagram_config.write({'instagram_business_id': instagram_id})
            
            # Test the token
            test_url = f"https://graph.facebook.com/v18.0/me?access_token={access_token}"
            response = requests.get(test_url)
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Try to get Instagram Business Account
                pages_url = f"https://graph.facebook.com/v18.0/me/accounts?access_token={access_token}"
                pages_response = requests.get(pages_url)
                
                if pages_response.status_code == 200:
                    pages_data = pages_response.json()
                    result = f"""
                    <html><body style="font-family: Arial; padding: 20px;">
                    <h2 style="color: green;">✅ Token erfolgreich gespeichert!</h2>
                    <p>Facebook User: {user_data.get('name', 'Unknown')}</p>
                    <p>User ID: {user_data.get('id', 'Unknown')}</p>
                    """
                    
                    if pages_data.get('data'):
                        result += "<h3>Gefundene Facebook Pages:</h3><ul>"
                        for page in pages_data.get('data', []):
                            result += f"<li>{page.get('name')} (ID: {page.get('id')})</li>"
                        result += "</ul>"
                    
                    result += """
                    <p><a href="/web#action=kulturhaus_dashboard.action_instagram_config">→ Zur Instagram Konfiguration</a></p>
                    <p><a href="/instagram/test">→ API Status testen</a></p>
                    </body></html>
                    """
                    
                    # Fetch Instagram data
                    instagram_config.fetch_instagram_data()
                    
                    return result
                else:
                    return f"Token gespeichert, aber Pages-Abruf fehlgeschlagen: {pages_response.text}"
            else:
                return f"Token-Test fehlgeschlagen: {response.text}"
                
        except Exception as e:
            return f"Fehler: {str(e)}"
    
    @http.route('/instagram/debug', auth='public', website=True)
    def debug_info(self, **kw):
        """Show debug information"""
        try:
            config = request.env['kulturhaus.instagram.config'].sudo().search([], limit=1)
            if config:
                info = {
                    'api_connected': config.api_connected,
                    'has_token': bool(config.facebook_access_token),
                    'instagram_id': config.instagram_business_id,
                    'app_id': config.facebook_app_id,
                    'last_error': config.api_last_error
                }
            else:
                info = {'error': 'No configuration found'}
        except Exception as e:
            info = {'error': str(e)}
        
        return request.make_response(
            json.dumps(info, indent=2),
            headers=[('Content-Type', 'application/json')]
        )