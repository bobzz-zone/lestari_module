# Copyright (c) 2021, Patrick Stuhlmüller and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

@frappe.whitelist()
def contoh_report():
    tfs = []
    list_doc = frappe.get_list("Update Bundle Stock")
    no = 0
    for row in list_doc:
        doc = frappe.get_doc("Update Bundle Stock", row)
        for col in doc.items:
            no+=1
            baris_baris = {
                'no' : no,
                'sub_kategori' : col.sub_kategori,
                'kadar' : col.kadar,
                'qty' : col.qty_penambahan,
                'item' : col.item,
                'kategori' : col.kategori,
                'name' : doc.name,
                'posting_date' : frappe.format(doc.date,{'fieldtype':'Date'}),
                'bundle' : doc.bundle,
                'type' : doc.type,
                'nama_stokist' : doc.nama_stokist,
                'sales' : doc.sales,
                'warehouse' : doc.warehouse
            }
            tfs.append(baris_baris)
    # frappe.msgprint(str(po))  
    return tfs   