# -*- coding: utf-8 -*-
{
    'name': 'Task Group Mentions',
    'version': '18.0.1.0.0',
    'category': 'Project',
    'summary': 'Enable @all and @Vorstand mentions in task chatter',
    'description': """
        Task Group Mentions
        ===================
        
        This module enables special mentions in project task chatter:
        - @all: Notifies all task followers
        - @Vorstand: Notifies all board members
        
        Features:
        - Automatic detection of special keywords
        - Bulk notification to groups
        - Visual feedback in chatter
    """,
    'author': 'Kulturhaus Bortfeld',
    'website': 'https://kulturhaus-bortfeld.de',
    'depends': [
        'project',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/mail_template.xml',
        'views/project_task_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'task_group_mentions/static/src/js/chatter_composer.js',
            'task_group_mentions/static/src/scss/chatter.scss',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}