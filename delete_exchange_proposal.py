#! /usr/bin/env python3
# -*- encoding: utf-8 -*-


import sys
import argparse
import erppeek
import csv
import unidecode

from datetime import datetime
from dateutil import tz
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
#reg_id = 39002
#for prop in openerp.Proposal.browse([("src_registration_id", "=", 39207)]):
#for prop in openerp.Proposal.browse(["|", ("src_registration_id", "=", reg_id), ("des_registration_id", "=", reg_id)]):
#for prop in openerp.Proposal.browse([]):
#    print(prop.state, prop.create_uid, prop.des_registration_id, prop.src_registration_id)

def main():
    # Configure arguments parser
    parser = argparse.ArgumentParser(
            description='Supprime les traces d\'echanges d\'un service')
    parser.add_argument('nom', help='Nom du membre (NOM, prenom)')
    parser.add_argument('date_service',
            help='Date du service (YYYY-MM-DD HH:MM)')
    args = parser.parse_args()

    # Check arg format
    date_service = None
    try:
        date_service = datetime.strptime(args.date_service, '%Y-%m-%d %H:%M').\
                replace(tzinfo = tz.tzlocal())
    except Exception as e:
        raise Exception('%s : Mauvais format de date (AAAA-MM-JJ HH:MM)' %\
                (args.date_service))

    # Get member from Odoo
    members = openerp.ResPartner.browse([("name", "=", args.nom)])
    if len(members) < 1:
        raise Exception('%s : Membre introuvable dans Odoo' % (args.nom))

    # Get shift registration for this member
    date_service_str = date_service.astimezone(tz.tzutc()).\
            strftime('%Y-%m-%d %H:%M:%S')
    for reg in openerp.ShiftRegistration.browse(
            [
                ("partner_id", "=", members[0].id),
                ("date_begin", "=", date_service_str)
            ]):
        print(reg)
        # Get related proposals if any
        for prop in openerp.Proposal.browse(
                [
                    "|",
                    ("src_registration_id", "=", reg.id),
                    ("des_registration_id", "=", reg.id)
                ]):
            print(prop)
            prop.unlink()


if __name__ == "__main__":
    main()
