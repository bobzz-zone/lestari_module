# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now_datetime ,now
from frappe.model.document import Document
from erpnext.accounts.utils import get_account_currency, get_fiscal_years, validate_fiscal_year
from datetime import datetime # from python std library
from frappe.utils import flt

class UpdateBundleStock(Document):
    @frappe.whitelist()
    def calculate(self):
        from lestari.randomize import randomizer

        self.per_sub_category = []
        for row in self.items:
            input_warehouse = self.s_warehouse
            input_kadar = row.kadar
            kebutuhan = row.qty_penambahan

            result = randomizer(input_warehouse, input_kadar, kebutuhan)

            for baris_result in result:
                self.append("per_sub_category",{
                    "item": baris_result[0] ,
                    "item_name": frappe.get_doc("Item",baris_result[0]).item_name,
                    "bruto": frappe.utils.flt(baris_result[1]),
                    "kadar": row.kadar
                })


    def validate(self):
        self.status = 'Draft'
    def on_cancel(self):
        self.status = 'Cancelled'       
    def on_submit(self):
        ste = frappe.new_doc("Stock Entry")
        ste.stock_entry_type = "Material Transfer"
        ste.employee_id = self.pic
        ste.remarks = self.keterangan
        ste.update_bundle_stock_no = self.name
        for row in self.per_sub_category:
            baris_baru = {
				'item_code' : row.item,
				's_warehouse' : self.s_warehouse,
				't_warehouse' : self.warehouse,
				'qty' : row.bruto,
				'allow_zero_valuation_rate' : 1
			}
            ste.append("items",baris_baru)
        ste.flags.ignore_permissions = True
        ste.save()
        frappe.db.sql("""UPDATE `tabUpdate Bundle Stock` SET status = "Submitted" where name = "{0}" """.format(self.name))
        frappe.msgprint(str(frappe.get_last_doc("Stock Entry")))
        for row in self.items:
            gdle = frappe.new_doc("Gold Ledger Entry")
            gdle.item = row.gold_selling_item
            gdle.bundle = self.bundle
            gdle.kategori = row.kategori
            gdle.sub_kategori = row.sub_kategori
            gdle.kadar = row.kadar
            gdle.warehouse = self.warehouse
            gdle.posting_date = self.date
            gdle.posting_time = datetime.now().strftime('%H:%M:%S')
            gdle.voucher_type = self.doctype
            gdle.voucher_no = self.name
            gdle.voucher_detail_no = row.name
            if self.type == "New Stock":
                gdle.proses = 'Penyerahan'
                gdle.qty_in = row.qty_penambahan
                gdle.qty_out = 0
                gdle.qty_balance = 0
            if self.type == "Add Stock":
                gdle.proses = 'Penambahan'
                doc = frappe.db.get_list(doctype = "Kartu Stock Sales", filters={"bundle" : self.bundle, "item":row.gold_selling_item, "kategori": row.sub_kategori}, fields=['item','bundle','kategori','kadar','qty'])
                for col in doc:
                    gdle.qty_in = row.qty_penambahan
                    gdle.qty_out = 0
                    gdle.qty_balance = col.qty
            if self.type == "Deduct Stock":
                gdle.proses = 'Penyetoran'
                doc = frappe.db.get_list(doctype = "Kartu Stock Sales", filters={"bundle" : self.bundle, "item":row.gold_selling_item, "kategori": row.sub_kategori}, fields=['item','bundle','kategori','kadar','qty'])
                for col in doc:
                    gdle.qty_in = 0
                    gdle.qty_out = row.qty_penambahan
                    gdle.qty_balance = col.qty
            gdle.flags.ignore_permissions = True
            frappe.msgprint(gdle.proses)
            gdle.save()
    
    @frappe.whitelist()
    def add_row_action(self):
        baris_baru = {
      				"kadar":self.kadar,
                	"sub_kategori":self.category,
                   	"kategori":frappe.get_doc('Item Group',self.category).parent_item_group,
                    "qty_penambahan":self.bruto
                    }
        self.append("items",baris_baru)
        self.kadar = ""
        self.category = ""
        self.bruto = ""
    # @frappe.whitelist()
    # def cek_new(self):
    #     cek = frappe.db.sql_list("""
    #             SELECT * FROM `tabUpdate Bundle Stock 
    #             WHERE bundle = '{}' and docstatus != 2
    #         """.format(self.bundle))
    #     frappe.msgprint(str(cek))
    #     return cek
    @frappe.whitelist()
    def get_bundle_sales(self):
        bundle = frappe.db.get_list("Close Bundle Stock")
        for row in bundle:
            frappe.msgprint(row)
	
@frappe.whitelist()
def get_sub_item(kadar, sub_kategori):
    item_code = frappe.db.sql("""
                              SELECT item_code, gold_selling_item FROM `tabItem` WHERE kadar = "{}" and item_code LIKE "{}%" LIMIT 1
                              """.format(kadar,sub_kategori))
    # frappe.msgprint(item_code)
    return item_code

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_sub_kategori(doctype, txt, searchfield, start, page_len, filters):
    return frappe.db.sql("""
        SELECT name
        FROM `tabItem Group`
        WHERE parent_item_group 
        IN (SELECT NAME 
        FROM `tabItem Group` 
        WHERE parent_item_group = "{}")
    """.format({
            filters.get('parent')
        }), {
        # 'txt': "%{}%".format(txt),
        # '_txt': txt.replace("%", ""),
        # 'start': start,
        # 'page_len': page_len
    })