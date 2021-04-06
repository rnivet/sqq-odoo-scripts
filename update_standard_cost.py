#! /usr/bin/env python3
# -*- encoding: utf-8 -*-


import sys
import erppeek
import csv
import unidecode

from cfg_secret_configuration import odoo_configuration_user_test as odoo_configuration_user

###############################################################################
# Odoo Connection
###############################################################################
def init_openerp(url, login, password, database):
    openerp = erppeek.Client(url)
    uid = openerp.login(login, password=password, database=database)
    user = openerp.ResUsers.browse(uid)
    tz = user.tz
    return openerp, uid, tz

openerp, uid, tz = init_openerp(
    odoo_configuration_user['url'],
    odoo_configuration_user['login'],
    odoo_configuration_user['password'],
    odoo_configuration_user['database'])


###############################################################################
# Configuration
###############################################################################

###############################################################################
# Script
###############################################################################

for product in openerp.ProductTemplate.browse([
    ('has_theoritical_cost_different', '=', True),
    ('standard_price', '=', 0)]):
    print(product.name)
    product.use_theoritical_cost()
    print(product.standard_price, product.base_price)
