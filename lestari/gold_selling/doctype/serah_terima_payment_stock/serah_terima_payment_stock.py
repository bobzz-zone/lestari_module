# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class SerahTerimaPaymentStock(Document):
	@frappe.whitelist()
	def get_detail(self):
		
		if self.category == "Emas 24":
			depo_list = frappe.get_list('Stock Payment',filters={'docstatus': 1, "rate":['>',100], 'is_done':["<",1]}, fields=['parent','parenttype','name','item','qty','rate','amount','is_done'])
		else:
			depo_list = frappe.get_list('Stock Payment',filters={'docstatus': 1, "rate":['<=',100], 'is_done':["<",1]}, fields=['parent','parenttype','name','item','qty','rate','amount','is_done'])
		for row in depo_list:
			# frappe.msgprint(str(row.voucher_type))
			doc = frappe.get_doc(str(row.parenttype), row.parent).sales_bundle
			if doc and doc == self.sales_bundle:
				# item_baru = {
				# 	'item':row.item,
				# 	'qty':row.qty,
				# }
				# self.append('items',item_baru)
				customer = frappe.db.get_value(row.parenttype,row.parent,'customer')
				subcustomer = frappe.db.get_value(row.parenttype,row.parent,'subcustomer')
				baris_baru = {
					'item':row.item,
					'qty':row.qty,
					'voucher_type':row.parenttype,
					'voucher_no':row.parent,
					'customer': customer,
					'sub_customer': subcustomer,
					'customer_name':frappe.db.get_value("Customer",customer,'customer_name'),
					'customer_group':frappe.db.get_value(row.parenttype,row.parent,'customer_group'),
					'territory':frappe.db.get_value(row.parenttype,row.parent,'territory'),
					'child_table':"Stock Payment",
					'child_id':row.name
				}
				self.append('details',baris_baru)
		# self.flags.ignore_permissions = True
		# self.save()
	def on_submit(self):
		# self.items=[]
		for col in self.details:
			frappe.db.set_value("Stock Payment", col.child_id, "is_done", 1)
		# 	item_baru = {
		# 			'item':col.item,
		# 			'qty':col.qty,
		# 		}
		# 	self.append('items',item_baru)
		ste = frappe.new_doc('Stock Entry')
		ste.stock_entry_type = "Material Transfer"
		for row in self.details:
			baris_baru = {
				's_warehouse' : self.s_warehouse,
				't_warehouse' : self.t_warehouse,
				'item_code' : row.item,
				'qty' : row.qty,
				'allow_zero_valuation_rate' : 1
			}
			ste.append('items', baris_baru)
		ste.flags.ignore_permissions = True
		ste.save()
	def on_cancel(self):
		for col in self.details:
			frappe.db.set_value("Stock Payment", col.child_id, "is_done", 0)
