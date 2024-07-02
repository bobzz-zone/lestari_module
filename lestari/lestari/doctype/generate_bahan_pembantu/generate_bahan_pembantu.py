# Copyright (c) 2024, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from lestari.lestari.doctype.pemakaian_bahan_pembantu_per_bulan.pemakaian_bahan_pembantu_per_bulan import generate_mr

class GenerateBahanPembantu(Document):
	@frappe.whitelist()
	def generate_random_mr(self):
		for row in self.detail:
			generate_mr(self.item_code,row.bulan,row.tahun)
		
		frappe.msgprint("Generate Done")

	@frappe.whitelist()
	def get_detail(self):
		doc = frappe.get_doc("Pemakaian Bahan Pembantu",self.bahan_pembantu)
		for row in doc.item:
			self.append("list_department",{
				"department":row.department,
				"persen":row.persen
			})
		
		list_doc = frappe.db.get_list("Pemakaian Bahan Pembantu Per Bulan", {"pemakaian_bahan_pembantu":self.bahan_pembantu})
		for col in list_doc:
			pbp = frappe.db.get_value('Pemakaian Bahan Pembantu Per Bulan', col, ['bulan', 'tahun', 'pemakaian'], as_dict=1)
			self.append("detail",{
				"bulan": pbp.bulan,
				"tahun": pbp.tahun,
				"pemakaian": pbp.pemakaian
			})