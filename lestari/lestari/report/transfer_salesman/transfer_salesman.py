# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe import _, _dict
from frappe.utils import getdate,flt

def execute(filters=None):
    columns = [
        {
            "label": _("ID"),
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Update Bundle Stock",
            "width": 120
        },     
        {
            "label": _("Bundle"),
            "fieldname": "bundle",
            "fieldtype": "Link",
            "options": "Sales Stock Bundle",
            "width": 120
        },     
        {
            "label": _("Sales"),
            "fieldname": "sales",
            "fieldtype": "Link",
            "options": "Sales Partner",
            "width": 200
        },     
        {
            "label": _("Pendamping"),
            "fieldname": "pendamping",
            "fieldtype": "Link",
            "options": "Sales Partner",
            "width": 200
        },     
        {
            "label": _("Posting Date"),
            "fieldname": "date",
            "fieldtype": "Date",
            "width": 120
        },
        {
            "label": _("Aktifitas"),
            "fieldname": "type",
            "fieldtype": "Data",
            "width": 90
        },
        {
            "label": _("Kadar"),
            "fieldname": "kadar",
            "fieldtype": "Link",
            "options": "Data Logam",
            "width": 120
        },
    ]

    conditions = " AND `tabUpdate Bundle Stock`.date BETWEEN %(from_date)s AND %(to_date)s"

    if filters.get("name"):
        conditions += " AND `tabUpdate Bundle Stock`.name = %(name)s"
    if filters.get("sales"):
        conditions += " AND `tabUpdate Bundle Stock`.sales = %(sales)s"
    if filters.get("pendamping"):
        conditions += " AND `tabSales Stock Bundle`.pendamping = %(pendamping)s"
    if filters.get("bundle"):
        conditions += " AND `tabUpdate Bundle Stock`.bundle = %(bundle)s"
    if filters.get("type"):
        conditions += " AND `tabUpdate Bundle Stock`.type = %(type)s"
    if filters.get("kadar"):
        conditions += " AND `tabUpdate Bundle Stock`.kadar = %(kadar)s"

    query = """
        SELECT
            `tabUpdate Bundle Stock`.name,
            `tabUpdate Bundle Stock`.sales,
            `tabUpdate Bundle Stock`.bundle,
            `tabSales Stock Bundle`.pendamping,
            `tabUpdate Bundle Stock`.date,
            `tabUpdate Bundle Stock`.type,
            `tabDetail Penambahan Stock`.kadar,
            `tabDetail Penambahan Stock`.qty_penambahan
        FROM
            `tabUpdate Bundle Stock`
        LEFT JOIN `tabDetail Penambahan Stock` ON `tabUpdate Bundle Stock`.name = `tabDetail Penambahan Stock`.parent
        LEFT JOIN `tabSales Stock Bundle` ON `tabUpdate Bundle Stock`.bundle = `tabSales Stock Bundle`.name
        WHERE `tabUpdate Bundle Stock`.docstatus = 1
        {0}
        ORDER BY `tabUpdate Bundle Stock`.date ASC, `tabDetail Penambahan Stock`.kadar ASC 
    """.format(conditions)

    data = frappe.db.sql(query, filters, as_dict=True)

    return columns, data