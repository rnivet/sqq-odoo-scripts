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
            description='Liste les problèmes de créneau')
    args = parser.parse_args()

    for member in openerp.ResPartner.browse(
            [("active", "=", True),
                ("is_worker_member", "=", True),
                ("is_unsubscribed", "=", False)]
            ):

        for reg in openerp.ShiftTemplateRegistration.browse(
                [("partner_id", "=", member.id)]):
            for l in filter(lambda x: x.is_current is True, reg.line_ids):
                if l.shift_template_id != l.shift_ticket_id.shift_template_id:
                    print(member, member.email)
                    print(l.date_begin, l.date_end, l.shift_template_id, l.shift_ticket_id.shift_template_id)

if __name__ == "__main__":
    main()
