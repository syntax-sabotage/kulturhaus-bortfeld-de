# -*- coding: utf-8 -*-
"""
Alternative approach using mail.alias for group notifications
This can be used instead of or alongside the main implementation
"""
from odoo import models, fields, api, _


class MailAlias(models.Model):
    _inherit = 'mail.alias'
    
    is_group_alias = fields.Boolean(
        string='Group Alias',
        help='This alias represents a group for notifications'
    )
    
    group_partner_ids = fields.Many2many(
        'res.partner',
        string='Group Members',
        help='Partners to notify when this alias is used'
    )


class ProjectProject(models.Model):
    _inherit = 'project.project'
    
    all_followers_alias_id = fields.Many2one(
        'mail.alias',
        string='All Followers Alias',
        help='Email alias that notifies all project followers'
    )
    
    board_members_alias_id = fields.Many2one(
        'mail.alias', 
        string='Board Members Alias',
        help='Email alias that notifies board members'
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        """Create mail aliases for group notifications"""
        projects = super().create(vals_list)
        
        for project in projects:
            # Create @all alias
            all_alias = self.env['mail.alias'].create({
                'alias_name': f'all-{project.id}',
                'alias_model_id': self.env.ref('project.model_project_task').id,
                'alias_defaults': {'project_id': project.id},
                'is_group_alias': True,
            })
            project.all_followers_alias_id = all_alias
            
            # Create @vorstand alias  
            board_alias = self.env['mail.alias'].create({
                'alias_name': f'board-{project.id}',
                'alias_model_id': self.env.ref('project.model_project_task').id,
                'alias_defaults': {'project_id': project.id},
                'is_group_alias': True,
            })
            project.board_members_alias_id = board_alias
            
        return projects