# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class DataIntegrityHash(models.Model):

    _name = 'data.integrity.hash'
    _description = 'Data Integrity Hash'

    active = fields.Boolean(
        default=True,
        index=True,
    )
    source = fields.Reference(
        string='Source Record',
        selection=referenceable_models,
        required=True,
        index=True,
    )
    rule_id = fields.Many2one(
        string=''
    )
    date_activated = fields.Datetime(
        compute='_compute_date_activated',
        store=True,
        readonly=True,
    )
    date_deactivated = fields.Datetime(
        compute='_compute_date_deactivated',
        store=True,
        readonly=True,
    )

    @api.multi
    @api.depends('active')
    def _compute_date_activated(self):
        for record in self:
            if record.active and not record.date_activated:
                record.date_activated = fields.Datetime.now()

    @api.multi
    @api.depends('active')
    def _compute_date_deactivated(self):
        for record in self:
            if not record.active and not record.date_deactivated:
                record.date_deactivated = fields.Datetime.now()

    @api.multi
    @api.constrains('active', 'source_int', 'source_model')
    def check_only_active_source(self):
        """ Do not allow multiple active hashes for the same source. """
        for record in self:
            if not record.active:
                continue
            matches = self.search([
                ('active', '=', True),
                ('source_int', '=', record.source_int),
                ('source_model', '=', record.source_model),
            ])
            if len(matches) > 1:
                raise ValidationError(_(
                    'You cannot store multiple active hashes for the same '
                    'record.',
                ))

    @api.model
    def get(self, record):
        """ Return the DataIntegrityHash associated with record. """
        return self.search([
            ('source', '=', '%s,%d' % (record._name, record.id)),
        ])

    @api.model
    def new(self, record, deactivate=True):
        """ Create a new DataIntegrityHash for the record.
        
        Args:
            deactivate (bool): Deactivate the old hash for the record?
        """
        if deactivate:
            self.get(record).active = False
        return self.create({
            'source': record,
        })
