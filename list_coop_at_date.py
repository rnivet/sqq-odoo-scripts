#! /usr/bin/env python3
# -*- encoding: utf-8 -*-


import sys
import erppeek
import argparse

from datetime import datetime
from openpyxl import load_workbook, Workbook

from cfg_secret_configuration\
        import odoo_configuration_user_test as odoo_configuration_user

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

def read_odoo_coops(at_date):
    odoo_coops = []

    partners = openerp.ResPartner.browse([
        ("is_member", "=", True),
        ("active", "in", [True, False])])
    for partner in partners:
        # Find all capital invoices for the partner
        capital = 0
        for invoice in openerp.AccountInvoice.browse([
                ("partner_id", "=", partner.id),
                ("is_capital_fundraising", "=", True),
                ("state", "=", "paid"),
                ("date_invoice", "!=", False)]):
            invoice_date = datetime.strptime(invoice.date_invoice, '%Y-%m-%d')
            if invoice_date < at_date:
                capital += invoice.amount_total_signed
        # If total amount of capital bought before 2020 is null, skip the coop
        if capital == 0:
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
            print(partner.name)
            continue
    return odoo_coops

def save_to_xls(file_name, date, coops):
    DST_FILE = file_name
    next_row = 1
    wb = Workbook()
    ws = wb.active
    ws.title = 'Capital parts A au ' + date.replace('/', '-')

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


def main():
    # Configure arguments parser
    parser = argparse.ArgumentParser(
            description=('Liste les cooperateurs',
            ' possesseurs de parts à une date donnée'))
    parser.add_argument('date',
            help='Date effective (31/12/2022)')
    args = parser.parse_args()

    # Check arg format
    at_date = None
    try:
        at_date = datetime.strptime(args.date, '%d/%m/%Y')
    except Exception as e:
        raise Exception('%s : Mauvais format de date (JJ/MM/AAAA)' %\
                (args.date))

    coop_list = read_odoo_coops(at_date)
    save_to_xls("out.xls", args.date, coop_list)
    #dump_to_csv(coop_list)

if __name__ == "__main__":
    main()
