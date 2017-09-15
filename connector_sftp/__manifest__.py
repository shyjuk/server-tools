# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "SFTP Connector",
    "summary": "Framework for interacting with SFTP hosts",
    "version": "10.0.1.0.0",
    "category": "Base",
    "website": "https://laslabs.com/",
    "author": "LasLabs, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [
            'paramiko',
        ],
    },
    'data': [
        'views/connector_sftp_view.xml',
        'views/res_company_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/connector_sftp_demo.xml',
    ],
}