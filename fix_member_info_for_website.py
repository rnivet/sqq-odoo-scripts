#! /usr/bin/env python3
# -*- encoding: utf-8 -*-


import sys
import argparse
import erppeek
import csv
import unidecode

from datetime import datetime
from dateutil import tz
from cfg_secret_configuration import \
        odoo_configuration_user_test as odoo_configuration_user

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
            description='Force le bypass du paiement dans le shop')
    args = parser.parse_args()

    for member in openerp.ResPartner.browse([("is_worker_member", "=", True)]):
        if member.skip_website_checkout_payment is False:
            member.skip_website_checkout_payment = True
        if member.country_id is False:
            member.country_id = openerp.ResCountry.get(76)
        if member.phone is False and member.mobile is not False:
            member.phone = member.mobile
        print("%s, skip_payment=%s, country=%s, phone=%s" % (member.name,
            member.skip_website_checkout_payment,
            member.country_id,
            member.phone))

if __name__ == "__main__":
    main()
