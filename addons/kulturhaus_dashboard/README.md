# Kulturhaus Dashboard

A mobile-optimized, card-based dashboard module for Odoo 18 that provides simplified navigation for non-technical users.

## Features

- **Card-Based Interface**: Simple, intuitive navigation cards
- **Mobile-First Design**: Optimized for iOS/Android tablets and phones  
- **KPI Widgets**: Quick overview with 3 key performance indicators
- **User Preferences**: Optional dashboard that users can enable/disable
- **Multiple Themes**: 3 professional color themes (Blue, Green, Orange)
- **Non-Invasive**: Preserves all standard Odoo functionality

## Target Users

- Board members and volunteers
- Event coordinators
- Non-technical users requiring simplified navigation
- Mobile and tablet users

## Installation

1. Copy the module to your Odoo addons directory
2. Update the module list
3. Install "Kulturhaus Dashboard" from the Apps menu
4. Users can enable the dashboard in their user preferences

## Configuration

### For Users
1. Go to Preferences → Dashboard Preferences
2. Enable "Use Dashboard Home"
3. Choose your preferred theme
4. The dashboard will replace your home screen

### For Administrators
1. Access "Dashboard Config" menu
2. Configure dashboard cards and permissions
3. Create custom cards for specific workflows
4. Manage user group access

## Default Cards

- **Events**: Veranstaltungen verwalten
- **Members**: Mitgliederverwaltung  
- **Projects**: Projektmanagement
- **Marketing**: Newsletter und Massenmailings
- **Finances**: Buchhaltung und Berichte
- **Reports**: Reports und Auswertungen
- **Website**: Link zu kulturhaus-bortfeld.de
- **Settings**: System-Einstellungen (Admin only)

## KPI Indicators

1. **Events This Month**: Count of scheduled events
2. **New Members**: Members added in last 30 days
3. **Active Projects**: Projects with "in progress" status

## Technical Requirements

- Odoo 18 Community Edition
- Python 3.11+
- PostgreSQL 16
- Modern web browser (Chrome, Safari, Firefox, Edge)

## Browser Support

- iOS Safari 15+
- Chrome Mobile/Desktop 90+
- Firefox 88+
- Edge 90+

## Development

### Module Structure
```
kulturhaus_dashboard/
├── models/          # Data models
├── views/           # XML views
├── controllers/     # HTTP controllers
├── static/          # CSS, JS, assets
├── data/           # Default data
├── security/       # Access rights
└── i18n/           # Translations
```

### Key Files
- `models/res_users.py` - User preference extension
- `models/dashboard_card.py` - Card definition model
- `controllers/dashboard.py` - API endpoints
- `static/src/js/dashboard.js` - Frontend component
- `static/src/css/dashboard.css` - Responsive styles

## License

LGPL-3

## Support

For issues and feature requests, please contact the development team or create an issue in the project repository.

## Changelog

### Version 1.0.0
- Initial release
- Basic dashboard with card navigation
- Mobile-responsive design
- User preferences integration
- 3 theme options
- KPI widgets
- Default card configuration