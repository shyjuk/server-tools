# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class CertName(models.Model):
    """ It provides the concept of a cert's SubjectInfo """

    _name = 'cert.name'
    _description = 'Cert Name'

    country_id = fields.Many2one(
        string='Country',
        comodel_name='res.country',
        required=True,
        default=lambda s: s.env.user.country_id,
    )
    state_id = fields.Many2one(
        string='State',
        comodel_name='res.country.state',
        domain='[(country_id, "=", country_id)]',
        default=lambda s: s.env.user.state_id,
    )
    city = fields.Char(
        default=lambda s: s.env.user.city,
    )
    company_id = fields.Many2one(
        string='Organization',
        comodel_name='res.company',
        required=True,
        domain='[(company_id, "=", company_id)]',
        default=lambda s: s.env.user.company_id,
    )
    organization_unit = fields.Char(
        required=True,
    )
    api_object = fields.Binary(
        compute="_compute_api_object",
    )

    @api.multi
    def _compute_api_object(self):
        """ It computes the keys required for the JSON request """
        for record in self:
            record.api_object = self.cfssl.SubjectInfo(
                record.company_id.name,
                record.organizational_unit,
                record.city,
                record.state_id.name,
                record.country_id.code,
            )
