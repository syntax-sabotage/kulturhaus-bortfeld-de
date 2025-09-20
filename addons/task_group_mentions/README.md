# Task Group Mentions Module

## Overview
This module enables `@all` and `@Vorstand` mentions in Odoo 18 project task chatter, allowing bulk notifications to groups of followers.

## Features

### 1. **@all Mention**
- Type `@all` in task chatter to notify ALL task followers
- Automatically detects and processes the mention
- Visual badge indicator in the message

### 2. **@Vorstand Mention**  
- Type `@Vorstand` to notify board members only
- Identifies board members by:
  - User group membership (configurable)
  - Partner function field containing "Vorstand"
  - Manual designation

### 3. **Manual Notification Buttons**
- "Notify All" button in task header
- "Notify Board" button for board members
- Smart button showing board member count

### 4. **Visual Feedback**
- Color-coded badges for group mentions
- Suggestion dropdown integration
- Real-time notification indicators

## Installation

1. Copy module to your addons directory:
```bash
cp -r task_group_mentions /path/to/odoo/addons/
```

2. Update apps list:
```bash
./odoo-bin -u base --stop-after-init
```

3. Install module:
   - Go to Apps
   - Search for "Task Group Mentions"
   - Click Install

## Configuration

### Setting Up Board Members

#### Option 1: Using User Groups
```python
# In your configuration module
board_group = self.env['res.groups'].create({
    'name': 'Board Members',
    'users': [(6, 0, board_user_ids)]
})
```

#### Option 2: Using Partner Function
```python
# Set function on partners
partner.function = 'Vorstand'
```

#### Option 3: Custom Logic
Override `_compute_board_members` in project.task

### Customizing Notification Groups

Edit `/models/project_task.py`:
```python
def _compute_board_members(self):
    # Your custom logic here
    pass
```

## Usage

### In Task Chatter

1. **Notify All Followers:**
   ```
   @all Please review the latest updates
   ```

2. **Notify Board Members:**
   ```
   @Vorstand Approval needed for budget increase
   ```

### Using Buttons
- Click "Notify All" to send immediate notification to all followers
- Click "Notify Board" to notify board members only

## Technical Details

### Architecture
- **Server-side:** Python models intercept message_post()
- **Client-side:** JavaScript patches Composer widget
- **Styling:** SCSS for visual indicators

### Key Components

1. **project_task.py**
   - Main logic for detecting mentions
   - Partner resolution
   - Notification dispatch

2. **chatter_composer.js**
   - UI enhancements
   - Autocomplete suggestions
   - Visual feedback

3. **mail_thread.py**
   - Global mail.thread extensions
   - Notification group handling

### Performance Considerations
- Caches board member computation
- Batch processes notifications
- Minimal database queries

## Troubleshooting

### Mentions Not Working
1. Check module is installed
2. Verify user has project.group_project_user
3. Check browser console for JS errors

### Board Members Not Detected
1. Verify partner function field
2. Check user group membership
3. Review _compute_board_members logic

### Notifications Not Sent
1. Check email configuration
2. Verify follower settings
3. Review server logs

## API Reference

### Python Methods

```python
# Extract group mentions from text
task._extract_group_mentions(body_html)

# Manually notify all followers
task.action_notify_all_followers()

# Manually notify board members
task.action_notify_board_members()
```

### JavaScript Functions

```javascript
// Check for group mentions
composer._highlightGroupMention(mentionType)

// Add special suggestions
composer.computeSuggestions()
```

## Extending the Module

### Adding New Group Types

1. Define new group in model:
```python
team_member_ids = fields.Many2many(...)
```

2. Add detection pattern:
```python
team_pattern = r'@team\b'
```

3. Update JavaScript suggestions:
```javascript
if ('team'.startsWith(searchTerm)) {
    // Add suggestion
}
```

## Security
- Respects existing follower permissions
- No privilege escalation
- Audit trail in chatter

## License
LGPL-3

## Support
Contact: admin@kulturhaus-bortfeld.de