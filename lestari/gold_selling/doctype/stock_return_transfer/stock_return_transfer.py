# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class StockReturnTransfer(Document):
	@frappe.whitelist()
	def get_kpr(self):
		# frappe.msgprint(self.type)
		if self.type == "Keluar":
			if self.customer:
				list_kpr = frappe.db.get_list("Konfirmasi Payment Return",filters={'customer':self.customer,'sales':self.sales, 'docstatus':1})
			else:
				list_kpr = frappe.db.get_list("Konfirmasi Payment Return",filters={'sales':self.sales, 'docstatus':1})
			for row in list_kpr:
				# frappe.msgprint(str(row))
				doc = frappe.get_doc("Konfirmasi Payment Return", row)
				for col in doc.detail_perhiasan:
					if col.is_out != 1:
						if col.tolak_qty > 0:
							customer = self.customer
							if not self.customer:
								customer = frappe.db.get_value(col.voucher_type,col.voucher_no,'customer')
							if self.sub_customer:
								subcustomer = self.sub_customer
								perhiasan = {
								'item': col.item,
								'berat': col.tolak_qty,
								'customer': customer,
								'sub_customer': subcustomer,
								'kadar':frappe.db.get_value("Item",col.item,'kadar'),
								'voucher_type': col.voucher_type,
								'voucher_no': col.voucher_no,
								'child_type':col.doctype,
								'child_name':col.name,
							}
							else:
								subcustomer = frappe.db.get_value(col.voucher_type,col.voucher_no,'subcustomer')
								perhiasan = {
								'item': col.item,
								'berat': col.tolak_qty,
								'customer': customer,
								'sub_customer': subcustomer,
								'kadar':frappe.db.get_value("Item",col.item,'kadar'),
								'voucher_type': col.voucher_type,
								'voucher_no': col.voucher_no,
								'child_type':col.doctype,
								'child_name':col.name,
							}
							self.append("transfer_details",perhiasan)
				for col in doc.detail_rongsok:
					if col.is_out != 1:
						if col.tolak_qty > 0:
							customer = self.customer
							if not self.customer:
								customer = frappe.db.get_value(col.voucher_type,col.voucher_no,'customer')
							if self.sub_customer:
								subcustomer = self.sub_customer
								rongsok = {
									'item': col.item,
									'berat': col.tolak_qty,
									'customer': customer,
									'sub_customer': subcustomer,
									'kadar':frappe.db.get_value("Item",col.item,'kadar'),
									'voucher_type': col.voucher_type,
									'voucher_no': col.voucher_no,
									'child_type':col.doctype,
									'child_name':col.name,
								}
							else:
								subcustomer = frappe.db.get_value(col.voucher_type,col.voucher_no,'subcustomer')
								rongsok = {
									'item': col.item,
									'berat': col.tolak_qty,
									'customer': customer,
									'sub_customer': subcustomer,
									'kadar':frappe.db.get_value("Item",col.item,'kadar'),
									'voucher_type': col.voucher_type,
									'voucher_no': col.voucher_no,
									'child_type':col.doctype,
									'child_name':col.name,
								}
							self.append("transfer_details",rongsok)
		else:
			doc = frappe.get_doc("Stock Return Transfer",self.no_doc)
			self.sales = doc.sales
			self.warehouse = doc.warehouse
			self.customer = doc.customer
			self.sub_customer = doc.sub_customer
			for row in doc.transfer_details:
				details = {
							'item': row.item,
							'berat': row.berat,
							'customer': row.customer,
							'sub_customer': row.sub_customer,
							'kadar':row.kadar,
							'kategori':row.kategori,
							'voucher_type': row.voucher_type,
							'voucher_no': row.voucher_no,
							'child_type':row.child_type,
							'child_name':row.child_name,
						}
				self.append("transfer_details",details)
			# list_kpr = frappe.db.get_list("Stock Return Transfer",filters={'sales':self.sales,'type':"Keluar"})
			# for row in list_kpr:
			# 	doc = frappe.get_doc("Stock Return Transfer", row)
			# 	for col in doc.transfer_detail:
			# 		frappe.db.set_value(str(row.child_type),row.child_name,'is_out',0) 
	def on_submit(self):
		for row in self.transfer_details:
			if self.type == "Keluar":
				frappe.db.set_value(str(row.child_type),row.child_name,'is_out',1)
			else:
				frappe.db.set_value(str(row.child_type),row.child_name,'is_out',0)
	def on_cancel(self):
		for row in self.transfer_details:
			if self.type == "Keluar":
				frappe.db.set_value(str(row.child_type),row.child_name,'is_out',0)