#! /usr/bin/env python3
# -*- encoding: utf-8 -*-


import sys
import argparse
import erppeek

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
# Script
###############################################################################
def parse_args():
    parser = argparse.ArgumentParser(
            description='Find product with archive state desynchronized \
                    between template and product')

    return parser.parse_args()

def main():
    # Configure arguments parser
    args = parse_args()

    count = 0
    for product in openerp.ProductProduct.browse([("active", "=", False)]):
        template = product.product_tmpl_id
        if template.active is not False:
            count +=1
            print(template.name, template.active)
            print(product.name, product.active)
    print("Total articles : ", count)

if __name__ == "__main__":
    main()
