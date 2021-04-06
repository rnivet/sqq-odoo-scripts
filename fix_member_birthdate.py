#! /usr/bin/env python3
# -*- encoding: utf-8 -*-


import sys
import argparse
import erppeek
import csv
import unidecode

from datetime import datetime
from cfg_secret_configuration \
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
# Configuration
###############################################################################

###############################################################################
# Script
###############################################################################

def main():
    # Configure arguments parser
    parser = argparse.ArgumentParser(
            description='Force la date de naissance du membre au bon format')
    parser.add_argument('nom', help='Nom du membre (NOM, prenom)')
    parser.add_argument('date_naissance',
            help='Date de naissance (YYYY-MM-DD)')
    args = parser.parse_args()

    # Check arg format
    try:
        datetime.strptime(args.date_naissance, '%Y-%m-%d')
    except Exception as e:
        raise Exception('%s : Mauvais format de date (AAAA-MM-JJ)' %\
                (args.date_naissance))

    # Get member from Odoo
    member = openerp.ResPartner.browse([("name", "=", args.nom)])
    if len(member) < 1:
        raise Exception('%s : Membre introuvable dans Odoo' % (args.nom))

    print('Date de naissance avant : %s' % (member[0].birthdate))
    print('Modification...')
    member[0].birthdate = args.date_naissance
    print('Date de naissance après : %s' % (member[0].birthdate))

if __name__ == "__main__":
    main()
