# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class DashboardController(http.Controller):
    
    @http.route('/dashboard/data', type='json', auth='user', website=False)
    def get_dashboard_data(self, **kwargs):
        """Get all dashboard data in single API call"""
        try:
            Dashboard = request.env['kulturhaus.dashboard']
            data = Dashboard.get_dashboard_data()
            return {'success': True, 'data': data}
        except Exception as e:
            _logger.error(f"Dashboard data error: {e}")
            return {'success': False, 'error': str(e)}
    
    @http.route('/dashboard/refresh/<string:widget>', type='json', auth='user')
    def refresh_widget(self, widget, **kwargs):
        """Refresh specific widget data"""
        try:
            Dashboard = request.env['kulturhaus.dashboard']
            dashboard = Dashboard.search([('user_id', '=', request.env.user.id)], limit=1)
            
            if not dashboard:
                dashboard = Dashboard.create({'user_id': request.env.user.id})
            
            widget_map = {
                'members': '_compute_member_metrics',
                'churn': '_compute_quarterly_churn',
                'sepa': '_compute_sepa_metrics',
                'events': '_compute_event_metrics',
                'website': '_compute_website_metrics',
                'social': '_compute_social_metrics'
            }
            
            if widget in widget_map:
                getattr(dashboard, widget_map[widget])()
                
            data = Dashboard.get_dashboard_data()
            return {'success': True, 'data': data.get(widget, {})}
            
        except Exception as e:
            _logger.error(f"Widget refresh error: {e}")
            return {'success': False, 'error': str(e)}
    
    @http.route('/dashboard/quick-action/instagram', type='json', auth='user')
    def quick_instagram(self, message, image_url=None, **kwargs):
        """Quick action: Post to Instagram"""
        try:
            Dashboard = request.env['kulturhaus.dashboard']
            result = Dashboard.quick_action_instagram(message, image_url)
            return result
        except Exception as e:
            _logger.error(f"Instagram action error: {e}")
            return {'success': False, 'error': str(e)}
    
    @http.route('/dashboard/quick-action/telegram', type='json', auth='user')
    def quick_telegram(self, message, **kwargs):
        """Quick action: Send to Telegram"""
        try:
            Dashboard = request.env['kulturhaus.dashboard']
            result = Dashboard.quick_action_telegram(message)
            return result
        except Exception as e:
            _logger.error(f"Telegram action error: {e}")
            return {'success': False, 'error': str(e)}
    
    @http.route('/dashboard/websocket/subscribe', type='json', auth='user')
    def websocket_subscribe(self, **kwargs):
        """Subscribe to real-time updates via WebSocket"""
        # Return WebSocket configuration
        return {
            'success': True,
            'config': {
                'url': '/websocket',
                'channels': ['dashboard.updates'],
                'user_id': request.env.user.id
            }
        }