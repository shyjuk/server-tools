# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from werkzeug import exceptions


class OauthApiException(exceptions.BadRequest):
    pass


class OauthInvalidTokenException(exceptions.Unauthorized):
    def __init__(self):
        super(OauthInvalidTokenException, self).__init__(
            'Invalid or Expired Token',
        )
        self.traceback = ('', '', '')


