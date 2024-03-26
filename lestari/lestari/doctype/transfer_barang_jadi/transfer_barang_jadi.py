# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TransferBarangJadi(Document):
	@frappe.whitelist()
	def validate(self):
		tot_berat = 0
		tot_qty = 0
		for row in self.items:
			tot_berat += row.berat
			tot_qty += row.qty
		self.total_qty = tot_qty
		self.total_berat = tot_berat
	
	@frappe.whitelist()
	def on_submit(self):
		new_doc = frappe.new_doc("Stock Entry")
		new_doc.stock_entry_type = "Material Receipt"
		new_doc.posting_date = self.posting_date
		new_doc.posting_time = self.posting_time
		new_doc.set_posting_time = 1
		new_doc.remarks = self.name
		for row in self.items:
			alloy = frappe.db.get_value("Data Logam", row.kadar, 'alloy')
			item_code = row.sub_kategori+"-"+row.kadar+alloy
			# frappe.throw(item_code)
			baris_baru = {
				't_warehouse' : 'Stockist - LMS',
				'item_code' : item_code,
				'qty': row.berat,
				'pcs': row.qty,
				'uom':'Gram',
				'allow_zero_valuation_rate':1
			}
		new_doc.append('items',baris_baru)
		new_doc.flags.ignore_permissions = True
		new_doc.save()
		new_doc.submit()
			

@frappe.whitelist()
def get_spk_ppic(no_spk,kadar):
	spk = frappe.get_doc('SPK Produksi', no_spk)
	detail_spk = {}
	for row in spk.tabel_rencana_produksi:
		if row.kadar == kadar:
			detail_spk = {
				'kadar' : row.kadar,
				'sub_kategori' : row.sub_kategori,
				'no_fo' : row.form_order,
			}
	return detail_spk
