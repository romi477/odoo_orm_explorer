# -*- coding: utf-8 -*-

{
    'name': 'Odoo ORM Explorer',
    'summary': 'Odoo ORM Explorer',
    'version': '13.0.1.0.0',
    'category': 'Orher',
    'author': 'Raman K.',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/orm_query_views.xml',
        'wizard/orm_query_wizard.xml',
        'views/ir_action.xml',
        'views/ir_menu.xml',
    ],
    'images': [
        # 'static/description/icon.png',
    ],
    'installable': True,
    'application': False,
}
