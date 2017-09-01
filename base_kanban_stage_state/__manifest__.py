# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Base Kanban Stage State",
    "summary": "Maps stages from base_kanban_stage to states",
    "version": "10.0.1.0.0",
    "category": "Base",
    "website": "https://github.com/OCA/server-tools.git",
    "author": "LasLabs, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base_kanban_stage",
    ],
    "data": [
        "views/base_kanban_stage_state_view.xml",
    ],
}
