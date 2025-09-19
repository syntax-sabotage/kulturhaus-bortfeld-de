# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class CreateResolutionWizard(models.TransientModel):
    _name = 'create.resolution.wizard'
    _description = 'Create Board Resolution Wizard'

    # Wizard Steps
    step = fields.Selection([
        ('basic', 'Basic Information'),
        ('attendance', 'Attendance'),
        ('resolution', 'Resolution Text'),
        ('voting', 'Voting'),
        ('confirmation', 'Confirmation')
    ], string='Step', default='basic')

    # Step 1: Basic Information
    title = fields.Char('Title', required=True)
    description = fields.Text('Description')
    date = fields.Date('Resolution Date', required=True, default=fields.Date.today)
    project_id = fields.Many2one('project.project', string='Related Project')
    task_id = fields.Many2one('project.task', string='Related Task')

    # Step 2: Attendance
    board_members = fields.Many2many(
        'res.partner', 
        'wizard_board_members_rel', 
        'wizard_id', 
        'partner_id',
        string='All Board Members',
        domain=[('board_member', '=', True)],
        default=lambda self: self.env['res.partner'].search([('board_member', '=', True)])
    )
    present_members = fields.Many2many(
        'res.partner', 
        'wizard_present_members_rel', 
        'wizard_id', 
        'partner_id',
        string='Present Members',
        domain=[('board_member', '=', True)]
    )
    present_count = fields.Integer('Present Count', compute='_compute_present_count')
    total_board_members = fields.Integer('Total Board Members', compute='_compute_total_board_members')
    quorum_met = fields.Boolean('Quorum Met', compute='_compute_quorum_met')

    # Step 3: Resolution Text
    resolution_text = fields.Html('Resolution Text', required=True)

    # Step 4: Voting
    voting_mode = fields.Selection([
        ('open', 'Open Voting'),
        ('secret', 'Secret Voting')
    ], string='Voting Mode', default='open', required=True)
    
    # For secret voting
    votes_for = fields.Integer('Votes For', default=0)
    votes_against = fields.Integer('Votes Against', default=0)
    votes_abstain = fields.Integer('Votes Abstain', default=0)
    
    # For open voting
    votes_for_members = fields.Many2many(
        'res.partner', 
        'wizard_votes_for_rel', 
        'wizard_id', 
        'partner_id',
        string='Members Voted For'
    )
    votes_against_members = fields.Many2many(
        'res.partner', 
        'wizard_votes_against_rel', 
        'wizard_id', 
        'partner_id',
        string='Members Voted Against'
    )
    votes_abstain_members = fields.Many2many(
        'res.partner', 
        'wizard_votes_abstain_rel', 
        'wizard_id', 
        'partner_id',
        string='Members Abstained'
    )
    
    # Computed fields for voting
    total_votes = fields.Integer('Total Votes', compute='_compute_total_votes')
    result = fields.Selection([
        ('passed', 'Passed'),
        ('rejected', 'Rejected'),
        ('tie', 'Tie')
    ], string='Result', compute='_compute_result')

    @api.depends('present_members')
    def _compute_present_count(self):
        for wizard in self:
            wizard.present_count = len(wizard.present_members)

    def _compute_total_board_members(self):
        for wizard in self:
            wizard.total_board_members = len(wizard.board_members)

    @api.depends('present_count', 'total_board_members')
    def _compute_quorum_met(self):
        for wizard in self:
            if wizard.total_board_members > 0:
                wizard.quorum_met = wizard.present_count > (wizard.total_board_members / 2)
            else:
                wizard.quorum_met = False

    @api.depends('voting_mode', 'votes_for', 'votes_against', 'votes_abstain', 'votes_for_members', 'votes_against_members', 'votes_abstain_members')
    def _compute_total_votes(self):
        for wizard in self:
            if wizard.voting_mode == 'secret':
                wizard.total_votes = wizard.votes_for + wizard.votes_against + wizard.votes_abstain
            else:
                wizard.total_votes = len(wizard.votes_for_members) + len(wizard.votes_against_members) + len(wizard.votes_abstain_members)

    @api.depends('voting_mode', 'votes_for', 'votes_against', 'votes_for_members', 'votes_against_members')
    def _compute_result(self):
        for wizard in self:
            if wizard.voting_mode == 'secret':
                for_votes = wizard.votes_for
                against_votes = wizard.votes_against
            else:
                for_votes = len(wizard.votes_for_members)
                against_votes = len(wizard.votes_against_members)
            
            if for_votes > against_votes:
                wizard.result = 'passed'
            elif against_votes > for_votes:
                wizard.result = 'rejected'
            else:
                wizard.result = 'tie'

    @api.onchange('task_id')
    def _onchange_task_id(self):
        if self.task_id:
            self.project_id = self.task_id.project_id

    @api.onchange('voting_mode')
    def _onchange_voting_mode(self):
        """Clear voting data when changing mode"""
        if self.voting_mode == 'secret':
            self.votes_for_members = [(5, 0, 0)]
            self.votes_against_members = [(5, 0, 0)]
            self.votes_abstain_members = [(5, 0, 0)]
        else:
            self.votes_for = 0
            self.votes_against = 0
            self.votes_abstain = 0

    def action_next_step(self):
        """Move to next step"""
        if self.step == 'basic':
            self._validate_basic_step()
            self.step = 'attendance'
        elif self.step == 'attendance':
            self._validate_attendance_step()
            self.step = 'resolution'
        elif self.step == 'resolution':
            self._validate_resolution_step()
            self.step = 'voting'
        elif self.step == 'voting':
            self._validate_voting_step()
            self.step = 'confirmation'
        
        return self._return_wizard()

    def action_previous_step(self):
        """Move to previous step"""
        if self.step == 'confirmation':
            self.step = 'voting'
        elif self.step == 'voting':
            self.step = 'resolution'
        elif self.step == 'resolution':
            self.step = 'attendance'
        elif self.step == 'attendance':
            self.step = 'basic'
        
        return self._return_wizard()

    def action_create_resolution(self):
        """Create the board resolution"""
        self._validate_all_steps()
        
        # Prepare values
        vals = {
            'title': self.title,
            'description': self.description,
            'date': self.date,
            'resolution_text': self.resolution_text,
            'project_id': self.project_id.id if self.project_id else False,
            'task_id': self.task_id.id if self.task_id else False,
            'present_members': [(6, 0, self.present_members.ids)],
            'voting_mode': self.voting_mode,
        }
        
        # Add voting data
        if self.voting_mode == 'secret':
            vals.update({
                'votes_for': self.votes_for,
                'votes_against': self.votes_against,
                'votes_abstain': self.votes_abstain,
            })
        else:
            vals.update({
                'votes_for': len(self.votes_for_members),
                'votes_against': len(self.votes_against_members),
                'votes_abstain': len(self.votes_abstain_members),
                'votes_for_members': [(6, 0, self.votes_for_members.ids)],
                'votes_against_members': [(6, 0, self.votes_against_members.ids)],
                'votes_abstain_members': [(6, 0, self.votes_abstain_members.ids)],
            })
        
        # Create resolution
        resolution = self.env['board.resolution'].create(vals)
        
        # Move to voted state if votes were recorded
        if self.total_votes > 0:
            resolution.action_vote()
        
        return {
            'name': _('Board Resolution'),
            'type': 'ir.actions.act_window',
            'res_model': 'board.resolution',
            'res_id': resolution.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _validate_basic_step(self):
        """Validate basic information step"""
        if not self.title:
            raise ValidationError(_('Title is required.'))
        if not self.date:
            raise ValidationError(_('Date is required.'))

    def _validate_attendance_step(self):
        """Validate attendance step"""
        if not self.present_members:
            raise ValidationError(_('At least one board member must be present.'))
        if not self.quorum_met:
            raise ValidationError(_('Quorum not met. At least %d board members must be present.') % 
                                (self.total_board_members // 2 + 1))

    def _validate_resolution_step(self):
        """Validate resolution text step"""
        if not self.resolution_text or self.resolution_text.strip() == '<p><br></p>':
            raise ValidationError(_('Resolution text is required.'))

    def _validate_voting_step(self):
        """Validate voting step"""
        if self.voting_mode == 'secret':
            if self.total_votes > self.present_count:
                raise ValidationError(_('Total votes (%d) cannot exceed present members (%d).') % 
                                    (self.total_votes, self.present_count))
            if self.total_votes == 0:
                raise ValidationError(_('Please record at least one vote.'))
        else:
            # Check for overlapping votes
            for_against = self.votes_for_members & self.votes_against_members
            for_abstain = self.votes_for_members & self.votes_abstain_members
            against_abstain = self.votes_against_members & self.votes_abstain_members
            
            if for_against or for_abstain or against_abstain:
                raise ValidationError(_('Members cannot vote multiple ways.'))
            
            # Check that voting members are present
            all_voting_members = self.votes_for_members | self.votes_against_members | self.votes_abstain_members
            if all_voting_members and not all_voting_members <= self.present_members:
                raise ValidationError(_('Only present members can vote.'))
            
            # Warn if not all members voted (but don't block)
            if len(all_voting_members) < self.present_count:
                # This is just a warning, not a hard error - resolution can still be created in draft
                pass

    def _validate_all_steps(self):
        """Validate all steps before creating resolution"""
        self._validate_basic_step()
        self._validate_attendance_step()
        self._validate_resolution_step()
        self._validate_voting_step()

    def _return_wizard(self):
        """Return wizard action to stay on current form"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'create.resolution.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }