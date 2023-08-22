# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class SerahTerimaPaymentTransfer(Document):
	@frappe.whitelist()
	def get_payment(self):
		list_bank = frappe.get_list("Mode of Payment", filters={'type': 'Bank', 'enabled': '1'})
		# frappe.msgprint(str(list_bank))
		bank = []
		for row in list_bank:
			bank.append(row.name)
			# frappe.msgprint(str(bank))
		payment = frappe.get_list('IDR Payment',filters={'docstatus': 1, 'mode_of_payment':["in",bank],'is_done':["<",1]}, fields=['parent','parenttype','name','mode_of_payment','amount','is_done'])
		total_cash = 0
		for row in payment:
			# frappe.msgprint(row)
			total_cash += row.amount
			payment_baru = {
				'mode_of_payment': row.mode_of_payment,
				'amount': row.amount,
				'customer': frappe.get_value(row.parenttype, row.parent, 'customer'),
				'deposit_account': frappe.get_doc('Mode of Payment', row.mode_of_payment).accounts[0].default_account,
				'voucher_type':row.parenttype,
				'voucher_no':row.parent,
				'child_table':"IDR Payment",
				'child_id':row.name
			}
			self.append('payment',payment_baru)
			# baris_baru = {
			# 	'amount':row.amount,
			# 	'voucher_type':row.parenttype,
			# 	'voucher_no':row.parent,
			# 	'child_table':"Stock Payment",
			# 	'child_id':row.name
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
