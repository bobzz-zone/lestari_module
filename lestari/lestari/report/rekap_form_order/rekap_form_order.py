# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe import _, _dict
from frappe.utils import getdate,flt

def execute(filters=None):
    columns = [
        {
            "label": _("No FO"),
            "fieldname": "no_fo",
            "fieldtype": "Link",
            "options": "Form Order",
            "width": 120
        },     
        {
            "label": _("Posting Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 90
        },
        {
            "label": _("Type"),
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
        {
            "label": _("Sub Kategori"),
            "fieldname": "sub_kategori",
            "fieldtype": "Link",
            "options": "Item Group",
            "width": 120
        },
        {
            "label": _("Kategori"),
            "fieldname": "kategori",
            "fieldtype": "Link",
            "options": "Item Group",
            "width": 120
        },
        {
            "label": _("Jenis"),
            "fieldname": "model",
            "fieldtype": "Link",
            "options": "Item",
            "width": 120
        },
        {
            "label": _("Qty"),
            "fieldname": "qty",
            "fieldtype": "Int",
            "width": 120
        },
        {
            "label": _("Berat"),
            "fieldname": "berat",
            "fieldtype": "Float",
            "width": 120
        },
    ]

    conditions = " AND `tabForm Order`.posting_date BETWEEN %(from_date)s AND %(to_date)s"

    if filters.get("no_fo"):
        conditions += " AND `tabForm Order`.no_fo = %(no_fo)s"
    if filters.get("type"):
        conditions += " AND `tabForm Order`.type = %(type)s"
    if filters.get("kadar"):
        conditions += " AND `tabForm Order`.kadar = %(kadar)s"
    if filters.get("sub_kategori"):
        conditions += " AND `tabForm Order`.sub_kategori = %(sub_kategori)s"
    if filters.get("kategori"):
        conditions += " AND `tabForm Order`.kategori = %(kategori)s"
    # if filters.get("from_date"):
        

    query = """
        SELECT
            `tabForm Order`.no_fo,
            `tabForm Order`.posting_date,
            `tabForm Order`.type,
            `tabForm Order`.kadar,
            `tabForm Order`.kategori,
            `tabForm Order`.sub_kategori,
            `tabForm Order Item`.model,
            `tabForm Order Item`.qty,
            `tabForm Order Item`.berat
        FROM
            `tabForm Order`
        LEFT JOIN `tabForm Order Item` ON `tabForm Order`.name = `tabForm Order Item`.parent
        WHERE `tabForm Order`.docstatus = 1
        {0}
        ORDER BY `tabForm Order`.posting_date ASC
    """.format(conditions)

    data = frappe.db.sql(query, filters, as_dict=True)

    return columns, data