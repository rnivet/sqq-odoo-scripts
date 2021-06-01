#! /usr/bin/env python3
# -*- encoding: utf-8 -*-


import sys
import erppeek
import csv
import unidecode
import traceback

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
# Configuration
###############################################################################

###############################################################################
# Script
###############################################################################
date_begin = "2021-06-07"
date_end = "2021-08-29"

for shift in openerp.ShiftShift.browse([("active", "=", True),
    "&", ("date_begin", ">=", date_begin), ("date_begin", "<=", date_end)]):
    print(shift)
    for ticket in shift.shift_ticket_ids:
        if ticket.shift_type == 'ftop':
            ticket.seats_max = 0
            print(ticket.available_seat_ftop)
    try:
        shift.button_cancel()
    except:
        pass
