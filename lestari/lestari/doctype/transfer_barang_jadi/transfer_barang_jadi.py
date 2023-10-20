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
