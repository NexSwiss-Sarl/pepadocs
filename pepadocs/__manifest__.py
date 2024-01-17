# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#FOR ODOO 15 MIN ! because of how assets are imported. 'price': 0.00,
{
    'name': 'pepadocs',
    'version': '15.0.1.0.0',
    'category': 'services/pepadocs',
    'sequence': 1,
    'support':'contact@nexswiss.ch',
    'summary': 'Digital intervention reports',
    'description': "We'll help you create customized report templates that you and your team can then complete on iOS & Android. This application relies on pepadocs.com services to operate. ( https://pepadocs.com/CG )",
    'currency': 'EUR',
    'license': 'LGPL-3', 
    'website': 'https://pepadocs.com',
    'depends': [
        'base',
        'web'
    ],
    'data': [
        'views/main_view.xml',
        'views/settings_view.xml',
        'views/user_view.xml',
        'security/ir.model.access.csv'
    ],
    'demo': [
    ],
    'css': [],
    'images': ['static/description/banner.png', 'static/description/icon.png','static/description/main_screenshot.png'],
    'assets': {
        'web.assets_backend': [
            'pepadocs/static/src/js/load_iframe.js',
        ],
        'web.assets_common': [
        ],
        'web.assets_qweb': [
            'pepadocs/static/src/xml/main_template.xml',
        ],
    },
    'author': 'NexSwiss Sàrl',
    'maintainer': 'NexSwiss Sàrl',
    'installable': True,
    'application': True,
    'auto_install': False,
    'uninstall_hook': 'uninstall_hook',
}