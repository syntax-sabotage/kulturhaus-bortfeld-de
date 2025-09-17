# Kulturhaus Dashboard - Installation Guide

## Quick Installation for Odoo 18

### Prerequisites
- Odoo 18 Community Edition running
- PostgreSQL 16 database  
- Admin access to Odoo instance

### Installation Steps

1. **Copy Module to Server**
   ```bash
   # On the Odoo server
   ssh kulturhaus
   cd /opt/odoo18/addons/
   
   # Copy the kulturhaus_dashboard directory here
   # (via git clone, scp, or direct copy)
   ```

2. **Restart Odoo Service**
   ```bash
   sudo systemctl restart odoo18
   ```

3. **Install Module via Odoo Interface**
   - Login to Odoo as administrator
   - Go to Apps menu
   - Click "Update Apps List"
   - Search for "Kulturhaus Dashboard"
   - Click Install

4. **Configure User Permissions**
   - Go to Settings → Users & Companies → Users
   - Edit users who should have dashboard access
   - Add them to "Dashboard User" group

### User Activation

1. **Enable Dashboard for User**
   - User goes to Preferences (top right menu)
   - Check "Use Dashboard Home"
   - Select preferred theme
   - Save preferences

2. **Dashboard Replaces Home Screen**
   - Next login/refresh will show dashboard
   - All standard Odoo menus remain accessible
   - User can disable dashboard anytime in preferences

### Admin Configuration

1. **Manage Dashboard Cards**
   - Go to "Dashboard Config" menu (admin only)
   - Click "Dashboard Cards"
   - Edit existing cards or create new ones
   - Set permissions by user groups

2. **Default Cards Included**
   - Events (Veranstaltungen)
   - Members (Mitglieder)  
   - Projects (Projekte)
   - Marketing (Newsletter)
   - Finances (Finanzen)
   - Reports (Berichte)
   - Website (External link)
   - Settings (Admin only)

### Testing Installation

1. **Verify Module Installation**
   - Check that no errors appear in Odoo logs
   - Confirm "Dashboard Config" menu is visible to admins
   - Test API endpoints: `/dashboard/data` should return JSON

2. **Test User Experience**
   - Enable dashboard for test user
   - Verify dashboard loads with cards and KPIs
   - Test card navigation to different Odoo screens
   - Test theme switching via configuration button
   - Verify mobile responsiveness

### Troubleshooting

#### Common Issues

**Module not appearing in Apps list:**
- Ensure module directory is in correct location
- Restart Odoo service
- Check "Update Apps List" was clicked

**Dashboard not loading:**
- Check browser console for JavaScript errors
- Verify user has "Dashboard User" group assigned
- Check Odoo server logs for Python errors

**Cards not showing:**
- Verify default data was loaded during installation
- Check user group permissions on cards
- Ensure required Odoo modules (event, project, etc.) are installed

**KPIs showing zero:**
- Normal for fresh installation with no data
- KPIs will populate as events, members, projects are added

### Performance Optimization

```bash
# Enable Odoo development mode for debugging
# Add to Odoo config: dev_mode = True

# For production, ensure:
# - Odoo workers configured (workers = 8)
# - Database indexing optimal
# - Static assets served by nginx
```

### Security Considerations

- Dashboard respects existing Odoo security groups
- Users only see cards they have permission to access
- External URLs in cards should be validated
- Regular security updates recommended

### Next Steps

1. **Train Users**
   - Provide user training on dashboard features
   - Create user guides for common workflows
   - Set up support process for questions

2. **Monitor Usage**
   - Track user adoption rates
   - Collect feedback for improvements
   - Monitor system performance impact

3. **Phase 2 Planning**
   - Plan advanced features based on user feedback
   - Consider custom card development
   - Evaluate integration needs

## Support

For technical support:
- Check Odoo server logs: `/var/log/odoo/odoo18.log`
- Enable developer mode for detailed error messages
- Contact development team for module-specific issues

## Rollback Plan

If needed to disable dashboard:
1. Users can disable in preferences
2. Admin can deactivate module
3. No data loss - all settings preserved
4. Standard Odoo functionality unaffected