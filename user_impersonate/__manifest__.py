# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'User Impersonation',
    'summary': 'Provides the ability for administrators to impersonate '
               'users.',
    'version': '10.0.1.0.0',
    'author': "LasLabs, Odoo Community Association (OCA)",
    'category': 'Technical Settings',
    'depends': [
        'base',
    ],
    'website': 'https://laslabs.com',
    'license': 'LGPL-3',
    'data': [
        'wizards/res_users_impersonate_view.xml',
    ],
    'installable': True,
    'application': False,
}
