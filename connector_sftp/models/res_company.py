# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'
    sftp_connector_ids = fields.One2many(
        string='SFTP Connectors',
        comodel_name='connector.sftp',
        inverse_name='company_id',
    )
