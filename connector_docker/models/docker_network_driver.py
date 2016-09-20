# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import models, api, fields


class DockerNetworkDriver(models.Model):
    _name = 'docker.network.driver'
    _description = 'Docker Network Driver'

    name = fields.Char()
    code = fields.Char()
    
