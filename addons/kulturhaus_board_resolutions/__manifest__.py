# -*- coding: utf-8 -*-
{
    'name': 'Kulturhaus Board Resolutions',
    'version': '18.2.1.0.0',
    'category': 'Project',
    'summary': 'Board resolution management for Kulturhaus Bortfeld e.V.',
    'description': """
Board Resolution Management
===========================

This module provides comprehensive board resolution management for German cultural associations:

* Auto-numbered resolutions (VB-YYYY-NNN format)
* Complete workflow: draft → voted → to_approve → approved → archived
* Project and task integration
* Multi-step creation wizard with attendance tracking
* Voting management (open/secret modes)
* Approval workflow with secretary activities
* PDF export functionality
* German localization
* Quorum validation

Perfect for managing Vorstandsbeschlüsse in compliance with German association law.
    """,
    'author': 'IdeaWise Group',
    'website': 'https://www.ideawisegroup.com',
    'depends': [
        'base',
        'project',
        'mail',
        'web',
    ],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/sequence.xml',
        'data/demo_board_members.xml',
        
        # Views
        'views/res_partner_views.xml',
        'views/board_resolution_views.xml',
        'views/project_views.xml',
        'wizards/wizard_views.xml',
        'views/menu.xml',
        
        # Reports
        'report/board_resolution_report.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}