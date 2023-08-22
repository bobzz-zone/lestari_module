# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
import math
from frappe.model.document import Document

class SPKLilin(Document):
    @frappe.whitelist()
    def get_spk_produksi(self):
        from_spk = self.from_spk
        to_spk = self.to_spk
        spk = frappe.db.sql(
        """
        SELECT a.parent, a.qty, a.kadar, a.produk_id, b.rubber_mould, b.hasil_inject, b.name as resep FROM `tabSPK Produksi Detail` a
        JOIN `tabResep Mul Karet` b ON a.produk_id = b.final_product
        WHERE a.parent between '{}' and '{}'
        """.format(from_spk,to_spk),as_dict = 1)
        frappe.msgprint(str(spk))
        total_qty = 0
        total_inject = 0
        total_batu = 0
        for row in spk:
            inject = 0
            if row.resep:
                inject = math.ceil(row.qty / row.hasil_inject)
                frappe.msgprint(str(row))
                baris_baru = {
                    'no_spk': row.parent,
                    'produk': row.produk_id,
                    'kategori': frappe.db.get_value('Item', row.produk_id, 'item_group'),
                    'parts': row.rubber_mould,
                    'resep_mul_karet': row.resep,
                    'kadar': row.kadar,
                    'inject': inject,
                    'qty': row.qty
                }
                self.append('items',baris_baru)
                total_inject += inject
                total_qty += row.qty
                resep = frappe.get_doc('Resep Mul Karet', row.resep)
                batu = 0
                for col in resep.batu:
                    batu = col.qty * row.qty
                    baris_batu = {
                        'parts': row.rubber_mould,
                        'batu': col.batu,
                        'warna': col.color,
                        'qty': col.qty * row.qty,
                        'no_spk': row.parent
                    }
                    self.append('stones', baris_batu)
                    total_batu += batu
        self.total_qty = total_qty
        self.total_inject = total_inject
        self.total_batu = total_batu
