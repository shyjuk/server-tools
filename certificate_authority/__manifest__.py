# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Certificate Authority',
    'description': 'This module provides CA functionality by connecting to '
                   'remote CFSSL server(s).',
    'version': '10.0.1.0.0',
    'category': 'Base',
    'author': 'LasLabs Inc.',
    'license': 'LGPL-3',
    'website': 'https://laslabs.com',
    'depends': [
        'base',
    ],
    'data': [
        'data/image_template.xml',
        'data/image.xml',
        'data/image_port.xml',
        'data/image_volume.xml',
        'data/application_tag.xml',
        'data/application_type.xml',
        'data/application_template.xml',
        'data/application.xml',
        'data/cert_policy_use.xml',
        'views/cert_authority.xml',
        'views/menu.xml',
        'wizards/cert_authority_scan.xml',
        'wizards/cert_authority_sign.xml',
        'wizards/cert_authority_revoke.xml',
    ],
    'installable': True,
    'application': False,
}
