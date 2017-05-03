# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from hashlib import sha1

from odoo import api, fields, models


class CertRequest(models.Model):
    """ It provides the concept of a Cert Request """

    _name = 'cert.request'
    _inherit = ['cert.abstract',
                'key.abstract',
                ]
    _description = 'Cert Request'

    name = fields.Char(
        string='Common Name',
        required=True,
    )
    authority_id = fields.Many2one(
        string='Cert Authority',
        comodel_name='cert.authority',
        required=True,
        ondelete='cascade',
    )
    host_ids = fields.Many2one(
        string='Hosts',
        comodel_name='cert.host',
    )
    subject_info_ids = fields.Many2many(
        string='Names',
        comodel_name='cert.name',
        required=True,
    )
    public_key_ids = fields.One2many(
        string='Public Key',
        comodel_name='key.public',
        inverse_name='request_id',
    )
    private_key_ids = fields.One2many(
        string='Private Key',
        comodel_name='key.private',
        inverse_name='request_id',
    )
    cert_ids = fields.One2many(
        string='Signed Cert',
        comodel_name='cert.x509',
        inverse_name='request_id',
    )
    api_object = fields.Binary(
        compute="_compute_api_object",
    )

    @api.multi
    def create_cert_request(self):
        """ Generate a new PK, certificate, and CSR. """
        for record in self:
            response = record.api.new_cert(
                request=record.to_api(),
            )
            record._new_cert(
                response['cert'],
            )
            record._new_key(
                response['private_key'],
                public=False,
            )
            attachment = record.attachment_id.create({
                'datas': response['cert_request'],
            })
            record.write({
                'attachment_id': attachment.id,
            })

    @api.multi
    def _new_key(self, key_data, public=False, mime='x-pem-file'):
        self.ensure_one()
        model = 'public' if public else 'private'
        key = self.env['key.%s' % model].create({
            'name': sha1(key_data).hexdigest(),
            'strength': self.strength,
            'algorithm': self.algorithm,
            'mime_sub_type': mime,
            'request_id': self.id,
        })
        attachment = key.attachment_id.create({
            'datas': key_data,
        })
        key.attachment_id = attachment.id
        return key

    @api.multi
    def _new_cert(self, cert_data):
        self.ensure_one()
        cert_info = self.authority_id._get_cert_info(cert_data)
        public_key = self._new_key(
            cert['public_key'],
            public=True,
        )
        auth_key = cert_info['authorityKeyIdentifier']['key_identifier']
        usages = self.env['policy.use']
        for usage_str in cert_info['keyUsage']:
            usage = usages.search([
                ('code', '=', usage_str.replace(' ', '_')),
            ])
            if not usage:
                continue
            usages += usage
        cert = self.env['cert.x509'].create({
            'subject_key': cert_info['subjectKeyIdentifier']['digest'],
            'authority_key': auth_key,
            'public_key_id': public_key.id,
            'request_id': self.id,
            'usage_ids': usages.ids,
        })
        attachment = key.attachment_id.create({
            'datas': cert_data,
        })
        cert.attachment_id = attachment.id

    @api.multi
    def _compute_api_object(self):
        """ It computes the keys required for the JSON request """
        for record in self:
            record.api_object = self.cfssl.CertRequest(
                common_name=record.name,
                names=record.subject_info_ids.mapped('api_object'),
                hosts=record.host_ids.mapped('api_object'),
                key=self.cfssl.ConfigKey(
                    algorithm=record.algorithm,
                    strength=record.strength,
                ),
            )
