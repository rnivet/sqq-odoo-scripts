#! /usr/bin/env python3
# -*- encoding: utf-8 -*-


import sys
import traceback
import erppeek
import csv
import unidecode

from datetime import date, datetime, timedelta

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

def generate_tmpl_tuples():
    for week in ('A', 'B', 'C', 'D'):
        for day in ('Lun', 'Mer', 'Jeu', 'Ven'):
            for start in (
                    ('12:30', '13:45'),
                    ('15:30', '16:15'),
                    ('18:30', '18:45')):
                yield ("%s%s. - %s" % (week, day, start[0]),
                        "%s%s. - %s" % (week, day, start[1]))
        for start in (
                ('12:00', '13:45'),
                ('15:00', '16:15'),
                ('18:00', '18:45')):
            yield ("%sSam. - %s" % (week, start[0]),
                    "%sSam. - %s" % (week, start[1]))

def migrate_template(cur_tmpl, new_tmpl, start_date, limit=None):
    current_templates = openerp.ShiftTemplate.browse([("name", "=", cur_tmpl)])
    new_templates = openerp.ShiftTemplate.browse( [("name", "=", new_tmpl)])

    print("Migrating template [%s] to [%s]" % (
            current_templates[0].read("display_name"),
            new_templates[0].read("display_name")))

    for reg in openerp.ShiftTemplateRegistration.browse(
            [("shift_template_id", "=", current_templates[0].id)],
            limit = limit):
        print(reg.partner_id)

        future_lines = [x for x in reg.line_ids if x.read('is_future') is True]
        if len(future_lines) > 0:
            print("[Partner is in leave - Migration aborted]")
            continue

        current_lines = [x for x in reg.line_ids if x.read('is_current') is True]
        if len(current_lines) > 0:
            if current_lines[0].date_end:
                print("[A change in future is already planned", "-",
                        "Migration aborted]")
                continue

            new_team_change_data = {
                    "partner_id": reg.partner_id.id,
                    "current_shift_template_id": current_templates[0].id,
                    "new_shift_template_id": new_templates[0].id,
                    "new_next_shift_date": start_date,
                    }
            try:
                new_team_change = openerp.ShiftChangeTeam.create(
                        new_team_change_data)
                try:
                    new_team_change.btn_change_team_process()
                except:
                    pass
                new_team_change.button_close()
                print("[Migrated]")
            except:
                print("[Migration failed]")
                traceback.print_exc()
        else:
            print("[Partner has no current line - Migration aborted]")

def main():
    #for tmpl in generate_tmpl_tuples():
    #    migrate_template(tmpl[0], tmpl[1], "2020/06/18")
    #tmpl = next(generate_tmpl_tuples())
    migrate_template("Service volants - DSam. - 21:00",
            "Service volants - BSam. - 21:00",
            "2021/10/11",
            350)

if __name__ == "__main__":
    main()
