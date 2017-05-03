# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class KeyPublic(models.Model):
    """ It provides attributes and methods related to handling public keys """

    _name = 'key.public'
    _inherit = 'key.abstract'
    _description = 'Key Abstract'
