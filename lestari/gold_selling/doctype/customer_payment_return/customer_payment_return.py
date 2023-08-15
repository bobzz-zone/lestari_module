# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
import erpnext
from frappe.model.document import Document
from erpnext.stock import get_warehouse_account_map
from erpnext.accounts.utils import get_account_currency, get_fiscal_years, validate_fiscal_year
from erpnext.controllers.stock_controller import StockController
from erpnext.stock.stock_ledger import NegativeStockError, get_previous_sle, get_valuation_rate
from frappe.utils import flt
from frappe.utils import now_datetime ,now
class CustomerPaymentReturn(StockController):
	def validate(self):
		# if self.saldo_awal == 0:
		# 	payment_detail = 0
		# 	payment_map={}
		# 	if self.name:
		# 		for row in self.items:
		# 			# gp_used=frappe.db.sql("""select name from `tabCustomer Payment Return` where gold_payment="{}" and name !="{}" and docstatus!=2""".format(self.gold_payment,self.name),as_list=1)
		# 			gp_used=frappe.db.sql("""
		# 						SELECT parent.name
		# 						FROM `tabCustomer Payment Return` parent 
		# 						JOIN `tabStock Payment Return Item` items ON items.parent = parent.name
		# 						WHERE items.voucher_no = "{}"
		# 						AND parent.docstatus = 1
		# 						AND items.voucher_type = "Gold Payment"
		# 						""".format(row.voucher_no,self.name),as_list=1)
		# 			if len(gp_used)>0:
		# 				frappe.throw("""Gold Payment telah di return pada Transaksi no {} """.format(gp_used[0][0]))
		# 			#validate payment return
		# 			payment_detail=frappe.db.sql("""select item,qty from `tabStock Payment` where parent="{}" """.format(row.voucher_no),as_list=1)
		# 			for col in payment_detail:
		# 				payment_map[col[0]]=col[1]
		# 			#validate returned stock
		# 			# for row in self.items:
		# 			# frappe.msgprint(str(payment_map))
		# 			if row.item not in payment_map:
		# 				frappe.throw("""{} Tidak ada pada Record Payment {}""".format(row.item,row.voucher_no))
		# 			if payment_map[row.item]<row.qty:
		# 				frappe.throw("""Jumlah {} Tidak boleh melebihi nilai pada Record Payment {} yaitu {}""".format(row.item,row.voucher_no,payment_map[row.item]))
		# 			#seharusnya validasi agaryang belum due, di pastikan tutupan sama..atau hanya 1 invoice agar di gold payment tutupan di samakan
		# 	#check unallocated harus 0
		# 	if not self.warehouse:
		# 		self.warehouse = frappe.db.get_single_value('Gold Selling Settings', 'default_warehouse')
		# 	if self.total<=1:
		# 		frappe.throw("Error Tidak ada nilai yang dikembalikan")
		# else:
			pass
	def on_submit(self):
		for row in self.items:
			frappe.db.sql(
				"""
				UPDATE `tabStock Return Transfer Details` 
				SET is_out = 1
				WHERE name = "{}"
				""".format(row.child_no))
			row.valuation_rate = get_valuation_rate(
					row.item,
					self.warehouse,
					self.doctype,
					self.name,
					0,
					currency=erpnext.get_company_currency(self.company),
					company=self.company,
					raise_error_if_no_rate=True
				)
			if not row.valuation_rate or row.valuation_rate==0:
				row.valuation_rate = get_valuation_rate(
					row.item,
					self.warehouse,
					self.doctype,
					self.name,
					1,
					currency=erpnext.get_company_currency(self.company),
					company=self.company,
					raise_error_if_no_rate=False
				)
			row.total_amount=row.qty*row.valuation_rate
		self.make_gl_entries()
		#posting Stock Ledger Post
		self.update_stock_ledger()
		self.repost_future_sle_and_gle()
		
	def on_cancel(self):
		for row in self.items:
			frappe.db.sql(
				"""
				UPDATE `tabStock Return Transfer Details` 
				SET is_out = 0
				WHERE name = "{}"
				""".format(row.child_no))
		self.flags.ignore_links=True
		self.make_gl_entries_on_cancel()
		self.update_stock_ledger()
		self.repost_future_sle_and_gle()
	@frappe.whitelist()
	def get_stock_return(self):
		stock_return = frappe.get_list("Stock Return Transfer", filters={
			'type': 'Keluar',
			'docstatus':1
		})
		total = 0
		outstanding = 0
		for row in stock_return:
			doc = frappe.get_doc('Stock Return Transfer',row.name)
			for col in doc.transfer_details:
				if col.customer == self.customer and col.is_out == 0:
					rate = get_gold_purchase_rate(col.item,self.customer,self.customer_group)
					total += col.berat
					amount = col.berat * flt(rate['nilai']) / 100
					frappe.msgprint(total)
					baris_baru = {
						'item': col.item,
						'qty':col.berat,
						'rate':flt(rate['nilai']),
						'amount':amount,
						'no_document':row.name,
						'child_no':col.name,
						'voucher_type':col.voucher_type,
						'voucher_no':col.voucher_no
					}
					outstanding += amount
					self.append('items',baris_baru)
		self.total = total
		self.outstanding = outstanding

	@frappe.whitelist()
	def get_sales_bundle(self):
		from lestari.gold_selling.doctype.gold_invoice.gold_invoice import get_gold_purchase_rate
		sales_partner = frappe.db.get_list("Stock Return Transfer", filters={
			'sales_partner': self.sales_partner,
			# 'customer': self.customer,
        	# 'status_pengembalian': 'Belum Diambil',
			'docstatus':1
    	})
		for row in sales_partner:
			# frappe.msgprint(str(row.name))
			items = frappe.get_doc("Stock Return Transfer", row.name)
			total = 0
			for col in items.transfer_details:
				customer = frappe.db.get_value(str(col.voucher_type),col.voucher_no,"customer")
				if self.customer and self.customer == customer:
					purchase_rate = get_gold_purchase_rate(col.item,self.customer,self.customer_group)
					if col.type == "Keluar":
						frappe.msgprint(str(frappe.db.get_value(str(col.voucher_type), col.voucher_no, ['tutupan'])))
						total = total + col.berat
						# total = total + (col.berat*purchase_rate['nilai']/100)
						baris_baru = {
							'item': col.item,
							'qty': col.berat,
							'rate': purchase_rate['nilai'],
							'amount': col.berat*purchase_rate['nilai']/100,
							'tutupan': frappe.db.get_value(str(col.voucher_type), col.voucher_no, ['tutupan']),
							'no_document': row.name,
							'child_no':col.name,
							'voucher_type': col.voucher_type,
							'voucher_no': col.voucher_no,
						}
						self.append('items',baris_baru)
			self.total = total
	def update_stock_ledger(self):
		sl_entries = []
		sl=[]
		#perlu check hpp outnya
		fiscal_years = get_fiscal_years(self.posting_date, company=self.company)[0][0]

		for row in self.items:
			sl.append({
				"item_code":row.item,
				"actual_qty":row.qty*-1,
				"fiscal_year":fiscal_years,
				"voucher_type": self.doctype,
				"voucher_no": self.name,
				"company": self.company,
				"posting_date": self.posting_date,
				"posting_time": self.posting_time,
				"is_cancelled": 0,
				"stock_uom":frappe.db.get_value("Item", row.item, "stock_uom"),
				"warehouse":self.warehouse,
				"valuation_rate":row.valuation_rate,
				"recalculate_rate": 1,
				"dependant_sle_voucher_detail_no": row.name,
				"is_cancelled":1 if self.docstatus == 2 else 0
				})
		for row in sl:
			sl_entries.append(frappe._dict(row))

		# reverse sl entries if cancel
		# if self.docstatus == 2:
		# 	sl_entries.reverse()

		self.make_sl_entries(sl_entries)
	def make_gl_entries(self, gl_entries=None, from_repost=False):
		from erpnext.accounts.general_ledger import make_gl_entries, make_reverse_gl_entries
		if not gl_entries:
			gl_entries = self.get_gl_entries()
		if gl_entries:
			update_outstanding = "Yes"

			if self.docstatus == 1:
				make_gl_entries(
					gl_entries,
					update_outstanding=update_outstanding,
					merge_entries=False,
					from_repost=from_repost,
				)
			elif self.docstatus == 2:
				make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)

			if update_outstanding == "No":
				from erpnext.accounts.doctype.gl_entry.gl_entry import update_outstanding_amt
				piutang_gold = frappe.db.get_single_value('Gold Selling Settings', 'piutang_gold')
				update_outstanding_amt(
					piutang_gold,
					"Customer",
					self.customer,
					self.doctype,
					self.name,
				)

		elif self.docstatus == 2 :
			make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)
	def get_gl_entries(self, warehouse_account=None):
		from erpnext.accounts.general_ledger import merge_similar_entries
		#GL  Generate
		#get configurasi
		cost_center = frappe.db.get_single_value('Gold Selling Settings', 'cost_center')
		gl_entries=[]
		gl={}
		gl_piutang=[]
		fiscal_years = get_fiscal_years(self.posting_date, company=self.company)[0][0]
		#1 untuk GL untuk piutang Gold
		piutang_gold = frappe.db.get_single_value('Gold Selling Settings', 'piutang_gold')

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
		if self.total>0:
			#hpp perlu di update dulu
			if not self.warehouse and self.saldo_awal == 1:
				self.warehouse = "Stockist - LMS"
			warehouse_account = get_warehouse_account_map(self.company)[self.warehouse].account
			total_value=0
			for row in self.items:
				total_value=total_value+row.total_amount
			self.tutupan=total_value/self.total
			gl[warehouse_account]={
									"posting_date":self.posting_date,
									"account":warehouse_account,
									"party_type":"",
									"party":"",
									"cost_center":cost_center,
									"credit":total_value,
									"debit":0,
									"account_currency":"IDR",
									"credit_in_account_currency":total_value,
									"debit_in_account_currency":0,
									#"against":"4110.000 - Penjualan - L",
									"voucher_type":"Customer Payment Return",
									"voucher_no":self.name,
									#"remarks":"",
									"is_opening":"No",
									"is_advance":"No",
									"fiscal_year":fiscal_years,
									"company":self.company,
									"is_cancelled":0
									}
			gl[piutang_gold]={
									"posting_date":self.posting_date,
									"account":piutang_gold,
									"party_type":"Customer",
									"party":self.customer,
									"cost_center":cost_center,
									"debit":total_value,
									"credit":0,
									"account_currency":"GOLD",
									"debit_in_account_currency":self.total,
									"credit_in_account_currency":0,
									#"against":"4110.000 - Penjualan - L",
									"voucher_type":"Customer Payment Return",
									"voucher_no":self.name,
									#"remarks":"",
									"is_opening":"No",
									"is_advance":"No",
									"fiscal_year":fiscal_years,
									"company":self.company,
									"is_cancelled":0
									}
		
			for row in gl:
				gl_entries.append(frappe._dict(gl[row]))
			gl_entries = merge_similar_entries(gl_entries)
			return gl_entries

@frappe.whitelist(allow_guest=True)
def get_gold_purchase_rate(item,customer,customer_group):
	#check if customer has special rates
	customer_rate=frappe.db.sql("""select nilai_tukar from `tabCustomer Rates` where customer="{}" and item="{}" and valid_from<="{}"  and type="Buying" order by valid_from desc """.format(customer,item,now_datetime()),as_list=1)
	if customer_rate and customer_rate[0]:
		return {"nilai":customer_rate[0][0]}
	customer_group_rate=frappe.db.sql("""select nilai_tukar from `tabCustomer Group Rates` where customer_group="{}" and item="{}" and valid_from<="{}" and type="Buying"  order by valid_from desc """.format(customer_group,item,now_datetime()),as_list=1)
	if customer_group_rate and customer_group_rate[0]:
		return {"nilai":customer_group_rate[0][0]}
	return {"nilai":0}