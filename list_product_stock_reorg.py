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
DATE_NOTIME_FORMAT = '%d-%m-%Y'

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
        "Qte mini", "Qte vendu depuis 06/20", "Date 1ere vente",
        "Nb cmds depuis 06/20"))
    next_row += 1

    for p in products:
        ws.append((p['barcode'], p['supplier'], p['name'], p['weight'],
            p['pcat'], p['cat'], p['unit'], p['pqty'], p['minqty'],
            p['total_sale'], p['date_first_sale'], p['nb_purchase']))
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
    cat_to_filter = (96, 89, 124, 90, 85, 18, 4, 66, 147, 148, 75, 30, 139)
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

    # Get all sales since june 2020
    total_sale = 0
    date_first_sale = None

    sales = openerp.PosOrderLine.browse([
        ("product_id", "=", pp.id),
        ("create_date", ">", '2020-06-01')],
        order="create_date asc")

    if sales and len(sales) > 0:
        date_first_sale = datetime.strptime(
                sales[0].create_date, DATE_FORMAT).strftime(DATE_NOTIME_FORMAT)

    for sale in sales:
        total_sale += sale.qty

    #weekly = pp.read('displayed_average_consumption')
    #daily_sell = weekly / 5 # store is open 5 days a week

    # Get all cmd since june 2020
    purchases = openerp.PurchaseOrderLine.browse([
        ("product_id", "=", pp.id),
        ("create_date", ">", '2020-06-01')],
        order="create_date asc")

    nb_purchase = len(purchases)
    if nb_purchase > 0:
        first_purchase_date = datetime.strptime(
                purchases[0].create_date, DATE_FORMAT)
        days_since_first_purchase = (datetime.now() - first_purchase_date).days


    print("%s;%s;%s;%s;%s;%s;%s;%s;%s;%d;%s;%d" % (pp.barcode, sinfo.name, pname,
        pt.weight_net, mcat, scat, pt.uom_id.name, sinfo.package_qty,
        sinfo.min_qty, total_sale, date_first_sale, nb_purchase))

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
        'total_sale': int(total_sale),
        'date_first_sale': str(date_first_sale),
        'nb_purchase': int(nb_purchase)})

save_to_xls('articles.xls', products)
