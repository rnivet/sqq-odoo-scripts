#! /usr/bin/env python3
# -*- encoding: utf-8 -*-


import sys
import argparse
import erppeek
import csv
import unidecode
import traceback

from datetime import datetime
from dateutil import tz

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

openerp, uid, _ = init_openerp(
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

def main():
    # Configure arguments parser
    parser = argparse.ArgumentParser(
            description='Annule un echange de service')
    parser.add_argument('nom', help='Nom du membre (NOM, prenom)')
    parser.add_argument('shift',
            help='Date du service d\'origine à rétablir (28/02/2022 18:45)')
    args = parser.parse_args()

    # Check arg format
    date_service = None
    try:
        date_service = datetime.strptime(args.shift, '%Y-%m-%d %H:%M').\
                replace(tzinfo = tz.tzlocal())
    except Exception as e:
        raise Exception('%s : Mauvais format de date (AAAA-MM-JJ HH:MM)' %\
                (args.shift))

    # Get member from Odoo
    members = openerp.ResPartner.browse([("name", "=", args.nom)])
    if len(members) < 1:
        raise Exception('%s : Membre introuvable dans Odoo' % (args.nom))

    # Get service reg
    date_service_str = date_service.astimezone(tz.tzutc()).\
            strftime('%Y-%m-%d %H:%M:%S')
    for reg in openerp.ShiftRegistration.browse(
            [
                ("date_begin", "=", date_service_str),
                ("partner_id", "=", members[0].id)]):
        print(reg.id, reg.date_begin, reg.state, reg.exchange_state)
        reg.state = 'open'
        reg.exchange_state = 'draft'
        print(reg, reg.date_begin, reg.state, reg.exchange_state)

if __name__ == "__main__":
    main()
