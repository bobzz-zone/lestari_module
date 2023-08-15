# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class TransferStockist(Document):
	def validate(self):
		self.status = 'Draft'
	def on_submit(self):
		self.status = frappe.db.sql("""UPDATE `tabTransfer Stockist` SET status = "{0}" where name = "{0}" """.format(self.name))
	def on_cancel(self):
		self.status = 'Cancelled'
