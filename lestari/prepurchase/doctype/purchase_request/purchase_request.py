# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PurchaseRequest(Document):
	pass
@frappe.whitelist()
def get_template(template):
	if not template:
		return

	reqpur_doc = frappe.get_doc("Purchase Request Template", template)

	req_template = []
	for d in reqpur_doc.get("items"):
		req_details = {
			'item' : d.item, 
			'item_name' : d.item_name, 
			'description' : d.description, 
			'qty' : d.qty, 
			'uom' : d.uom
		}
		req_template.append(req_details)

	return req_template
