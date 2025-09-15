# -*- coding: utf-8 -*-
import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def post_init_hook(env):
    """
    Post-installation hook to set up SKR49 chart of accounts
    """
    _logger.info("Setting up SKR49 chart of accounts for Kulturhaus Bortfeld...")
    
    # Load the chart of accounts
    company = env.company
    
    # Check if chart already exists
    if not company.chart_template:
        chart_template = env['account.chart.template'].search([
            ('name', '=', 'SKR49 - Gemeinnützige Vereine')
        ], limit=1)
        
        if chart_template:
            _logger.info(f"Applying chart template: {chart_template.name}")
            chart_template.try_loading()
    
    _logger.info("SKR49 setup completed")