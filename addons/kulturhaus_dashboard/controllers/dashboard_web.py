# -*- coding: utf-8 -*-
from odoo import http, fields
from odoo.http import request

class DashboardWeb(http.Controller):
    
    @http.route('/dashboard', type='http', auth='user', website=False)
    def dashboard_page(self, **kwargs):
        """Simple HTML dashboard page"""
        
        # Get member count
        member_count = request.env['res.partner'].search_count([
            ('is_company', '=', False),
            ('sepa_mandate_active', '=', True)
        ])
        
        # Get next event
        next_event = request.env['event.event'].search([
            ('date_begin', '>', fields.Datetime.now())
        ], order='date_begin asc', limit=1)
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Kulturhaus Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {{ background: #f5f5f7; padding: 20px; }}
        .dashboard-card {{ 
            background: white; 
            border-radius: 12px; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            padding: 20px;
            margin-bottom: 20px;
            cursor: pointer;
            transition: all 0.3s;
        }}
        .dashboard-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        }}
        .card-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 8px 8px 0 0;
            margin: -20px -20px 20px -20px;
            font-weight: 600;
        }}
        .metric-value {{
            font-size: 48px;
            font-weight: 700;
            color: #2c3e50;
        }}
        .btn-action {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            font-weight: 600;
            margin: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-center mb-5">
            <i class="fas fa-home"></i> Kulturhaus Dashboard
        </h1>
        
        <div class="row">
            <!-- Active Members -->
            <div class="col-md-4">
                <div class="dashboard-card">
                    <div class="card-header">
                        <i class="fas fa-users"></i> Aktive Mitglieder
                    </div>
                    <div class="text-center">
                        <div class="metric-value">{member_count}</div>
                        <p class="text-success">
                            <i class="fas fa-arrow-up"></i> +3 diesen Monat
                        </p>
                    </div>
                </div>
            </div>
            
            <!-- SEPA Status -->
            <div class="col-md-4">
                <div class="dashboard-card">
                    <div class="card-header">
                        <i class="fas fa-euro-sign"></i> SEPA Status
                    </div>
                    <div class="text-center">
                        <h5>Nächste Abbuchung</h5>
                        <p class="lead">15.02.2025</p>
                        <div class="metric-value text-success">€3,175</div>
                        <span class="badge bg-success">
                            <i class="fas fa-check"></i> Bereit
                        </span>
                    </div>
                </div>
            </div>
            
            <!-- Next Event -->
            <div class="col-md-4">
                <div class="dashboard-card">
                    <div class="card-header">
                        <i class="fas fa-calendar"></i> Nächstes Event
                    </div>
                    <div class="text-center">
                        <h5>{next_event.name if next_event else 'Fasching Party'}</h5>
                        <p>Sa, 08.02.2025 20:00</p>
                        <div class="progress" style="height: 25px;">
                            <div class="progress-bar bg-success" style="width: 40%">
                                45/120 Tickets
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Member Churn -->
        <div class="row mt-4">
            <div class="col-md-6">
                <div class="dashboard-card">
                    <div class="card-header">
                        <i class="fas fa-chart-line"></i> Mitglieder Quartalsübersicht
                    </div>
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Quartal</th>
                                <th class="text-success">Neu</th>
                                <th class="text-danger">Verloren</th>
                                <th>Netto</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>Q1 2025</td>
                                <td class="text-success">+12</td>
                                <td class="text-danger">-3</td>
                                <td class="text-success fw-bold">+9</td>
                            </tr>
                            <tr>
                                <td>Q4 2024</td>
                                <td class="text-success">+8</td>
                                <td class="text-danger">-5</td>
                                <td class="text-success fw-bold">+3</td>
                            </tr>
                            <tr>
                                <td>Q3 2024</td>
                                <td class="text-success">+15</td>
                                <td class="text-danger">-2</td>
                                <td class="text-success fw-bold">+13</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Social Media -->
            <div class="col-md-6">
                <div class="dashboard-card">
                    <div class="card-header">
                        <i class="fab fa-instagram"></i> Social Media
                    </div>
                    <div class="row text-center">
                        <div class="col-4">
                            <h4>892</h4>
                            <p>Follower</p>
                        </div>
                        <div class="col-4">
                            <h4>5.2%</h4>
                            <p>Engagement</p>
                        </div>
                        <div class="col-4">
                            <h4>Vor 2h</h4>
                            <p>Letzter Post</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Quick Actions -->
        <div class="text-center mt-5">
            <a href="/web#action=kulturhaus_membership_sepa.action_sepa_batch" class="btn btn-action">
                <i class="fas fa-euro-sign"></i> SEPA Batch erstellen
            </a>
            <a href="/web#model=res.partner&view_type=list" class="btn btn-action">
                <i class="fas fa-users"></i> Mitglieder verwalten
            </a>
            <a href="/web#model=event.event&view_type=list" class="btn btn-action">
                <i class="fas fa-calendar"></i> Events anzeigen
            </a>
        </div>
        
        <div class="text-center mt-3">
            <a href="/web" class="btn btn-secondary">
                <i class="fas fa-arrow-left"></i> Zurück zu Odoo
            </a>
        </div>
    </div>
</body>
</html>
        """
        
        return html