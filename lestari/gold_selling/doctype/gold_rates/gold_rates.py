# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now_datetime
from frappe.model.document import Document

class GoldRates(Document):
	pass
@frappe.whitelist(allow_guest=True)
def get_latest_rates(type = "CT"):
	try:
		return frappe.db.sql("select nilai from `tabGold Rates` where date<='{}' and type_emas='{}' order by date desc".format(now_datetime(),type),as_dict=True)[0]
	except:
		return 0
	#return "select nilai from `tabGold Rates` where date<='{}' order by date desc"
