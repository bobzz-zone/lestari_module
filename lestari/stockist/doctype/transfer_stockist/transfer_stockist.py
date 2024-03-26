# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime ,now
from frappe.utils import getdate
from datetime import datetime
from frappe.model.naming import getseries
from frappe.model.naming import make_autoname

class TransferStockist(Document):
	@frappe.whitelist()
	def autoname(self):
		date = getdate(self.date)
		tahun = date.strftime("%y")
		bulan = date.strftime("%m")
		hari = date.strftime("%d")
		# frappe.throw(str(self.naming_series))
		self.naming_series = self.naming_series.replace(".YY.", tahun).replace(".MM.", bulan).replace(".DD.", hari)
		self.name = self.naming_series.replace(".####", getseries(self.naming_series,4))
	def validate(self):
		self.status = 'Draft'
	def on_submit(self):
		print("-- Submitting Transfer Stockist "+self.name+" DONE --")
		ste = frappe.new_doc("Stock Entry")
		ste.stock_entry_transfer = "Transfer QC ke Stockist"
		ste.employee_id = self.pic
		ste.posting_date = self.date
		ste.remarks = self.keterangan
		ste.update_bundle_stock_no = self.name
		for row in self.items:
			doc = frappe.db.sql("""
                              SELECT item_code FROM `tabItem` WHERE kadar = "{}" and item_code LIKE "{}%" LIMIT 1
                              """.format(row.kadar,row.sub_kategori),as_dict=True)
			baris_baru = {
				'item_code' : doc[0].item_code,
				's_warehouse' : self.s_warehouse,
				't_warehouse' : self.t_warehouse,
				'qty' : row.qty_penambahan,
				'allow_zero_valuation_rate' : 1
			}
			ste.append("items",baris_baru)
		ste.flags.ignore_permissions = True
		ste.save()
		print("-- Submitting Stock Entry "+ste.name+" DONE --")
		print("-- DONE --")
		self.status = frappe.db.sql("""UPDATE `tabTransfer Stockist` SET status = "Submitted" where name = "{0}" """.format(self.name))
	def on_cancel(self):
		self.status = 'Cancelled'