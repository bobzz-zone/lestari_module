# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class SerahTerimaPaymentCash(Document):
	@frappe.whitelist()
	def get_payment(self):
		# payment = frappe.get_list('IDR Payment',filters={'docstatus': 1, 'mode_of_payment':"Cash",'is_done':["<",1], 'sales_bundle':self.bundle}, fields=['parent','parenttype','name','mode_of_payment','amount','is_done'])
		payment = frappe.get_list('Gold Payment',filters={'docstatus': 1,'sales_bundle':self.bundle})
		total_cash = 0
		for row in payment:
			doc = frappe.get_doc("Gold Payment", row)
			for col in doc.idr_payment:
				if col.mode_of_payment == "Cash":
					if col.is_done != 1:
						total_cash += col.amount
						payment_baru = {
							'mode_of_payment': col.mode_of_payment,
							'amount': col.amount,
							'customer': frappe.get_value(col.parenttype, col.parent, 'customer'),
							'deposit_account': frappe.get_doc('Mode of Payment', col.mode_of_payment).accounts[0].default_account,
							'voucher_type':col.parenttype,
							'voucher_no':col.parent,
							'child_table':"IDR Payment",
							'child_id':col.name
						}
						self.append('payment',payment_baru)
						# baris_baru = {
						# 	'amount':col.amount,
						# 	'voucher_type':col.parenttype,
						# 	'voucher_no':col.parent,
						# 	'child_table':"Stock Payment",
						# 	'child_id':col.name
						# }
						# frappe.msgprint(baris_baru)
						# self.append('details',baris_baru)
					self.nilai_cash = total_cash
	def on_submit(self):
		je = frappe.new_doc('Journal Entry')
		je.voucher_type = "Journal Entry"
		for row in self.payment:
			baris_baru = {
				'account' : row.deposit_account,
				'debit_in_account_currency' : row.amount,
			}
			je.append('accounts', baris_baru)
		account_kas = frappe.db.get_single_value('Gold Selling Settings','default_kas_kantor')
		je.append('accounts',{'account':account_kas,"credit_in_account_currency":self.nilai_cash})
		je.posting_date = self.posting_date
		je.bill_no = self.name
		je.bill_date = self.posting_date
		je.flags.ignore_permissions = True
		je.save()
		for col in self.payment:
			frappe.db.set_value("IDR Payment", col.child_id, "is_done", 1)
