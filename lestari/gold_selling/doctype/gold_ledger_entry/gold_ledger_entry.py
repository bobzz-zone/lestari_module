# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class GoldLedgerEntry(Document):
	@frappe.whitelist()
	def validate(self):
		if self.proses == "Penyerahan":
			kss = frappe.new_doc("Kartu Stock Sales")
			kss.item = self.item
			kss.bundle = self.bundle
			kss.kategori = self.kategori
			kss.sub_kategori = self.sub_kategori
			kss.kadar = self.kadar
			kss.warehouse = self.warehouse
			kss.qty = self.qty_in
			kss.flags.ignore_permissions = True
			kss.save()
		else:
			doc = frappe.db.get_list(doctype = "Kartu Stock Sales", filters={"bundle" : self.bundle, "item":self.item, "sub_kategori": self.sub_kategori})
			for col in doc:
				kss = frappe.get_doc("Kartu Stock Sales", col)
				if self.proses == "Penambahan":
					kss.qty = kss.qty + self.qty_in
				if self.proses == "Penyetoran":
					kss.qty = kss.qty - self.qty_out
				if self.proses == "Penjualan":
					kss.qty = kss.qty - self.qty_out
				kss.flags.ignore_permissions = True
				kss.save()