# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    'name': 'Import Wordpress',
    'version': '10.0.1.0.0',
    'category': 'Tools',
    'author': "LasLabs",
    'website': 'https://laslabs.com',
    'license': 'LGPL-3',
    'installable': True,
    'depends': [
        'website_blog_category',
    ],
    'data': [
        'wizards/import_wordpress_wizard_view.xml',
    ],
    'external_dependencies': {
        'python': [
            'bs4',
            'wordpress_xmlrpc',
        ],
    },
}
