# -*- coding: utf-8 -*-
{
    'name': "E-Marine",
    'summary': """HR Management & Operations""",
    'description': """Insurance Broker System """,
    'author': "Black Belts Egypt",
    'website': "www.blackbelts-egypt.com",
    'category': 'Marine',
    'version': '0.1',
    'license': 'AGPL-3',
    # any module necessary for this one to work correctly
    'depends': ['base','arope-conf'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'views/policy_marine.xml',
        # 'reports/marine_policy_report.xml',
        # 'reports/certificate_report.xml',
        # 'reports/fcl_report.xml',
        # 'reports/en_marine_policy_report.xml',
        'views/setup.xml',
        'views/certificate.xml',
        'views/endorsement.xml',

        'views/menu_item.xml'

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'css': ['static/src/css/marine.css'],

}
