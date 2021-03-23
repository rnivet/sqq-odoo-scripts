#! /usr/bin/env python3
# -*- encoding: utf-8 -*-


import sys
from datetime import datetime

import erppeek
from openpyxl import load_workbook, Workbook

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

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def get_translation_if_exist(source):
    # Get translated product name if any
    value = None
    tr = openerp.IrTranslation.browse([("src", "=", pt.name)])
    if tr is not None and len(tr) > 0:
        value = tr[0].value
    else:
        value = source
    return value

def save_to_xls(file_name, products):
    next_row = 1
    wb = Workbook()
    ws = wb.active
    ws.title = 'Liste articles'

    ws.append(("Code barre", "Fournisseur", "Nom produit", "Poids",
        "Categorie mere", "Sous-categorie", "Unite de vente", "Colisage",
        "Quantite mini", "Quantite vendu par jour", "Nombre de commandes",
        "Nombre de jours depuis la 1ere cmd"))
    next_row += 1

    for p in products:
        ws.append((p['barcode'], p['supplier'], p['name'], p['weight'],
            p['pcat'], p['cat'], p['unit'], p['pqty'], p['minqty'], p['sell'],
            p['nb_purchase'], p['first_purchase_since']))
        next_row += 1

    wb.save(filename = file_name)

print("Code barre;Fournisseur;Nom produit;Poids;Categ mere;Sous-categ;Unite de vente;Colisage;Quantite mini;Quantite vendu par jour")

products = []

for pp in openerp.ProductProduct.browse([
        ("active", "=", True),
        ("purchase_ok", "=", True),
        ("sale_ok", "=", True)]):
    pt = pp.read('product_tmpl_id')
    pname = get_translation_if_exist(pp.name)

    # Get & Filter category
    mcat = None
    scat = None
    cat = pt.read('categ_id')
    pcat = cat.read('parent_id')

    # Filter wanted cat
    cat_to_filter = (96, 89, 124, 90, 85, 18, 4, 66, 82, 147, 148, 75)
    if cat.id not in cat_to_filter and (not pcat or pcat.id not in cat_to_filter):
        continue

    if cat.parent_id is not False:
        mcat = pcat.name
        scat = cat.name
    else:
        mcat = cat.name

    # Get supplier infos
    sinfo = None
    sups = openerp.ProductSupplierinfo.browse([("product_tmpl_id", "=", pt.id)])
    if sups is not None and len(sups) > 0:
        sinfo = sups[0]
    else:
        continue

    # Get average sell
    weekly = pp.read('displayed_average_consumption')
    daily_sell = weekly / 5 # store is open 5 days a week

    # Get all cmd during last 12 month
    purchases = openerp.PurchaseOrderLine.browse([("product_id", "=", pp.id)],
            order="create_date asc")
    nb_purchase = len(purchases)
    if nb_purchase > 0:
        first_purchase_date = datetime.strptime(
                purchases[0].create_date, DATE_FORMAT)
        days_since_first_purchase = (datetime.now() - first_purchase_date).days


    print("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%d;%s" % (pp.barcode, sinfo.name, pname,
        pt.weight_net, mcat, scat, pt.uom_id.name, sinfo.package_qty,
        sinfo.min_qty, daily_sell, nb_purchase, first_purchase_date))

    products.append({
        'barcode': str(pp.barcode),
        'supplier': str(sinfo.name),
        'name': str(pname),
        'weight': float(pt.weight_net),
        'pcat': str(mcat),
        'cat': str(scat),
        'unit': str(pt.uom_id.name),
        'pqty': int(sinfo.package_qty),
        'minqty': int(sinfo.min_qty),
        'sell': round(daily_sell, 1),
        'nb_purchase': int(nb_purchase),
        'first_purchase_since': int(days_since_first_purchase)})

save_to_xls('articles.xls', products)
