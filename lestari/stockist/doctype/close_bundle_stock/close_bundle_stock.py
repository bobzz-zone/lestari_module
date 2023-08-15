# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CloseBundleStock(Document):
    def on_submit(self):
        doc = frappe.new_doc("Update Bundle Stock")
        doc.type = "Deduct Stock"
        doc.bundle = self.bundle
        doc.keterangan = self.keterangan
        for row in self.items:
            if row.rencana_dibawa_kembali == 1:
                baris_baru = {
					"sub_kategori" : row.sub_kategori,
					"kategori" : row.kategori,
					"kadar" : row.kadar,
					"qty_penambahan" : row.qty_penambahan,
					"gold_selling_item" : row.gold_selling_item,
					"item" : row.item
				}
                doc.append("items", baris_baru)
        doc.flags.ignore_permissions = True
        doc.docstatus = 1
        doc.save()
        
    @frappe.whitelist()
    def add_row_action(self):
        baris_baru = {
      				"kadar":self.kadar,
                	"sub_kategori":self.category,
                   	"kategori":frappe.get_doc('Item Group',self.category).parent_item_group,
                    "qty_penambahan":self.bruto,
                    "item":frappe.get_value("Item", {'item_group': self.category,'kadar':self.kadar})
                    }
        self.append("items",baris_baru)
        self.kadar = ""
        self.category = ""
        self.bruto = ""

@frappe.whitelist()
def get_detail_bundle(bundle):
	s_doc = frappe.db.get_list("Kartu Stock Sales", filters={"bundle":bundle})
	detail = []
	for row in s_doc:
		doc = frappe.get_doc("Kartu Stock Sales", row)
		baris_baru = {
			"gold_selling_item" : doc.item,
			"total_dibawa_sales" : doc.qty,
			"sub_kategori" : doc.sub_kategori,
			"kategori" : doc.kategori,
			"kadar" : doc.kadar,
		}
		detail.append(baris_baru)
	return detail