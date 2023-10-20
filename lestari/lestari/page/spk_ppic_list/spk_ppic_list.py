# Copyright (c) 2021, Patrick Stuhlmüller and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import *
import json

@frappe.whitelist()
def make_spk_ppic(data,posting_date = None):

    for row in json.loads(data):
        doc = frappe.get_doc("Form Order", row)
        new_doc = frappe.new_doc("SPK Produksi")
        new_doc.name = doc.type+doc.name
        new_doc.idworksuggestion = doc.idworksuggestion
        new_doc.employee_id = frappe.db.get_value("Employee",{"user_id":frappe.session.user},"name")
        new_doc.type = doc.type
        new_doc.sub_kategori = doc.sub_kategori
        new_doc.kadar = doc.kadar
        new_doc.tanggal_spk = posting_date
        new_doc.form_order = doc.name
        tot_jumlah = 0
        model = []
        for col in doc.items_valid:
            tot_jumlah += col.qty
            if len(model) == 0:
                model.append(col.model)
            if len(model) > 0 and not col.model in model:
                model.append(col.model)
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
            col.spk_ppic = new_doc.name
            doc.status = "Ordered PPIC"
            doc.flags.ignore_permissions = True
            doc.save()
        new_doc.total_model = len(model)
        new_doc.total_jumlah = tot_jumlah
        new_doc.flags.ignore_permissions = True
        new_doc.save()
        new_doc.submit()      
        frappe.msgprint("SPK PPIC Berhasil dibuat dengan Nomor"+str(new_doc))

@frappe.whitelist()
def contoh_report():
    fm = []
    # list_doc = frappe.get_list("Form Order", filters={'docstatus':1},order_by="posting_date DESC",limit = 5000)
    list_doc = frappe.db.sql("""
        SELECT name
        FROM `tabForm Order`
        WHERE docstatus = 1
        AND posting_date like "2023-10%"    
        ORDER BY posting_date ASC
    """,as_dict = 1)
    no = 0
    for row in list_doc:
        doc = frappe.get_doc("Form Order", row)
        for col in doc.items_valid:
            if col.spk_ppic == "" or not col.spk_ppic:
                no+=1
                baris_baris = {
                    'no' : no,
                        'name' : str(doc.name),
                        'form_order' : str(doc.idworksuggestion),
                        'urut_fm' : str(col.idx),
                        'model' : col.model,
                        'qty' : col.qty,
                        'berat' : col.total_berat,
                        'posting_date' : frappe.format(doc.posting_date,{'fieldtype':'Date'}),
                        # 'posting_date' : frappe.date.datetime(doc.posting_date,"M/d/yyyy"),
                        'kadar' : doc.kadar,
                        'kategori' : doc.kategori,
                        'sub_kategori' : doc.sub_kategori,
                }
                fm.append(baris_baris)
    # frappe.msgprint(str(fm))  
    return fm   