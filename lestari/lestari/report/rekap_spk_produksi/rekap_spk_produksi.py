# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe import _, _dict
from frappe.utils import getdate,flt

def execute(filters=None):
    columns = [
        {
            "label": _("No SPK"),
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "SPK Produksi",
            "width": 150
        },     
        {
            "label": _("No FO"),
            "fieldname": "form_order",
            "fieldtype": "Link",
            "options": "Form Order",
            "width": 120
        },     
        {
            "label": _("Posting Date"),
            "fieldname": "tanggal_spk",
            "fieldtype": "Date",
            "width": 110
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
            "width": 60
        },
        {
            "label": _("Sub Kategori"),
            "fieldname": "sub_kategori",
            "fieldtype": "Link",
            "options": "Item Group",
            "width": 120
        },
        {
            "label": _("Produk ID"),
            "fieldname": "produk_id",
            "fieldtype": "Link",
            "options": "Item",
            
        },
        {
            "label": _("Qty"),
            "fieldname": "qty",
            "fieldtype": "Int",
            "width": 50
        },
        {
            "label": _("Berat"),
            "fieldname": "berat",
            "fieldtype": "Float",
            "width": 100
        },
    ]

    conditions = " AND `tabSPK Produksi`.tanggal_spk BETWEEN %(from_date)s AND %(to_date)s"

    if filters.get("no_fo"):
        conditions += " AND `tabSPK Produksi`.form_order = %(no_fo)s"
    if filters.get("type"):
        conditions += " AND `tabSPK Produksi`.type = %(type)s"
    if filters.get("kadar"):
        conditions += " AND `tabSPK Produksi`.kadar = %(kadar)s"
    if filters.get("sub_kategori"):
        conditions += " AND `tabSPK Produksi`.sub_kategori = %(sub_kategori)s"
    # if filters.get("from_date"):
        

    query = """
        SELECT
            `tabSPK Produksi`.name,
            `tabSPK Produksi`.form_order,
            `tabSPK Produksi`.tanggal_spk,
            `tabSPK Produksi`.type,
            `tabSPK Produksi`.kadar,
            `tabSPK Produksi`.sub_kategori,
            `tabSPK Produksi Detail`.produk_id,
            `tabSPK Produksi Detail`.qty,
            `tabSPK Produksi Detail`.target_berat
        FROM
            `tabSPK Produksi`
        LEFT JOIN `tabSPK Produksi Detail` ON `tabSPK Produksi`.name = `tabSPK Produksi Detail`.parent
        WHERE `tabSPK Produksi`.docstatus = 1
        {0}
        ORDER BY `tabSPK Produksi`.form_order, `tabSPK Produksi`.kadar
    """.format(conditions)

    data = frappe.db.sql(query, filters, as_dict=True)

    return columns, data