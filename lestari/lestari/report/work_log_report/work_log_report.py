# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    columns = [
        {
            "label": _("Employee"),
            "fieldname": "employee",
            "fieldtype": "Link",
            "options": "Employee",
            "width": 120
        },
        {
            "label": _("SSKO"),
            "fieldname": "ssko",
            "fieldtype": "Link",
            "options": "SSKO",
            "width": 120
        },
        {
            "label": _("Date"),
            "fieldname": "date",
            "fieldtype": "Date",
            "width": 90
        },
        {
            "label": _("Start Time"),
            "fieldname": "start_time",
            "fieldtype": "Time",
            "width": 90
        },
        {
            "label": _("End Time"),
            "fieldname": "end_time",
            "fieldtype": "Time",
            "width": 90
        },
        {
            "label": _("Duration (Minutes)"),
            "fieldname": "duration",
            "fieldtype": "Float",
            "width": 120
        }
    ]

    conditions = "WHERE DATE_FORMAT(`tabWork Log`.start_time, '%Y') = %(year)s \
                  AND DATE_FORMAT(`tabWork Log`.start_time, '%m') = %(month)s \
                  AND DATE_FORMAT(`tabWork Log`.start_time, '%u') = %(day_of_week)s"

    if filters.get("ssko"):
        conditions += " AND `tabWork Log`.ssko = %(ssko)s"

    query = """
        SELECT
            `tabEmployee`.name AS employee,
            `tabSPKO`.name AS spko,
            `tabWork Log`.waktu_mulai AS start_time,
            `tabWork Log`.waktu_selesai AS end_time,
            TIMESTAMPDIFF(SECOND, `tabWork Log`.start_time, `tabWork Log`.end_time) AS duration,
            `tabWork Log`.work_date AS date
        FROM
            `tabWork Log`
        LEFT JOIN `tabEmployee` ON `tabEmployee`.name = `tabWork Log`.employee
        LEFT JOIN `tabSPKO` ON `tabSPKO`.name = `tabWork Log`.spko
        {0}
        ORDER BY `tabWork Log`.start_time ASC
    """.format(conditions)

    data = frappe.db.sql(query, filters, as_dict=True)

    return columns, data