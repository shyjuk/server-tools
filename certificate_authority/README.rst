.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

=====================
Certificate Authority
=====================

This module provides a Cert Authority using Odoo and CFSSL,

Configuration
=============


Usage
=====

To use this module, you need to:

#. Create a CFSSL Service

Known issues / Roadmap
======================

* Add more Signature Profile options - https://github.com/cloudflare/cfssl/blob/86ecfbe5750ebf05565e4c80104d0a7919792fee/doc/cmd/cfssl.txt#L113
* Need to add a hook so that services dependent on revoked certs are refreshed
* Don't run as root

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/oca/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Dave Lasley <dave@laslabs.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
