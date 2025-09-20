# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class BoardMeetingType(models.Model):
    _name = 'board.meeting.type'
    _description = 'Board Meeting Type'
    _order = 'sequence, name'

    name = fields.Char(string='Meeting Type', required=True, translate=True)
    code = fields.Char(string='Code', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    color = fields.Integer(string='Color Index')
    description = fields.Text(string='Description', translate=True)
    
    # Quorum Configuration
    quorum_type = fields.Selection([
        ('simple_majority', _('Simple Majority (>50%)')),
        ('two_thirds', _('Two Thirds')),
        ('custom_formula', _('Custom Formula')),
    ], string='Quorum Type', required=True, default='simple_majority')
    
    custom_formula = fields.Char(
        string='Custom Formula',
        help='Python expression using total_members variable. Example: total_members>1'
    )
    
    # Voting Configuration  
    required_majority = fields.Selection([
        ('simple', _('Simple Majority (>50%)')),
        ('two_thirds', _('Two Thirds')),
        ('unanimous', _('Unanimous')),
    ], string='Required Majority', default='simple', required=True)
    
    allow_proxy_voting = fields.Boolean(string='Allow Proxy Voting', default=False)
    allow_secret_ballot = fields.Boolean(string='Allow Secret Ballot', default=True)
    allow_open_ballot = fields.Boolean(string='Allow Open Ballot', default=True)
    
    def calculate_quorum(self, total_members):
        """Calculate required quorum based on type"""
        if self.quorum_type == 'simple_majority':
            return (total_members // 2) + 1
        elif self.quorum_type == 'two_thirds':
            import math
            return math.ceil(total_members * 2 / 3)
        elif self.quorum_type == 'custom_formula' and self.custom_formula:
            try:
                # Safe evaluation with only total_members variable
                return int(eval(self.custom_formula, {"__builtins__": {}}, {"total_members": total_members}))
            except:
                raise ValidationError(_("Invalid custom formula"))
        return (total_members // 2) + 1  # Default to simple majority
    
    def calculate_voting_majority(self, votes_for, votes_against, votes_abstain):
        """Calculate if voting passes based on majority type"""
        total_votes = votes_for + votes_against
        
        if total_votes == 0:
            return False
            
        if self.required_majority == 'simple':
            return votes_for > votes_against
        elif self.required_majority == 'two_thirds':
            return votes_for >= (total_votes * 2 / 3)
        elif self.required_majority == 'unanimous':
            return votes_against == 0 and votes_for > 0
        
        return False