#! /usr/bin/env python3
# -*- encoding: utf-8 -*-


import sys

import erppeek

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
# Script
###############################################################################

def get_translation_if_exist(source):
    # Get translated product name if any
    value = None
    tr = openerp.IrTranslation.browse([("src", "=", pt.name)])
    if tr is not None and len(tr) > 0:
        value = tr[0].value
    else:
        value = source
    return value

print("Code barre;Fournisseur;Nom produit;Poids;Categ mere;Sous-categ;Unite de vente;Colisage;Quantite mini;Quantite vendu par jour")

for pp in openerp.ProductProduct.browse([
        ("active", "=", True),
        ("purchase_ok", "=", True)]):
    pt = pp.read('product_tmpl_id')
    pname = get_translation_if_exist(pp.name)

    # Get & Filter category
    pcat = None
    ppcat = None
    cat = pt.read('categ_id')
    if cat.parent_id is not False and (
            cat.parent_id.id == 52 \
            or cat.parent_id.id == 104):
        continue
    else:
        pcat = cat.name
        if cat.parent_id is not False:
            ppcat = cat.parent_id.name

    # Get supplier infos
    sinfo = None
    sups = openerp.ProductSupplierinfo.browse([("product_tmpl_id", "=", pt.id)])
    if sups is not None and len(sups) > 0:
        sinfo = sups[0]

    # Get average sell
    weekly = pp.read('displayed_average_consumption')
    daily_sell = weekly / 5 # store is open 5 days a week
        

    print("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s" % (pp.barcode, sinfo.name, pname,
        pt.weight_net, ppcat, pcat, pt.uom_id.name, sinfo.package_qty,
        sinfo.min_qty, daily_sell))
