# -*- coding: utf-8 -*-
from odoo import models, fields, api
import requests
import logging
import json
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class InstagramBusinessConfig(models.Model):
    _inherit = 'kulturhaus.instagram.config'
    
    # Facebook App Configuration
    facebook_app_id = fields.Char(string='Facebook App ID', help='Your Facebook App ID from developers.facebook.com')
    facebook_app_secret = fields.Char(string='Facebook App Secret', help='Your Facebook App Secret')
    facebook_access_token = fields.Text(string='Access Token', help='Facebook Page Access Token with instagram_basic permission')
    instagram_business_id = fields.Char(string='Instagram Business Account ID', help='Will be auto-detected')
    facebook_page_id = fields.Char(string='Facebook Page ID', help='Connected Facebook Page ID')
    
    # API Status
    api_connected = fields.Boolean(string='API Connected', compute='_compute_api_status', store=True)
    api_last_error = fields.Text(string='Last API Error')
    token_expires = fields.Datetime(string='Token Expires')
    
    @api.depends('facebook_access_token')
    def _compute_api_status(self):
        for record in self:
            record.api_connected = bool(record.facebook_access_token)
    
    def action_get_access_token(self):
        """Open Facebook OAuth dialog to get access token"""
        self.ensure_one()
        
        if not self.facebook_app_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Configuration Required',
                    'message': 'Please enter your Facebook App ID first',
                    'type': 'warning',
                }
            }
        
        # Build OAuth URL
        oauth_url = (
            f"https://www.facebook.com/v18.0/dialog/oauth?"
            f"client_id={self.facebook_app_id}"
            f"&redirect_uri=https://kulturhaus-bortfeld.de/instagram-callback"
            f"&scope=instagram_basic,instagram_manage_insights,pages_show_list,pages_read_engagement"
            f"&response_type=token"
        )
        
        return {
            'type': 'ir.actions.act_url',
            'url': oauth_url,
            'target': 'new',
        }
    
    def fetch_instagram_business_data(self):
        """Fetch data using Instagram Graph API for Business Accounts"""
        self.ensure_one()
        
        if not self.facebook_access_token:
            _logger.warning('No Facebook access token configured')
            return False
        
        try:
            # Base URL for Graph API
            base_url = 'https://graph.facebook.com/v18.0'
            
            # First, get Instagram Business Account ID if not set
            if not self.instagram_business_id:
                self._get_instagram_business_id()
            
            if not self.instagram_business_id:
                _logger.error('Could not retrieve Instagram Business Account ID')
                return False
            
            # Get Instagram account data
            fields_to_fetch = [
                'biography',
                'followers_count',
                'follows_count',
                'media_count',
                'name',
                'username',
                'website',
                'profile_picture_url'
            ]
            
            url = f"{base_url}/{self.instagram_business_id}"
            params = {
                'fields': ','.join(fields_to_fetch),
                'access_token': self.facebook_access_token
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                self.write({
                    'followers_count': data.get('followers_count', 0),
                    'following_count': data.get('follows_count', 0),
                    'media_count': data.get('media_count', 0),
                    'biography': data.get('biography', ''),
                    'website': data.get('website', ''),
                    'last_sync': fields.Datetime.now(),
                    'api_last_error': False
                })
                
                # Get insights for engagement rate
                self._fetch_engagement_insights()
                
                _logger.info(f'Successfully fetched Instagram data: {data.get("followers_count")} followers')
                return True
            else:
                error = response.json().get('error', {})
                error_msg = error.get('message', 'Unknown error')
                self.api_last_error = f"API Error: {error_msg}"
                _logger.error(f'Instagram API error: {error_msg}')
                return False
                
        except Exception as e:
            self.api_last_error = str(e)
            _logger.error(f'Failed to fetch Instagram Business data: {e}')
            return False
    
    def _get_instagram_business_id(self):
        """Get Instagram Business Account ID from connected Facebook Page"""
        if not self.facebook_access_token:
            return False
        
        try:
            # Get user's pages
            url = "https://graph.facebook.com/v18.0/me/accounts"
            params = {
                'access_token': self.facebook_access_token
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                pages = response.json().get('data', [])
                
                # Find page with Instagram Business Account
                for page in pages:
                    page_id = page.get('id')
                    page_token = page.get('access_token')
                    
                    # Get Instagram Business Account connected to this page
                    ig_url = f"https://graph.facebook.com/v18.0/{page_id}"
                    ig_params = {
                        'fields': 'instagram_business_account',
                        'access_token': page_token or self.facebook_access_token
                    }
                    
                    ig_response = requests.get(ig_url, params=ig_params)
                    
                    if ig_response.status_code == 200:
                        ig_data = ig_response.json()
                        ig_account = ig_data.get('instagram_business_account')
                        
                        if ig_account:
                            self.write({
                                'instagram_business_id': ig_account.get('id'),
                                'facebook_page_id': page_id,
                                'facebook_access_token': page_token or self.facebook_access_token
                            })
                            _logger.info(f'Found Instagram Business Account: {ig_account.get("id")}')
                            return True
            
            _logger.warning('No Instagram Business Account found')
            return False
            
        except Exception as e:
            _logger.error(f'Failed to get Instagram Business ID: {e}')
            return False
    
    def _fetch_engagement_insights(self):
        """Fetch engagement insights from Instagram Graph API"""
        if not self.instagram_business_id or not self.facebook_access_token:
            return False
        
        try:
            # Get recent media for engagement calculation
            url = f"https://graph.facebook.com/v18.0/{self.instagram_business_id}/media"
            params = {
                'fields': 'like_count,comments_count,timestamp',
                'limit': 25,  # Last 25 posts
                'access_token': self.facebook_access_token
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                media_data = response.json().get('data', [])
                
                if media_data and self.followers_count > 0:
                    total_engagement = sum(
                        post.get('like_count', 0) + post.get('comments_count', 0)
                        for post in media_data
                    )
                    
                    # Calculate average engagement rate
                    avg_engagement = total_engagement / len(media_data)
                    engagement_rate = (avg_engagement / self.followers_count) * 100
                    
                    self.engagement_rate = round(engagement_rate, 2)
                    _logger.info(f'Calculated engagement rate: {self.engagement_rate}%')
                    return True
        
        except Exception as e:
            _logger.error(f'Failed to fetch engagement insights: {e}')
        
        return False
    
    def action_sync_instagram_business(self):
        """Sync Instagram Business Account data"""
        self.ensure_one()
        
        if self.fetch_instagram_business_data():
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': f'Instagram Business data updated: {self.followers_count} followers',
                    'type': 'success',
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': self.api_last_error or 'Failed to fetch Instagram data',
                    'type': 'danger',
                }
            }
    
    def action_setup_facebook_app(self):
        """Guide user through Facebook App setup"""
        return {
            'type': 'ir.actions.act_url',
            'url': 'https://developers.facebook.com/apps/',
            'target': 'new',
        }
    
    @api.model
    def cron_sync_instagram_business(self):
        """Cron job to sync Instagram Business data"""
        configs = self.search([
            ('active', '=', True),
            ('auto_sync', '=', True),
            ('facebook_access_token', '!=', False)
        ])
        
        for config in configs:
            try:
                config.fetch_instagram_business_data()
                _logger.info(f'Instagram Business sync completed for {config.account_name}')
            except Exception as e:
                _logger.error(f'Instagram Business cron sync failed: {e}')