#! /usr/bin/env python3
# -*- encoding: utf-8 -*-


import sys

import erppeek

from cfg_secret_configuration import odoo_configuration_user_prod as odoo_configuration_user

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
# Script
###############################################################################
count = 0
print("Nom;Prenom;email")
for partner in openerp.ResPartner.browse([
    ("active", "=", True),
    ("is_worker_member", "=", True),
    ("is_unsubscribed", "=", False)]):
    count += 1
    try:
        (nom, prenom) = partner.name.split(',')
    except:
        continue
    print("%s;%s;%s" % (nom.strip(), prenom.strip(), partner.email))
