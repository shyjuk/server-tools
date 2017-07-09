# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime
import dateutil
import time
from collections import defaultdict

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval

from ..exceptions import OauthScopeValidationException


class OauthProviderScope(models.Model):
    _name = 'oauth.provider.scope'
    _description = 'OAuth Provider Scope'

    name = fields.Char(
        required=True, translate=True,
        help='Name of the scope, displayed to the user.')
    code = fields.Char(
        required=True, help='Code of the scope, used in OAuth requests.')
    description = fields.Text(
        required=True, translate=True,
        help='Description of the scope, displayed to the user.')
    model_id = fields.Many2one(
        comodel_name='ir.model', string='Model', required=True,
        help='Model allowed to be accessed by this scope.')
    model = fields.Char(
        related='model_id.model', string='Model Name', readonly=True,
        help='Name of the model allowed to be accessed by this scope.')
    filter_id = fields.Many2one(
        comodel_name='ir.filters', string='Filter',
        domain="[('model_id', '=', model)]",
        help='Filter applied to retrieve records allowed by this scope.')
    field_ids = fields.Many2many(
        comodel_name='ir.model.fields', string='Fields',
        domain="[('model_id', '=', model_id)]",
        help='Fields allowed by this scope.')

    _sql_constraints = [
        ('code_unique', 'UNIQUE (code)',
         'The code of the scopes must be unique !'),
    ]
    
    @property
    @api.model
    def ir_filter_eval_context(self):
        """ Returns the base eval context for ir.filter domains evaluation """
        return {
            'datetime': datetime,
            'dateutil': dateutil,
            'time': time,
            'uid': self.env.uid,
            'user': self.env.user,
        }

    @api.multi
    def filter_by_model(self, model):
        """ Return the current scopes that are associated to the model.

        Args:
            model (str): Name of the model to operate on.

        Returns:
            OauthProviderScope: Recordsets associated to the model.
        """
        return self.filtered(lambda record: record.model == model)

    @api.multi
    def get_data(self, model, res_id=None, all_scopes_match=False,
                 domain=None):
        """ Return the data matching the scopes from the requested model.

        Args:
            model (str): Name of the model to operate on.
            res_id (int): ID of record to find. Will only return this record,
                if defined.
            all_scopes_match (bool): True to filter out records that do not
                match all of the scopes in the current recordset.
            domain (list of tuples, optional): Domain to append to the
                `filter_domain` that is defined in the scope.

        Returns:
            dict: If `res_id` is defined, this will be the scoped data for the
                appropriate record (or empty dict if no match). Otherwise,
                this will be a dictionary of scoped record data, keyed by
                record ID.
        """

        data = defaultdict(dict)
        eval_context = self.ir_filter_eval_context
        all_scopes_records = self.env[model]

        for scope in self.filter_by_model(model):

            records = scope._get_scoped_records(eval_context, domain)

            for record_data in records.read(scope.field_ids.mapped('name')):
                for field, value in record_data.items():
                    if isinstance(value, tuple):
                        # Return only the name for a many2one
                        data[record_data['id']][field] = value[1]
                    else:
                        data[record_data['id']][field] = value

            # Keep a list of records that match all scopes
            if not all_scopes_records:
                all_scopes_records = records
            else:
                all_scopes_records &= records

        # If all scopes are required to match, filter the results to keep only
        # those matching all scopes
        if all_scopes_match:
            data = dict(
                filter(
                    lambda _data: _data[0] in all_scopes_records.ids,
                    data.items(),
                ),
            )

        if res_id is not None:
            data = data.get(res_id, {})

        return data

    @api.multi
    def create_record(self, model, vals):
        """ Create a record, validate the scope, and return (if valid).

        Args:
            model (str): Name of the model to operate on.
            vals (dict): Values to create record with, keyed by field name.

        Returns:
            OauthProviderScope: Newly created record

        Raises:
            OauthScopeValidationException: If fields are included in vals,
                but are not within the current scope.
        """
        
        if not self._validate_scope_field(model, vals):
            raise OauthScopeValidationException('field')

        record = self.env[model].create(vals)

        if not self._validate_scope_record(record):
            raise OauthScopeValidationException('record')

        return record

    def get_record(self, model, domain=None):
        """ Get the currently scoped records, adhering to optional domain.

        Args:
            model (str): Model to search.
            domain (list of tuples, optional): Additional domain to add to the
                currently scoped filter.

        Returns:
            models.Model: Recordsets.
        """
        records = self.env[model]
        eval_context = self.ir_filter_eval_context
        for scope in self.filter_by_model(model):
            records += scope._get_scoped_records(
                model, eval_context, domain,
            )
        return records

    @api.multi
    def write_record(self, records, vals):
        """ Write to a recordset, adhering to the current scope.

        Args:
            records (models.Model): Recordset to write to.
            vals (dict): Values to modify records with, keyed by field name.

        Returns:
            OauthProviderScope: The same recordset that was provided as input.

        Raises:
            OauthScopeValidationException: Raised in the following cases:
                * If records are attempted to be edited, but are not within
                    the current scope.
                * If fields are included in vals, but are not within the
                    current scope.
                * If the record no longer falls within scope after being
        """

        if not self._validate_scope_field(records._name, vals):
            raise OauthScopeValidationException('field')

        if not self._validate_scope_record(records):
            raise OauthScopeValidationException('record')

        records.write(vals)

        if not self._validate_scope_record(records):
            raise OauthScopeValidationException('record')

        return records

    @api.multi
    def delete_record(self, records):
        """ Delete a recordset that is within the current scope.

        Args:
            records (models.Model): Recordset to delete.

        Raises:
            OauthScopeValidationException: If records are not within the
                current scope.
        """
        
        if not self._validate_scope_record(records):
            raise OauthScopeValidationException('record')

        records.unlink()

    @api.multi
    def _get_filter_domain(self, eval_context):
        """ Return the scope's domain.

        Args:
            eval_context (dict): Base eval context, such as provided by
                `ir_filter_eval_context`

        Returns:
            list of tuples: Domain of the scope, in standard Odoo format.
        """
        self.ensure_one()
        filter_domain = [(1, '=', 1)]
        if self.filter_id:
            filter_domain = safe_eval(
                self.filter_id.sudo().domain,
                eval_context,
            )
        if res_id is not None:
            filter_domain.append(
                ('id', '=', res_id),
            )
        return filter_domain

    @api.multi
    def _get_scoped_records(self, model, eval_context=None, add_domain=None):
        """ Return records that are within the scopes in the recordset.

        Args:
            model (str): Name of the model to operate on.
            eval_context (dict, optional): Base eval context, such as provided
                by `ir_filter_eval_context`.
            add_domain (list of tuples, optional): Domain to append to the
                `filter_domain` that is defined in the scope.

        Returns:
            models.Model: Recordset matching the scope.
        """
        self.ensure_one()
        if eval_context is None:
            eval_context = self.ir_filter_eval_context
        if add_domain is None:
            add_domain = []
        filter_domain = self._get_filter_domain(eval_context)
        return self.env[model].search(filter_domain + add_domain)

    @api.multi
    def _validate_scope_record(self, records):
        """ Validate that the recordset is within the current scope.

        Args:
            records (models.Model): Recordset to validate.

        Returns:
            bool: Indicating whether the records are within scope.
        """

        scoped_records = self._get_scoped_records(
            self.env[records._name],
        )
        return all([
            r.id in scoped_records for r in records
        ])

    @api.multi
    def _validate_scope_field(self, model, vals):
        """ Validate that the input vals do not violate the current scope.

        Args:
            model (str): Name of the model to operate on.
            vals (dict): Values that should be checked against the current
                scope, keyed by field name.

        Returns:
            bool: Whether the values are within the scope.
        """
        scopes = self.filter_by_model(model)
        field_names = scopes.field_ids.mapped('name')
        return all([
            f in field_names for f in vals.keys()
        ])
