# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe.utils import now_datetime ,now
from frappe.utils import getdate
from datetime import datetime
from frappe.model.naming import getseries
from frappe.model.naming import make_autoname

class TransferBarangJadi(Document):
	@frappe.whitelist()
	def autoname(self):
		date = getdate(self.tanggal)
		tahun = date.strftime("%y")
		bulan = date.strftime("%m")
		hari = date.strftime("%d")
		# frappe.throw(str(self.naming_series))
		self.naming_series = self.naming_series.replace(".YY.", tahun).replace(".MM.", bulan).replace(".DD.", hari)
		self.name = self.naming_series.replace(".####", getseries(self.naming_series,4))
		
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
		print("-- Submitting Transfer Barang Jadi "+self.name+" DONE --")
		newdoc = frappe.new_doc("Transfer Stockist")
		newdoc.date = self.tanggal
		newdoc.transfer = "Transfer QC ke Stockist"
		newdoc.pic = self.employee
		newdoc.employee_penerima = self.penerima
		total_berat = 0
		for row in self.items:
			barang_jadi = {
				"sub_kategori": row.sub_kategori,
				"kadar": row.kadar,
				"qty_penambahan": row.berat,
				"note": row.keterangan,
			}
			total_berat += row.berat
		newdoc.append("items",barang_jadi)
		newdoc.total_berat = total_berat
		newdoc.flags.ignore_permissions = True
		newdoc.save()
		newdoc.submit()

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
