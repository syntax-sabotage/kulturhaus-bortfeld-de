# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta


class BoardResolution(models.Model):
    _name = 'board.resolution'
    _description = _('Board Resolution')
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, name desc'
    _rec_name = 'name'

    # Basic Information
    name = fields.Char(
        _('Resolution Number'), 
        required=True, 
        copy=False, 
        readonly=True, 
        default=lambda self: _('New'),
        tracking=True
    )
    title = fields.Char(_('Title'), required=True, tracking=True)
    description = fields.Text(_('Description'))
    date = fields.Date(_('Resolution Date'), required=True, default=fields.Date.today, tracking=True)
    resolution_text = fields.Html(_('Resolution Text'), required=True)
    
    # Meeting Type Configuration
    meeting_type_id = fields.Many2one(
        'board.meeting.type',
        string=_('Meeting Type'),
        required=True,
        default=lambda self: self._get_default_meeting_type(),
        tracking=True
    )
    
    # Related Meeting Type Fields (for display in views)
    meeting_quorum_type = fields.Selection(related='meeting_type_id.quorum_type', readonly=True)
    meeting_quorum_percentage = fields.Float(related='meeting_type_id.quorum_percentage', readonly=True)
    meeting_quorum_fixed = fields.Integer(related='meeting_type_id.quorum_fixed', readonly=True)
    meeting_voting_majority = fields.Selection(related='meeting_type_id.voting_majority', readonly=True)
    meeting_voting_majority_custom = fields.Float(related='meeting_type_id.voting_majority_custom', readonly=True)
    
    # Voting Information
    present_members = fields.Many2many(
        'res.partner', 
        'resolution_present_members_rel', 
        'resolution_id', 
        'partner_id',
        string=_('Present Members'),
        domain=[('board_member', '=', True)],
        tracking=True
    )
    present_count = fields.Integer(_('Present Count'), compute='_compute_present_count', store=True)
    total_board_members = fields.Integer(_('Total Board Members'), compute='_compute_total_board_members')
    quorum_met = fields.Boolean(_('Quorum Met'), compute='_compute_quorum_met', store=True)
    
    voting_mode = fields.Selection([
        ('open', _('Open Voting')),
        ('secret', _('Secret Voting'))
    ], string=_('Voting Mode'), default='open', required=True)
    
    votes_for = fields.Integer(_('Votes For'), default=0)
    votes_against = fields.Integer(_('Votes Against'), default=0)
    votes_abstain = fields.Integer(_('Votes Abstain'), default=0)
    total_votes = fields.Integer(_('Total Votes'), compute='_compute_total_votes', store=True)
    
    # Voting Details (for open voting)
    votes_for_members = fields.Many2many(
        'res.partner', 
        'resolution_votes_for_rel', 
        'resolution_id', 
        'partner_id',
        string=_('Members Voted For')
    )
    votes_against_members = fields.Many2many(
        'res.partner', 
        'resolution_votes_against_rel', 
        'resolution_id', 
        'partner_id',
        string=_('Members Voted Against')
    )
    votes_abstain_members = fields.Many2many(
        'res.partner', 
        'resolution_votes_abstain_rel', 
        'resolution_id', 
        'partner_id',
        string=_('Members Abstained')
    )
    
    # Project/Task Integration
    project_id = fields.Many2one('project.project', string=_('Related Project'))
    task_id = fields.Many2one('project.task', string=_('Related Task'))
    
    # Workflow
    state = fields.Selection([
        ('draft', _('Draft')),
        ('voted', _('Voted')),
        ('to_approve', _('To Approve')),
        ('approved', _('Approved')),
        ('archived', _('Archived'))
    ], string=_('State'), default='draft', required=True, tracking=True)
    
    # Approval
    approved_by = fields.Many2one('res.users', string=_('Approved By'), readonly=True)
    approved_date = fields.Datetime(_('Approved Date'), readonly=True)
    
    # Computed Fields
    is_approved = fields.Boolean(_('Is Approved'), compute='_compute_is_approved', store=True)
    can_edit = fields.Boolean(_('Can Edit'), compute='_compute_can_edit')
    result = fields.Selection([
        ('passed', _('Passed')),
        ('rejected', _('Rejected')),
        ('tie', _('Tie'))
    ], string=_('Result'), compute='_compute_result', store=True)

    @api.depends('present_members')
    def _compute_present_count(self):
        for resolution in self:
            resolution.present_count = len(resolution.present_members)

    @api.depends('present_count')
    def _compute_total_board_members(self):
        for resolution in self:
            resolution.total_board_members = self.env['res.partner'].search_count([('board_member', '=', True)])

    @api.depends('present_count', 'total_board_members', 'meeting_type_id')
    def _compute_quorum_met(self):
        for resolution in self:
            if resolution.total_board_members > 0 and resolution.meeting_type_id:
                required_quorum = resolution.meeting_type_id.calculate_quorum(resolution.total_board_members)
                resolution.quorum_met = resolution.present_count >= required_quorum
            elif resolution.total_board_members > 0:
                # Fallback to simple majority
                resolution.quorum_met = resolution.present_count > (resolution.total_board_members / 2)
            else:
                resolution.quorum_met = False

    @api.depends('votes_for', 'votes_against', 'votes_abstain')
    def _compute_total_votes(self):
        for resolution in self:
            resolution.total_votes = resolution.votes_for + resolution.votes_against + resolution.votes_abstain

    @api.depends('votes_for', 'votes_against', 'meeting_type_id')
    def _compute_result(self):
        for resolution in self:
            if resolution.meeting_type_id:
                votes_cast = resolution.votes_for + resolution.votes_against
                majority_needed = resolution.meeting_type_id.calculate_majority_needed(votes_cast)
                if resolution.votes_for >= majority_needed:
                    resolution.result = 'passed'
                elif resolution.votes_against > (votes_cast - majority_needed):
                    resolution.result = 'rejected'
                else:
                    resolution.result = 'tie'
            else:
                # Fallback to simple majority
                if resolution.votes_for > resolution.votes_against:
                    resolution.result = 'passed'
                elif resolution.votes_against > resolution.votes_for:
                    resolution.result = 'rejected'
                else:
                    resolution.result = 'tie'

    @api.depends('state')
    def _compute_is_approved(self):
        for resolution in self:
            resolution.is_approved = resolution.state in ('approved', 'archived')

    @api.depends('state', 'approved_by')
    def _compute_can_edit(self):
        for resolution in self:
            resolution.can_edit = resolution.state in ('draft', 'voted') and not resolution.is_approved

    @api.model
    def _get_default_meeting_type(self):
        """Get default meeting type from settings or first available"""
        default = self.env['ir.config_parameter'].sudo().get_param('kulturhaus_board_resolutions.default_meeting_type_id')
        if default:
            return int(default)
        return self.env['board.meeting.type'].search([], limit=1).id
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('board.resolution.sequence') or _('New')
        return super(BoardResolution, self).create(vals_list)

    @api.constrains('present_count', 'meeting_type_id')
    def _check_quorum(self):
        for resolution in self:
            if resolution.state not in ('draft',) and not resolution.quorum_met:
                if resolution.meeting_type_id:
                    required = resolution.meeting_type_id.calculate_quorum(resolution.total_board_members)
                    raise ValidationError(_('Quorum not met for %s. At least %d board members must be present.') % 
                                        (resolution.meeting_type_id.name, required))
                else:
                    raise ValidationError(_('Quorum not met. At least %d board members must be present.') % 
                                        (resolution.total_board_members // 2 + 1))

    @api.constrains('votes_for', 'votes_against', 'votes_abstain', 'present_count')
    def _check_vote_count(self):
        for resolution in self:
            if resolution.state in ('voted', 'to_approve', 'approved') and resolution.total_votes != resolution.present_count:
                raise ValidationError(_('Total votes (%d) must equal present members (%d).') % 
                                    (resolution.total_votes, resolution.present_count))

    @api.constrains('votes_for_members', 'votes_against_members', 'votes_abstain_members', 'present_members')
    def _check_voting_members(self):
        for resolution in self:
            if resolution.voting_mode == 'open' and resolution.state in ('voted', 'to_approve', 'approved'):
                all_voting_members = resolution.votes_for_members | resolution.votes_against_members | resolution.votes_abstain_members
                if set(all_voting_members.ids) != set(resolution.present_members.ids):
                    raise ValidationError(_('All present members must vote and can only vote once.'))

    def action_vote(self):
        """Move to voted state"""
        if not self.quorum_met:
            raise UserError(_('Cannot vote without quorum. At least %d members must be present.') % 
                          (self.total_board_members // 2 + 1))
        
        if self.voting_mode == 'open' and self.total_votes == 0:
            raise UserError(_('Please record the votes before marking as voted.'))
        
        self.state = 'voted'
        self.message_post(body=_('Resolution voted on.'))

    def action_submit_approval(self):
        """Move to approval state and create activity for secretary"""
        if self.state != 'voted':
            raise UserError(_('Resolution must be voted on before submitting for approval.'))
        
        self.state = 'to_approve'
        
        # Create activity for secretary
        secretary_group = self.env.ref('kulturhaus_board_resolutions.group_board_secretary', raise_if_not_found=False)
        if secretary_group:
            secretary_users = secretary_group.users
            if secretary_users:
                self.activity_schedule(
                    'kulturhaus_board_resolutions.mail_activity_data_resolution_approval',
                    date_deadline=fields.Date.today() + timedelta(days=7),
                    user_id=secretary_users[0].id,
                    summary=_('Board resolution approval required'),
                    note=_('Please review and approve board resolution: %s') % self.title
                )
        
        self.message_post(body=_('Resolution submitted for secretary approval.'))

    def action_approve(self):
        """Approve resolution (secretary only)"""
        if not self.env.user.has_group('kulturhaus_board_resolutions.group_board_secretary'):
            raise UserError(_('Only board secretaries can approve resolutions.'))
        
        if self.state != 'to_approve':
            raise UserError(_('Resolution must be in "To Approve" state.'))
        
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approved_date': fields.Datetime.now()
        })
        
        # Mark related activity as done
        activities = self.activity_ids.filtered(
            lambda a: a.activity_type_id.name == 'Resolution Approval' and a.user_id == self.env.user
        )
        activities.action_done()
        
        self.message_post(body=_('Resolution approved by %s.') % self.env.user.name)

    def action_archive(self):
        """Archive resolution"""
        if self.state != 'approved':
            raise UserError(_('Only approved resolutions can be archived.'))
        
        self.state = 'archived'
        self.message_post(body=_('Resolution archived.'))

    def action_reset_to_draft(self):
        """Reset to draft (for corrections)"""
        if self.is_approved:
            raise UserError(_('Cannot reset approved resolutions to draft.'))
        
        self.state = 'draft'
        self.message_post(body=_('Resolution reset to draft.'))
    
    def action_print_report(self):
        """Print PDF report"""
        return self.env.ref('kulturhaus_board_resolutions.action_report_board_resolution').report_action(self)

    def write(self, vals):
        """Prevent editing of approved resolutions"""
        for resolution in self:
            if resolution.is_approved and any(key not in ('state',) for key in vals.keys()):
                raise UserError(_('Cannot modify approved resolutions.'))
        return super(BoardResolution, self).write(vals)

    def unlink(self):
        """Prevent deletion of approved resolutions"""
        if any(resolution.is_approved for resolution in self):
            raise UserError(_('Cannot delete approved resolutions.'))
        return super(BoardResolution, self).unlink()