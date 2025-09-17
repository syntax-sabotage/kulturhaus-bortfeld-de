# Kulturhaus Calendar Subscription Module

## Overview

This Odoo 18 module allows users to generate secure subscription URLs for their calendars, enabling synchronization with external calendar applications like Apple Calendar, Google Calendar, Outlook, and others that support the iCal standard.

## Features

- **Secure Token-Based Authentication**: Each subscription uses a unique, cryptographically secure token
- **Read-Only Calendar Feeds**: Prevents accidental modifications from external apps
- **Flexible Privacy Settings**: Choose whether to include private events
- **Event Type Filtering**: Subscribe to specific calendar categories only
- **Configurable Time Range**: Control how far in the past/future to include events
- **Usage Tracking**: Monitor when and how often subscriptions are accessed
- **Multiple Subscriptions**: Create different feeds for different devices/purposes
- **Webcal Protocol Support**: Better refresh rates with compatible clients

## Installation

1. Install the required Python dependency:
   ```bash
   pip install icalendar
   ```

2. Copy the module to your Odoo addons directory:
   ```bash
   cp -r kulturhaus_calendar_subscription /path/to/odoo/addons/
   ```

3. Update the module list in Odoo (Apps → Update Apps List)

4. Install the module (search for "Kulturhaus Calendar Subscription")

## Usage

### Creating a Subscription

1. Go to **Calendar → Calendar Subscriptions → My Subscriptions**
2. Click **New** to create a subscription
3. Give it a descriptive name (e.g., "iPhone Calendar", "Work Laptop")
4. Configure your preferences:
   - **Include Private Events**: Whether to show events marked as private
   - **Event Types**: Filter by specific calendar categories (optional)
   - **Time Range**: How many days to include (past/future)
5. Save the subscription

### Adding to Your Calendar App

#### Apple Calendar (macOS/iOS)
1. Copy the subscription URL (HTTPS or webcal)
2. In Calendar app: File → New Calendar Subscription
3. Paste the URL and configure refresh settings

#### Google Calendar
1. Copy the HTTPS URL (not webcal)
2. In Google Calendar: Other calendars → From URL
3. Paste the URL (Note: Google refreshes slowly, typically every 3-12 hours)

#### Outlook
1. Copy the subscription URL
2. In Outlook: Add calendar → Subscribe from web
3. Paste the URL and set refresh interval

## Technical Details

### Security
- Tokens are generated using Python's `secrets` module (cryptographically secure)
- Tokens are stored as SHA-256 hashes in the database
- Each user can only see and manage their own subscriptions
- Public endpoint validates tokens without exposing user credentials

### Performance
- Implements HTTP caching headers (ETag, Last-Modified)
- Suggests refresh intervals based on client User-Agent
- Limits event range to prevent large responses
- Database queries are optimized with proper indexes

### Compatibility
- Fully compatible with Odoo 18
- Uses `<list>` tags instead of deprecated `<tree>` tags
- Implements proper timezone handling for international use
- Follows iCalendar RFC 5545 standard

## Troubleshooting

### Module Not Installing
- Ensure `icalendar` Python package is installed
- Check Odoo logs for any import errors
- Verify the module is in the correct addons path

### Calendar Not Updating
- Different calendar apps have different refresh rates
- Apple Calendar: Can be set to refresh every 15 minutes
- Google Calendar: Updates slowly (3-12 hours)
- Try using webcal:// URLs for better refresh rates

### Events Missing
- Check the time range settings in your subscription
- Verify event type filters aren't too restrictive
- Ensure you have permission to view the events in Odoo

## Development

The module is structured as follows:
- `models/`: Token management and user extensions
- `controllers/`: iCal feed generation endpoint
- `views/`: User interface definitions
- `security/`: Access controls and rules
- `static/`: JavaScript enhancements

## License

LGPL-3