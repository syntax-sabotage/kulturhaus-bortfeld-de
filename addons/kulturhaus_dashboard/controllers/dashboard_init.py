# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class DashboardInit(http.Controller):
    
    @http.route('/dashboard/init', type='json', auth='user')
    def init_dashboard(self):
        """Initialize dashboard for current user"""
        Dashboard = request.env['kulturhaus.dashboard']
        dashboard = Dashboard.search([('user_id', '=', request.env.user.id)], limit=1)
        
        if not dashboard:
            dashboard = Dashboard.create({
                'name': 'Main Dashboard',
                'user_id': request.env.user.id
            })
        
        return {
            'dashboard_id': dashboard.id,
            'action': {
                'type': 'ir.actions.act_window',
                'res_model': 'kulturhaus.dashboard',
                'view_mode': 'form',
                'res_id': dashboard.id,
                'target': 'current',
                'context': {'create': False, 'edit': False, 'delete': False}
            }
        }