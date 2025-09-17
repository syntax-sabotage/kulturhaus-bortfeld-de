{
    'name': 'Kulturhaus Vereinsarbeit Core',
    'version': '18.2.1.0.0',
    'category': 'Kulturhaus/Vereinsverwaltung',
    'summary': 'Kernmodul für Kulturhaus Vereinsarbeit - Verwaltung von Vereinsaktivitäten',
    'description': """
        Kulturhaus Vereinsarbeit Core
        ==============================
        
        Dieses Modul stellt die Kernfunktionalität für die Verwaltung
        von Vereinsaktivitäten im Kulturhaus Bortfeld zur Verfügung.
        
        Hauptfunktionen:
        ----------------
        * Mitgliederverwaltung
        * Veranstaltungsplanung
        * Ressourcenverwaltung
        * Aufgabenverwaltung
        * Dokumentenverwaltung
        
        Technische Details:
        -------------------
        * Odoo Version: 18.0
        * Lizenz: LGPL-3
    """,
    'author': 'Kulturhaus Bortfeld',
    'website': 'https://kulturhaus-bortfeld.de',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'contacts',
        'calendar',
        'project',
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_backend': [
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}