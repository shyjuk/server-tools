# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models, fields


models.MAGIC_COLUMN.extend((
    '_signature', '_hash',
))


class IrModel(models.Model):

    _inherit = 'ir.model'

    hash_method = fields.

