# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    resolution_ids = fields.One2many(
        'board.resolution',
        'project_id',
        string='Board Resolutions',
        help='Board resolutions related to this project.'
    )
    
    resolution_count = fields.Integer(
        'Resolutions Count',
        compute='_compute_resolution_count',
        help='Number of board resolutions for this project.'
    )

    @api.depends('resolution_ids')
    def _compute_resolution_count(self):
        for project in self:
            project.resolution_count = len(project.resolution_ids)

    def action_create_resolution(self):
        """Open wizard to create a new board resolution for this project"""
        return {
            'name': 'Create Board Resolution',
            'type': 'ir.actions.act_window',
            'res_model': 'create.resolution.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_project_id': self.id,
                'default_title': f'Resolution for Project: {self.name}',
            }
        }

    def action_view_resolutions(self):
        """View all resolutions for this project"""
        action = self.env["ir.actions.actions"]._for_xml_id("kulturhaus_board_resolutions.action_board_resolution")
        action['domain'] = [('project_id', '=', self.id)]
        action['context'] = {'default_project_id': self.id}
        return action


class ProjectTask(models.Model):
    _inherit = 'project.task'

    resolution_ids = fields.One2many(
        'board.resolution',
        'task_id',
        string='Board Resolutions',
        help='Board resolutions related to this task.'
    )
    
    resolution_count = fields.Integer(
        'Resolutions Count',
        compute='_compute_resolution_count',
        help='Number of board resolutions for this task.'
    )

    @api.depends('resolution_ids')
    def _compute_resolution_count(self):
        for task in self:
            task.resolution_count = len(task.resolution_ids)

    def action_create_resolution(self):
        """Open wizard to create a new board resolution for this task"""
        return {
            'name': 'Create Board Resolution',
            'type': 'ir.actions.act_window',
            'res_model': 'create.resolution.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_task_id': self.id,
                'default_project_id': self.project_id.id,
                'default_title': f'Resolution for Task: {self.name}',
            }
        }

    def action_view_resolutions(self):
        """View all resolutions for this task"""
        action = self.env["ir.actions.actions"]._for_xml_id("kulturhaus_board_resolutions.action_board_resolution")
        action['domain'] = [('task_id', '=', self.id)]
        action['context'] = {'default_task_id': self.id, 'default_project_id': self.project_id.id}
        return action