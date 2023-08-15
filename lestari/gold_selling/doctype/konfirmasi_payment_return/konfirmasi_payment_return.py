# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class KonfirmasiPaymentReturn(Document):
    def on_submit(self):
        ste = frappe.new_doc('Stock Entry')
        ste.stock_entry_type = "Material Transfer"
        if self.detail_perhiasan:
            for row in self.detail_perhiasan:
                if row.tolak_qty > 0:
                    baris_baru = {
                        's_warehouse' : self.s_warehouse,
                        't_warehouse' : self.t_warehouse,
                        'item_code' : row.item,
                        'qty' : row.tolak_qty,
                        'allow_zero_valuation_rate' : 1
                    }
                    ste.append('items', baris_baru)
                else:
                    return
        if self.detail_rongsok:
            for row in self.detail_rongsok:
                if row.tolak_qty > 0:
                    baris_baru = {
                        's_warehouse' : self.s_warehouse,
                        't_warehouse' : self.t_warehouse,
                        'item_code' : row.item,
                        'qty' : row.tolak_qty,
                        'allow_zero_valuation_rate' : 1
                    }
                    ste.append('items', baris_baru)
                else:
                    return
        if len(ste.items) <= 1:
            ste.flags.ignore_permissions = True
            ste.save()
	
    @frappe.whitelist()
    def get_serah_terima(self):
        doc = frappe.get_doc("Serah Terima Payment Stock", self.serah_terima)
        for row in doc.details:
            if frappe.db.get_value('Item', {'item_code': row.item}, ['item_group']) == "Rongsok":
                if row.sudah_cek == 0:
                    self.total_berat += row.qty
                    rongsok = {
						'item': row.item,
						'qty': row.qty,
						'kadar': frappe.db.get_value('Item', {'item_code': row.item}, ['kadar']),
						'voucher_type': row.voucher_type,
						'voucher_no': row.voucher_no,
                        'customer': frappe.db.get_value(str(row.voucher_type), {'name': row.voucher_no}, ['customer']),
                        'child_id': row.child_id
					}
                    self.append("detail_rongsok",rongsok)
            if frappe.db.get_value('Item', {'item_code': row.item}, ['item_group']) == "Perhiasan":
                if row.sudah_cek == 0:
                    self.total_berat += row.qty
                    perhiasan = {
						'item': row.item,
						'qty': row.qty,
                        'kadar': frappe.db.get_value('Item', {'item_code': row.item}, ['kadar']),
						'voucher_type': row.voucher_type,
						'voucher_no': row.voucher_no,
                        'customer': frappe.db.get_value(str(row.voucher_type), {'name': row.voucher_no}, ['customer']),
                        'child_id': row.child_id
					}
                    self.append("detail_perhiasan",perhiasan)
