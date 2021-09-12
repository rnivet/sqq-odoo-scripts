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
            description='Corrige un problème de créneau')
    parser.add_argument('nom', help='Nom du membre (NOM, prenom)')
    parser.add_argument('--check', dest='check', default=False, action='store_true')
    parser.add_argument('--fix-template', dest='fix_template', default=False, action='store_true')
    parser.add_argument('--fix-ticket', dest='fix_ticket', default=False, action='store_true')
    args = parser.parse_args()

    # Get member from Odoo
    members = openerp.ResPartner.browse([("name", "=", args.nom)])
    if len(members) < 1:
        raise Exception('%s : Membre introuvable dans Odoo' % (args.nom))

    # Get shift registration for this member
    for reg in openerp.ShiftTemplateRegistration.browse(
            [ ("partner_id", "=", members[0].id) ]):
        tmpl = reg.shift_template_id
        ticket = reg.shift_ticket_id

        if tmpl == ticket.shift_template_id:
            continue

        if args.check:
            print("name=%s  date=%s  reg_tmpl=%s(%d)  ticket_tmpl=%s(%d)" %
                    (reg.shift_template_id.name, reg.date_open,
                        reg.shift_template_id.name, reg.shift_template_id.id,
                        reg.shift_ticket_id.shift_template_id.name,
                        reg.shift_ticket_id.shift_template_id.id))
            return

        if args.fix_template:
            reg.shift_template_id = ticket.shift_template_id
        elif args.fix_ticket:
            # Get the right ticket
            shift_type = "ftop" if tmpl.is_ftop else "standard"
            for ticket in openerp.ShiftTemplateTicket.browse(
                    [("shift_template_id", "=", tmpl.id),
                        ("shift_type", "=", shift_type)]):
                    print(shift_type, ticket.id, ticket.shift_type)
                    reg.shift_ticket_id = ticket
        print("name=%s  date=%s  reg_tmpl=%s(%d)  ticket_tmpl=%s(%d)" % (reg.shift_template_id.name, reg.date_open, reg.shift_template_id.name, reg.shift_template_id.id, reg.shift_ticket_id.shift_template_id.name, reg.shift_ticket_id.shift_template_id.id))

if __name__ == "__main__":
    main()
