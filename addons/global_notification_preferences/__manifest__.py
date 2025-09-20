{
    'name': 'Global Notification Preferences',
    'version': '18.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Allow users to set global notification preferences for all followed records',
    'description': """
        Global Notification Preferences
        ================================
        
        This module allows users to configure their notification preferences globally,
        rather than per-record. Users can decide which types of updates they want to
        be notified about across ALL records they follow.
        
        Features:
        - User-level notification preferences in user profile
        - Automatic application to new followers
        - Override mechanism for specific records if needed
        - Works with all mail.thread models
    """,
    'author': 'IdeaWise Group',
    'website': 'https://ideawisegroup.com',
    'depends': [
        'base',
        'mail',
        'project',  # For testing with tasks
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_users_views.xml',
        'views/mail_followers_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}