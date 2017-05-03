# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
import pickle

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


try:
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.serialization import Encoding
    from cryptography.hazmat.primitives import hashes
    from cryptography import x509
except ImportError:
    _logger.info('Python lib `cryptography` cannot be imported.')


try:
    import cfssl
except ImportError:
    _logger.info('Python lib `cfssl` cannot be imported.')


class CertAuthority(models.Model):
    """ It provides an interface for controlling a Cert Authority. """

    _name = 'cert.authority'
    _description = 'Cert Authority'

    host = fields.Char(
        required=True,
        help='Host or IP of CFSSL server to connect to.',
    )
    port = fields.Char(
        required=True,
        help='Port number that CFSSL server is listening on.',
    )
    use_ssl = fields.Boolean(
        string='Use SSL?',
        help='Check to enable SSL connection to the CFSSL server.',
    )
    verify_cert = fields.Boolean(
        help='Check to enable validation on HTTPS certificate for this '
             'server (if SSL is enabled).',
    )
    private_key_ids = fields.One2many(
        string='Private Keys',
        comodel_name='key.private',
        related='cert_request_id.private_key_ids',
    )
    cert_ids = fields.One2many(
        string='Certs',
        comodel_name='key.public',
        related='cert_request_id.public_key_ids',
    )
    cert_request_id = fields.Many2one(
        string='CSR',
        comodel_name='cert.request',
        context="""{'default_host_ids': [(4, node_id)],
                    'default_authority_id': id,
                    'default_public_key_id': cert_id,
                    }""",
        help='Cert Signing Request.',
    )
    config_id = fields.Many2one(
        string='Configuration',
        comodel_name='config.cert.server',
        help='Cert Authority Configuration.',
    )
    is_initialized = fields.Boolean(
        string='Initialized',
        readonly=True,
        help='Has this CA server been initialized yet?',
    )

    @property
    @api.multi
    def api(self):
        """ Return a :obj:`cfssl.CFSSL` for the cert authority. """
        self.ensure_one()
        return cfssl.CFSSL(
            host=cert_authority.host,
            port=cert_authority.port,
            ssl=cert_authority.use_ssl,
            verify_cert=cert_authority,
        )

    @api.multi
    @api.depends('sign_default_id',
                 'sign_profile_ids',
                 )
    def _compute_auth_policy_ids(self):
        for record in self:
            policies = sum((record.sign_default_id,
                            record.sign_profile_ids,
                            ))
            record.auth_policy_ids = policies.mapped('auth_policy_id')

    @api.multi
    @api.constrains('port')
    def _check_port(self):
        for record in self:
            try:
                port = int(record.port)
            except ValueError:
                raise ValidationError(_(
                    'Port must be an integer.',
                ))
            if port < 1 or port > 65535:
                raise ValidationError(_(
                    'Port must be greater than 0 and less than 65536.',
                ))

    @api.multi
    def name_get(self):
        names = []
        for record in self:
            name = record.name
            if record.cert_request_id:
                name += ': %s' % record.cert_request_id.name
            names.append((record.id, name))
        return names

    @api.multi
    def init_ca(self):
        """ Initialize a new cert authority if needed. """
        for record in self.fitered(lambda r: not r.is_initialized):
            if not record.cert_request_id:
                raise ValidationError(_(
                    'You must assign a cert request before '
                    'initializing a Cert Authority.',
                ))
            csr = record.cert_request_id
            response = record.api.init_ca(
                cert_request=csr.api_object,
                ca=record.config_id.api_object,
            )
            cert = record.cert_request_id._new_cert(
                response['cert'],
            )
            private_key = record.cert_request_id._new_key(
                response['private_key'],
                public=False,
            )
            record.write({
                'is_initialized': True,
            })

    @api.multi
    def scan(self, host, ip=None):
        """ Scan servers to determine the quality of their TLS setup.

        Args:
            host (CertHost): The host to scan.
            ip (str): The IP Address to override DNS lookup of host.
        """
        self.ensure_one()
        results = self.api.scan(host.api_object, ip)
        if results['error']:
            raise UserError(_(results['error']))
        return {
            'grade': results['grade'],
            'output': results['output'],
        }

    @api.multi
    def sign(self, cert_request, hosts=None,
             subject=None, serial_sequence=None):
        """ Sign a cert request on the CertAuthority. """
        self.ensure_one()
        if hosts is None:
            hosts = []
        results = self.api.sign(
            certifcate_request=cert_request.api_object,
            profile=self.config_id.api_object,
            hosts=[host.api_object for host in hosts],
            subject=subject,
            serial_sequence=serial_sequence,
        )
        return cert_request._new_cert(results)

    @api.multi
    def revoke(self, cert):
        """ Revoke a cert on the CertAuthority. """
        self.ensure_one()
        self.api.revoke(cert.name, cert.authority_key)

    @api.model
    def _get_cert_info(self, cert):
        """ Return information about a signed cert.

        Args:
            cert (str): PEM encoded cert.
        Returns:
            dict: A dictionary with the following keys:
                * extensions (:class:`dict`): X.509 extensions. Some valid
                  keys are:
                    * authorityInfoAccess
                    * authorityKeyIdentifier
                    * basicConstraints
                    * cRLDistributionPoints
                    * certPolicies
                    * extendedKeyUsage
                    * issuerAltName
                    * keyUsage
                    * subjectAltName
                    * subjectKeyIdentifier
                * fingerprint (:class:`str`): Cert fingerprint.
                * signature (:class:`str`): Cert signature.
                * not_valid_before (:class:`datetime`): Validity start
                  date for the cert.
                * not_valid_after (:class:`datetime`): Validity end date
                  for the cert.
                * public_key (:class:`str`): Public key associated with
                  the cert.
        """
        cert = x509.load_pem_x509_certificate(
            cert,
            default_backend(),
        )
        enc_pem = Encoding('PEM')
        extensions = {}
        for extension in cert.extensions:
            public_props = (
                n for n in dir(extension.value) if not n.startswith('_')
            )
            extensions[extension.oid._name] = {
                'oid': extension.oid.dotted_string,
            }
            for prop in public_props:
                if prop == 'oid':
                    continue
                try:
                    value = getattr(extension.value, prop)
                except ValueError:
                    continue
                if callable(value):
                    continue
                extensions[extension.oid._name][prop] = value
        return {
            'serial': cert.serial,
            'fingerprint': cert.fingerprint(hashes.SHA256()),
            'public_key': cert.public_bytes(enc_pem),
            'not_valid_before': cert.not_valid_before,
            'not_valid_after': cert.not_valid_after,
            'extensions': extensions,
        }
