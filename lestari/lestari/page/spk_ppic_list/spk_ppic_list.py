# Copyright (c) 2021, Patrick Stuhlmüller and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import *
import json

@frappe.whitelist()
def make_spk_ppic(data):
    for row in json.loads(data):
        doc = frappe.get_doc("Form Order", row)
        new_doc = frappe.new_doc("SPK Produksi")
        new_doc.idworksuggestion = doc.idworksuggestion
        new_doc.employee_id = frappe.db.get_value("Employee",{"user_id":frappe.session.user},"name")
        for col in doc.items_valid:
            baris_baru = {
                'form_order': doc.name,
                'tanggal_order': doc.posting_date,
                'so_type': doc.type,
                'kadar': col.kadar,
                'kategori': col.kategori,
                'sub_kategori': col.sub_kategori,
                'produk_id': col.model,
                'qty': col.qty,
                'qty_isi_pohon': col.qty_isi_pohon,
                'target_berat': col.total_berat,
                'keterangan_variasi': col.keterangan_variasi,
                'keternagan_batu': col.keterangan_batu
            }
            new_doc.append('tabel_rencana_produksi', baris_baru)
        new_doc.flags.ignore_permissions = True
        new_doc.save()
        new_doc.submit()
        
        frappe.msgprint(str(new_doc))

@frappe.whitelist()
def contoh_report():
    fm = []
    list_doc = frappe.get_list("Form Order", limit = 5000)
    no = 0
    for row in list_doc:
        doc = frappe.get_doc("Form Order", row)
        for col in doc.items_valid:
            no+=1
            baris_baris = {
                'no' : no,
                    'name' : str(doc.name),
                    'form_order' : str(doc.idworksuggestion),
                    'urut_fm' : str(col.idx),
                    'model' : col.model,
                    'qty' : col.qty,
                    'berat' : 0,
                    'posting_date' : frappe.format(doc.posting_date,{'fieldtype':'Date'}),
                    # 'posting_date' : frappe.date.datetime(doc.posting_date,"M/d/yyyy"),
                    'kadar' : doc.kadar,
                    'kategori' : doc.kategori,
                    'sub_kategori' : doc.sub_kategori,
            }
            fm.append(baris_baris)
    # frappe.msgprint(str(fm))  
    return fm   