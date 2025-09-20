# Global Notification Preferences Module

## Overview
This module solves the notification overload problem by allowing users to configure their notification preferences GLOBALLY, rather than per-record. Users can set their preferences once and have them automatically applied to all records they follow.

## Key Features

### 1. User-Level Global Preferences
- Configure notification preferences in user profile
- Set preferences per model (e.g., different settings for Tasks vs Sales Orders)
- Quick toggle modes: Default, Important Only, Minimal, Custom

### 2. Automatic Application
- Preferences automatically applied when following new records
- Existing followers can bulk-apply their global preferences
- Override mechanism for specific records when needed

### 3. Notification Types Control
Users can control notifications for:
- **Messages**: New messages and comments
- **Notes**: Internal notes and logs
- **State Changes**: Stage/state transitions
- **Assignments**: When assigned to records

## Technical Implementation

### Architecture Benefits
✅ **Works WITH Odoo's architecture**: Uses existing mail.followers and subtype system
✅ **No core modifications**: Pure inheritance and extension
✅ **User empowerment**: Each user controls their own notification flood
✅ **Backwards compatible**: Existing per-record settings continue to work

### Key Models

#### `user.notification.preference`
Stores user's global preferences per model:
```python
- user_id: The user
- model_id: The Odoo model (e.g., project.task)
- subtype_ids: Which subtypes trigger notifications
- notify_on_*: Quick toggle fields
```

#### Extended `res.users`
Added fields:
- `global_notification_preference_ids`: User's preferences
- `notification_preference_mode`: Quick preset selection
- Master toggles for email/inbox/push

#### Extended `mail.followers`
- `use_global_preferences`: Toggle between global/custom
- Auto-applies global preferences on creation
- Override mechanism for specific records

## Installation & Configuration

### 1. Install the Module
```bash
# Add to addons path and update apps list
cd /path/to/odoo
./odoo-bin -u global_notification_preferences
```

### 2. User Configuration
Users can configure preferences via:
1. **Settings → Users → Edit User → Notifications tab**
2. **Discuss → Notification Preferences menu**
3. **Quick mode selection in user preferences**

### 3. Example Use Cases

#### Scenario 1: Developer wants only critical notifications
1. Set mode to "Important Only"
2. Automatically filters out internal notes across all models
3. Still receives direct messages and assignments

#### Scenario 2: Manager wants all task updates but minimal email updates
1. Set "Custom" mode
2. Configure project.task: All notifications
3. Configure account.move: Only state changes
4. Preferences apply automatically to new follows

#### Scenario 3: Team member overwhelmed by notifications
1. Set mode to "Minimal"
2. Only receives direct messages
3. Can override for specific critical projects

## Integration with Existing Code

### For Project Tasks (Example)
```python
# When user follows a task, global preferences automatically apply
task.message_subscribe(partner_ids=[user.partner_id.id])
# The module automatically applies user's task notification preferences

# Manual override for specific task
follower = task.message_follower_ids.filtered(
    lambda f: f.partner_id == user.partner_id
)
follower.use_global_preferences = False
follower.subtype_ids = custom_subtypes
```

### Creating Notifications with Respect to Preferences
```python
# The existing message_post respects follower subtypes
task.message_post(
    body="Task updated",
    subtype_xmlid='project.mt_task_stage',  # Only notifies users who want stage updates
)
```

## Migration from @all Mention Approach

### Why This is Better
1. **User Control**: Users decide their notification level, not senders
2. **No Spam**: No risk of notification bombing entire teams
3. **Scalable**: Works with 10 or 10,000 users
4. **Native Integration**: Uses Odoo's existing notification system

### Migration Path
1. Install global_notification_preferences module
2. Users configure their preferences
3. Remove @all mention functionality
4. Educate users on configuring their preferences

## API for Developers

### Get User's Preferences
```python
# Get subtypes user wants for a model
subtypes = user.get_notification_subtypes_for_model('project.task')

# Check if user wants specific notification type
pref = user.global_notification_preference_ids.filtered(
    lambda p: p.model_name == 'project.task'
)
if pref and pref.notify_on_notes:
    # User wants note notifications
```

### Apply Preferences Programmatically
```python
# Apply global preferences to existing follower
follower._apply_global_preferences()

# Bulk apply to all followers
self.env['mail.followers'].search([
    ('res_model', '=', 'project.task'),
    ('partner_id.user_ids', '!=', False)
]).action_apply_global_preferences()
```

## Performance Considerations
- Preferences cached at user level
- Minimal overhead on follower creation
- No impact on message sending performance
- Bulk operations optimized for large datasets

## Security
- Users can only modify their own preferences
- Portal users have read-only access
- Admin can configure defaults for new users

## Future Enhancements
1. **Time-based preferences**: Different settings for work hours vs off hours
2. **Urgency-based routing**: Critical notifications always get through
3. **Team templates**: Apply team-wide preference templates
4. **Analytics**: Track notification effectiveness and user engagement

## Conclusion
This module provides a sustainable, scalable solution to notification management in Odoo. By giving users control over their notification preferences globally, we eliminate notification spam while ensuring important information reaches the right people.