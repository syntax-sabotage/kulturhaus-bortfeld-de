#!/usr/bin/env python3
import sys

# Read the file
with open('/opt/odoo18/odoo/addons/kulturhaus_board_resolutions/models/board_resolution.py', 'r') as f:
    lines = f.readlines()

# Find where to insert the new methods (before the existing action_reset_to_draft)
insert_index = None
for i, line in enumerate(lines):
    if 'def action_reset_to_draft(self):' in line:
        insert_index = i
        break

if insert_index:
    # Insert the admin methods before action_reset_to_draft
    admin_methods = '''
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
        
        for resolution in self:
            resolution.message_post(body=_('Resolution scheduled for deletion by %s.') % self.env.user.name)
        
        return self.unlink()

'''
    lines.insert(insert_index, admin_methods)
    
    # Also update the existing action_reset_to_draft method
    for i in range(insert_index + 1, len(lines)):
        if 'def action_reset_to_draft(self):' in lines[i]:
            # Update the method
            j = i + 2  # Skip the docstring line
            if 'if self.is_approved:' in lines[j]:
                lines[j] = "        if self.is_approved and not self.env.user.has_group('kulturhaus_board_resolutions.group_board_resolution_admin'):\n"
                lines[j+1] = "            raise UserError(_('Only Beschluss Administrators can reset approved resolutions to draft.'))\n"
            break
    
    # Update the write method to allow admin edits
    for i, line in enumerate(lines):
        if 'def write(self, vals):' in line:
            for j in range(i, min(i+10, len(lines))):
                if 'raise UserError' in lines[j] and 'Cannot modify approved' in lines[j]:
                    lines[j] = "                if not self.env.user.has_group('kulturhaus_board_resolutions.group_board_resolution_admin'):\n"
                    lines.insert(j+1, "                    raise UserError(_('Cannot modify approved resolutions. Only Beschluss Administrators can edit approved resolutions.'))\n")
                    break
            break
    
    # Update the unlink method to allow admin deletes
    for i, line in enumerate(lines):
        if 'def unlink(self):' in line:
            for j in range(i, min(i+10, len(lines))):
                if 'raise UserError' in lines[j] and 'Cannot delete approved' in lines[j]:
                    lines[j-1] = "        if any(resolution.is_approved for resolution in self):\n"
                    lines[j] = "            if not self.env.user.has_group('kulturhaus_board_resolutions.group_board_resolution_admin'):\n"
                    lines.insert(j+1, "                raise UserError(_('Cannot delete approved resolutions. Only Beschluss Administrators can delete them.'))\n")
                    break
            break

# Write the file back
with open('/opt/odoo18/odoo/addons/kulturhaus_board_resolutions/models/board_resolution.py', 'w') as f:
    f.writelines(lines)

print("Admin methods added successfully")