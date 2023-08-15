# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class KonfirmasiReturnSubkategori(Document):
    def on_submit(self):
        pass
        # doc = frappe.get_doc("Konfirmasi Payment Return", self.no_konfirmasi)
        # for row in self.items:pass	
    @frappe.whitelist()
    def get_konfirmasi(self):
        doc = frappe.get_doc("Konfirmasi Payment Return", self.no_konfirmasi)
        terima_berat = 0
        total_berat_input = 0
        if doc.detail_perhiasan:
            for row in doc.detail_perhiasan:
                if row.is_out == 0 and row.is_confirm == 0:
                    total_berat_input += row.terima_qty
                    terima_berat += row.terima_qty
                    baris_baru = {
						'idx_konfirmasi': row.idx,
						'item': row.item,
						# 'sub_kategori': frappe.db.get_value('Item', {'item_code': row.item}, ['item_group']),
						'terima_berat': row.terima_qty,
						'berat_pembayaran': row.qty,
						'customer':row.customer,
						'voucher_type':row.voucher_type,
						'voucher_no':row.voucher_no,
						'child_table':row.doctype,
						'child_id':row.name
					}
                    self.append("items",baris_baru)
                else:
                    frappe.msgprint("Konfirmasi Payment Return Sudah tidak ada yang bisa di Return")
        else:
            frappe.msgprint("Konfirmasi Payment Return Tidak ada Return Perhiasan")
        self.terima_berat = terima_berat
        self.total_berat_input = total_berat_input
		# if doc.detail_rongsok:
		# 	for row in doc.detail_rongsok:
		# 		if row.is_out == 0 and row.is_confirm == 0:
		# 			self.total_berat_input += row.terima_qty
		# 			baris_baru = {
		# 				'idx_konfirmasi': row.idx,
		# 				'item': row.item,
      	# 				# 'sub_kategori': frappe.db.get_value('Item', {'item_code': row.item}, ['item_group']),
		# 				'terima_berat': row.terima_qty,
		# 				'berat_pembayaran': row.qty,
		# 				'customer':row.customer,
		# 				'voucher_type':row.voucher_type,
		# 				'voucher_no':row.voucher_no,
		# 				'child_table':row.doctype,
		# 				'child_id':row.name
		# 			}
		# 		self.append("items",baris_baru)
