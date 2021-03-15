#! /usr/bin/env python3
# -*- encoding: utf-8 -*-


import sys
import erppeek

from datetime import datetime
from openpyxl import load_workbook, Workbook

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

DATE_FORMAT = '%Y-%m-%d'

def read_odoo_coops(at_date):
    odoo_coops = []

    partners = openerp.ResPartner.browse([("is_member", "=", True)])
    for partner in partners:
        # Find all capital invoices for the partner
        capital = 0
        for invoice in openerp.AccountInvoice.browse([
                ("partner_id", "=", partner.id),
                ("is_capital_fundraising", "=", True),
                ("state", "=", "paid"),
                ("date_invoice", "!=", False)]):
            invoice_date = datetime.strptime(invoice.date_invoice, DATE_FORMAT)
            if invoice_date < at_date:
                capital += invoice.amount_total_signed
        # If total amount of capital bought before 2020 is null, skip the coop
        if capital == 0:
            print(partner.name)
            continue
        try:
            (nom, prenom) = partner.name.split(',')
            coop = {
                'nom' : nom.strip(),
                'prenom' : prenom.strip(),
                'mail' : partner.email,
                'address' : "%s %s %s" % (partner.street, partner.zip, partner.city),
                'parts' : partner.total_partner_owned_share,
                'capital' : int(capital)
                }
            odoo_coops.append(coop)
        except:
            continue
    return odoo_coops

def save_to_xls(file_name, coops):
    DST_FILE = file_name
    next_row = 1
    wb = Workbook()
    ws = wb.active
    ws.title = 'Capital parts A au 31-12-2020'

    ws.append(('Nom', 'Prenom', 'Adresse', 'Nb de parts', 'Capital'))
    next_row += 1

    for coop in coops:
        ws.append((coop['nom'], coop['prenom'], coop['address'], coop['parts'], coop['capital']))
        next_row += 1

    wb.save(filename = DST_FILE)

def dump_to_csv(coops):
    print("%s;%s;%s" % ('Nom', 'Prenom', 'Email'))
    for coop in coops:
        print("%s;%s;%s" % (coop['nom'], coop['prenom'], coop['mail']))


at_date = datetime.strptime("2021-03-05", DATE_FORMAT)
#save_to_xls("out.xls", read_odoo_coops(at_date))
dump_to_csv(read_odoo_coops(at_date))
