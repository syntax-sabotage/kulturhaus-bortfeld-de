# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MeetingType(models.Model):
    _name = 'board.meeting.type'
    _description = _('Board Meeting Type')
    _order = 'sequence, name'
    
    name = fields.Char(_('Meeting Type'), required=True, translate=True)
    sequence = fields.Integer(_('Sequence'), default=10)
    active = fields.Boolean(_('Active'), default=True)
    
    # Quorum Configuration
    quorum_type = fields.Selection([
        ('percentage', _('Percentage of Members')),
        ('fixed', _('Fixed Number')),
        ('half_plus_one', _('Half + 1')),
        ('two_thirds', _('Two Thirds')),
        ('all', _('All Members')),
        ('custom', _('Custom Formula'))
    ], string=_('Quorum Type'), required=True, default='half_plus_one')
    
    quorum_percentage = fields.Float(
        _('Quorum Percentage'), 
        default=50,
        help=_('Percentage of members required for quorum (when type is Percentage)')
    )
    
    quorum_fixed = fields.Integer(
        _('Fixed Quorum Number'),
        default=3,
        help=_('Fixed number of members required (when type is Fixed)')
    )
    
    quorum_custom_formula = fields.Char(
        _('Custom Formula'),
        help=_('Python expression. Available variables: total_members')
    )
    
    # Voting Configuration
    voting_majority = fields.Selection([
        ('simple', _('Simple Majority (>50%)')),
        ('two_thirds', _('Two Thirds Majority')),
        ('three_quarters', _('Three Quarters Majority')),
        ('unanimous', _('Unanimous')),
        ('custom', _('Custom'))
    ], string=_('Required Majority'), default='simple', required=True)
    
    voting_majority_custom = fields.Float(
        _('Custom Majority Percentage'),
        default=60,
        help=_('Required percentage for custom majority')
    )
    
    allow_proxy_voting = fields.Boolean(_('Allow Proxy Voting'), default=False)
    allow_secret_ballot = fields.Boolean(_('Allow Secret Ballot'), default=True)
    allow_open_ballot = fields.Boolean(_('Allow Open Ballot'), default=True)
    
    # Display Configuration
    description = fields.Text(_('Description'), translate=True)
    color = fields.Integer(_('Color Index'))
    
    @api.constrains('quorum_percentage')
    def _check_quorum_percentage(self):
        for record in self:
            if record.quorum_type == 'percentage':
                if record.quorum_percentage <= 0 or record.quorum_percentage > 100:
                    raise ValidationError(_('Quorum percentage must be between 0 and 100'))
    
    @api.constrains('quorum_fixed')
    def _check_quorum_fixed(self):
        for record in self:
            if record.quorum_type == 'fixed' and record.quorum_fixed <= 0:
                raise ValidationError(_('Fixed quorum must be greater than 0'))
    
    def calculate_quorum(self, total_members):
        """Calculate required quorum based on configuration"""
        self.ensure_one()
        
        if self.quorum_type == 'percentage':
            return max(1, int((total_members * self.quorum_percentage / 100) + 0.5))
        elif self.quorum_type == 'fixed':
            return min(self.quorum_fixed, total_members)
        elif self.quorum_type == 'half_plus_one':
            return (total_members // 2) + 1
        elif self.quorum_type == 'two_thirds':
            return max(1, int((total_members * 2 / 3) + 0.5))
        elif self.quorum_type == 'all':
            return total_members
        elif self.quorum_type == 'custom' and self.quorum_custom_formula:
            try:
                # Safe evaluation with limited context
                return int(eval(self.quorum_custom_formula, {'total_members': total_members}))
            except:
                return (total_members // 2) + 1  # Fallback to half+1
        
        return (total_members // 2) + 1  # Default fallback
    
    def calculate_majority_needed(self, votes_cast):
        """Calculate votes needed for majority based on configuration"""
        self.ensure_one()
        
        if votes_cast <= 0:
            return 1
            
        if self.voting_majority == 'simple':
            return (votes_cast // 2) + 1
        elif self.voting_majority == 'two_thirds':
            return max(1, int((votes_cast * 2 / 3) + 0.5))
        elif self.voting_majority == 'three_quarters':
            return max(1, int((votes_cast * 3 / 4) + 0.5))
        elif self.voting_majority == 'unanimous':
            return votes_cast
        elif self.voting_majority == 'custom':
            return max(1, int((votes_cast * self.voting_majority_custom / 100) + 0.5))
        
        return (votes_cast // 2) + 1  # Default to simple majority


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    default_meeting_type_id = fields.Many2one(
        'board.meeting.type',
        string=_('Default Meeting Type'),
        config_parameter='kulturhaus_board_resolutions.default_meeting_type_id'
    )