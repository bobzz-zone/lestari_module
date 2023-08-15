# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PencatatanPengembalianEmas(Document):
	pass

@frappe.whitelist()
def get_serah_terima_stock(customer,sales_bundle):
	doc = frappe.get_list("Serah Terima Payment Stock", filters={"docstatus":["=","1"],"sales_bundle":sales_bundle})
	baris_baru = []
	for row in doc:
		frappe.msgprint(str(row))
		penerimaan = frappe.get_doc('Serah Terima Payment Stock', row.name)
		for col in penerimaan.details:
			if col.customer == customer and col.rencana_pengembalian_kembali == 0 and col.sudah_cek == 0:
				baris_baru.append({
					'item': col.item,
					'category': frappe.db.get_value('Item', col.item, "gold_selling_item"),
					'item_group': frappe.db.get_value('Item', col.item, "item_group"),
					'qty': col.qty,
					'gold_payment_no': col.voucher_no
				})
	return baris_baru

  
	