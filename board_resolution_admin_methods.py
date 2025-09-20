    def action_reset_to_draft(self):
        """Reset to draft (for corrections)"""
        if self.is_approved and not self.env.user.has_group('kulturhaus_board_resolutions.group_board_resolution_admin'):
            raise UserError(_('Only Beschluss Administrators can reset approved resolutions to draft.'))
        
        self.write({
            'state': 'draft',
            'approved_by': False,
            'approved_date': False
        })
        self.message_post(body=_('Resolution reset to draft by %s.') % self.env.user.name)

    def action_admin_reset_to_draft(self):
        """Admin action to reset any resolution to draft"""
        if not self.env.user.has_group('kulturhaus_board_resolutions.group_board_resolution_admin'):
            raise UserError(_('Only Beschluss Administrators can use this action.'))
        
        self.write({
            'state': 'draft',
            'approved_by': False,
            'approved_date': False,
            'votes_for': 0,
            'votes_against': 0,
            'votes_abstain': 0,
            'votes_for_members': [(5, 0, 0)],
            'votes_against_members': [(5, 0, 0)],
            'votes_abstain_members': [(5, 0, 0)]
        })
        self.message_post(body=_('Resolution administratively reset to draft by %s.') % self.env.user.name)
    
    def action_admin_delete(self):
        """Admin action to delete resolution"""
        if not self.env.user.has_group('kulturhaus_board_resolutions.group_board_resolution_admin'):
            raise UserError(_('Only Beschluss Administrators can delete resolutions.'))
        
        # Log deletion before actually deleting
        for resolution in self:
            resolution.message_post(body=_('Resolution scheduled for deletion by %s.') % self.env.user.name)
        
        return self.unlink()
    
    def action_print_report(self):
        """Print PDF report"""
        return self.env.ref('kulturhaus_board_resolutions.action_report_board_resolution').report_action(self)

    def write(self, vals):
        """Prevent editing of approved resolutions (except for admins)"""
        for resolution in self:
            if resolution.is_approved and any(key not in ('state',) for key in vals.keys()):
                if not self.env.user.has_group('kulturhaus_board_resolutions.group_board_resolution_admin'):
                    raise UserError(_('Cannot modify approved resolutions. Only Beschluss Administrators can edit approved resolutions.'))
        return super(BoardResolution, self).write(vals)

    def unlink(self):
        """Prevent deletion of approved resolutions (except for admins)"""
        if any(resolution.is_approved for resolution in self):
            if not self.env.user.has_group('kulturhaus_board_resolutions.group_board_resolution_admin'):
                raise UserError(_('Cannot delete approved resolutions. Only Beschluss Administrators can delete them.'))
        return super(BoardResolution, self).unlink()