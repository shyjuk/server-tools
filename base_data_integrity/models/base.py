# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models, fields


models.MAGIC_COLUMN.extend((
    '_signature', '_hash',
))


class Base(models.AbstractModel):

    _inherit = 'base'

    @api.multi
    def data_integrity_hash(self, update=False):
        """ Return the old hash """

    @api.multi
    def data_integrity_get_hash(self):
        """ Return the current record's hash. """

