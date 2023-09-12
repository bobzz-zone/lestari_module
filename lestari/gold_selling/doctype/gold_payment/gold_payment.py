# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import (
	add_days,
	add_months,
	cint,
	flt,
	fmt_money,
	formatdate,
	get_last_day,
	get_link_to_form,
	getdate,
	nowdate,
	today,
)
from erpnext.stock import get_warehouse_account_map
from erpnext.accounts.utils import get_account_currency, get_fiscal_years, validate_fiscal_year
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account
from erpnext.controllers.stock_controller import StockController

form_grid_templates = {"invoice_table": "templates/item_grid.html"}
#need to check GL
#need check write off dan deposit
class GoldPayment(StockController):
	def validate(self):
		total = self.total_idr_payment
		if not self.warehouse:
			self.warehouse = frappe.db.get_single_value('Gold Selling Settings', 'default_warehouse')

	def on_submit(self):
		if self.unallocated_payment>0.001:
			# frappe.msgprint(self.total_invoice)
			frappe.throw("Error,unallocated Payment Masih ada {}".format(self.unallocated_payment))
		else:
			##			for cek in self.idr_payment:
				# if cek.mode_of_payment != "Cash":
					# frappe.throw("Silahkan Cek Transfer Bank Terlebih Dahulu")
				# else:
			self.make_gl_entries()
				#posting Stock Ledger Post
			self.update_stock_ledger()
			self.repost_future_sle_and_gle()
				#stock return transfer
			total_cpr24k = 0
			
			for row in self.invoice_table:
				if row.allocated==row.outstanding and row.tax_allocated==row.outstanding_tax:
					frappe.db.sql("""update `tabGold Invoice` set sisa_pajak=sisa_pajak - {} ,outstanding=outstanding-{} , invoice_status="Paid", gold_payment="{}" where name = "{}" """.format(row.tax_allocated,row.allocated,self.name,row.gold_invoice))
				else:
					frappe.db.sql("""update `tabGold Invoice` set sisa_pajak=sisa_pajak - {} , outstanding=outstanding-{} , gold_payment="{}" where name = "{}" """.format(row.tax_allocated,row.allocated,self.name,row.gold_invoice))
			
	def on_cancel(self):
		self.flags.ignore_links=True
		piutang_gold = self.piutang_gold
		self.make_gl_entries_on_cancel()
		self.update_stock_ledger()
		self.repost_future_sle_and_gle()
		
		#update invoice
		for row in self.invoice_table:
			frappe.db.sql("""update `tabGold Invoice` set sisa_pajak=sisa_pajak+{} ,outstanding=outstanding+{} , invoice_status="Unpaid" where name = "{}" """.format(row.tax_allocated,row.allocated,row.gold_invoice))
		
	@frappe.whitelist()
	def get_gold_invoice(self):
		#reset before add
		self.invoice_table=[]
		self.total_gold = 0
		# doc = frappe.db.get_list("Gold Invoice", filters={"customer": self.customer, "invoice_status":"Unpaid", 'docstatus':1}, fields=['name','posting_date','customer','subcustomer','enduser','outstanding','due_date','tutupan','total_bruto','grand_total'])
		doc = frappe.db.sql("""
                      SELECT
                      name,
                      posting_date,
                      customer,
                      outstanding,
                      due_date,
                      tutupan,
                      total_bruto,
                      grand_total,
                      sisa_pajak
                      FROM `tabGold Invoice`
                      WHERE invoice_status = "Unpaid"
                      and docstatus = 1
                      and 
                      customer = "{0}" 
                      """.format(self.customer),as_dict=1)
		# frappe.msgprint(str(doc))
		if self.tutupan > 0:
			tutupan = self.tutupan
		else:
			tutupan = frappe.db.sql("""
                        SELECT nilai
						FROM `tabGold Rates`
						WHERE nilai > 0
						AND DATE <= CURDATE() 
						ORDER BY DATE DESC
						LIMIT 1
                           """, as_dict=1)
			# frappe.msgprint(str())
			tutupan = tutupan[0].nilai
			self.tutupan = flt(tutupan)
		for row in doc:
			# frappe.msgprint(str(row))
			if row.outstanding and flt(row.outstanding)>0:
				if not self.total_invoice:
					self.total_invoice=0
				self.total_invoice = self.total_invoice + row.outstanding
				baris_baru = {
					'gold_invoice':row.name,
					'tanggal':row.posting_date,
					'customer':row.customer,
					'outstanding':row.outstanding,
					'total':row.grand_total,
					'due_date':row.due_date,
					'total_bruto':row.total_bruto,
					'tutupan':row.tutupan,
					'outstanding_tax':row.sisa_pajak
				}
				self.append("invoice_table",baris_baru)
		
	def update_stock_ledger(self):
		sl_entries = []
		sl=[]
		fiscal_years = get_fiscal_years(self.posting_date, company=self.company)[0][0]
		for row in self.stock_payment:
			sl.append({
					"item_code":row.item,
					"actual_qty":row.qty,
					"fiscal_year":fiscal_years,
					"voucher_type": self.doctype,
					"voucher_no": self.name,
					"company": self.company,
					"posting_date": self.posting_date,
					"posting_time": self.posting_time,
					"is_cancelled": 0,
					"stock_uom":frappe.db.get_value("Item", row.item, "stock_uom"),
					"warehouse":self.warehouse,
					"incoming_rate":row.rate*self.tutupan/100,
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

		#frappe.msgprint(gl_entries)
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
				piutang_gold = self.piutang_gold
				update_outstanding_amt(
					piutang_gold,
					"Customer",
					self.customer,
					self.doctype,
					self.name,
				)

		elif self.docstatus == 2 :
			make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)
   
	@frappe.whitelist()
	def gl_dict(self,cost_center,account,debit,credit,fiscal_years):
		return {
										"posting_date":self.posting_date,
										"account":account,
										"party_type":"",
										"party":"",
										"cost_center":cost_center,
										"debit":debit,
										"credit":credit,
										"account_currency":"IDR",
										"debit_in_account_currency":debit,
										"credit_in_account_currency":credit,
										#"against":"4110.000 - Penjualan - L",
										"voucher_type":"Gold Payment",
										"voucher_no":self.name,
										#"remarks":"",
										"is_opening":"No",
										"is_advance":"No",
										"fiscal_year":fiscal_years,
										"company":self.company,
										"is_cancelled":0
										}
	def update_against(self):
		if self.total_idr_payment>0:
			#journal IDR nya aja
			account_list_idr=""
			for row in self.idr_payment:
				account=get_bank_cash_account(row.mode_of_payment,self.company)["account"]
				if account not in account_list_idr:
					if account_list_idr=="":
						account_list_idr=account
					else:
						account_list_idr="{},{}".format(account_list_idr,account)
			frappe.db.sql("""update `tabGL Entry` set against="{}" where voucher_no="{}" and account = "110.401.000 - Piutang Dagang - LMS" """.format(account_list_idr,self.name))
	def get_gl_entries(self, warehouse_account=None):
		from erpnext.accounts.general_ledger import merge_similar_entries
		#GL  Generate
		#get configurasi

		gl_entries = []
		gl = {}
		
		gl_piutang = []
		gl_piutang_idr = []
		fiscal_years = get_fiscal_years(self.posting_date, company=self.company)[0][0]
		#1 untuk GL untuk piutang Gold
		piutang_gold = self.piutang_gold
		selisih_kurs = frappe.db.get_single_value('Gold Selling Settings', 'selisih_kurs')
		piutang_idr = frappe.db.get_single_value('Gold Selling Settings', 'piutang_idr')
		cost_center = frappe.db.get_single_value('Gold Selling Settings', 'cost_center')
		

		nilai_selisih_kurs = 0
		# distribute total gold perlu bagi per invoice
		#sisa= self.allocated_payment
		credit=0
		debit=0
		#untuk payment IDR
		account_list_idr=""
		if self.total_idr_payment>0:
			#journal IDR nya aja
			for row in self.idr_payment:
				account=get_bank_cash_account(row.mode_of_payment,self.company)["account"]
				if account in gl:
					if  row.amount >0:
						gl[account]['debit']=gl[account]['debit']+row.amount
						gl[account]['debit_in_account_currency']=gl[account]['debit']
					else:
						gl[account]['credit']=gl[account]['credit']-row.amount
						gl[account]['credit_in_account_currency']=gl[account]['credit']
				else:
					if row.amount >0:
						gl[account]=self.gl_dict(cost_center,account,row.amount,0,fiscal_years)
					else:
						gl[account]=self.gl_dict(cost_center,account,0,-1*row.amount,fiscal_years)
					if account_list_idr=="":
						account_list_idr=account
					else:
						account_list_idr="{},{}".format(account_list_idr,account)
		for row in self.invoice_table:
			if row.tax_allocated>0:
				gl_piutang_idr.append({
					"posting_date":self.posting_date,
					"account":piutang_idr,
					"party_type":"Customer",
					"party":self.customer,
					"cost_center":cost_center,
					"debit":0,
					"credit":row.tax_allocated,
					"account_currency":"IDR",
					"debit_in_account_currency":0,
					"credit_in_account_currency":row.tax_allocated,
					#"against":"4110.000 - Penjualan - L",
					"against":account_list_idr,
					"voucher_type":"Gold Payment",
					"against_voucher_type":"Gold Invoice",
					"against_voucher":row.gold_invoice,
					"voucher_no":self.name,
					#"remarks":"",
					"is_opening":"No",
					"is_advance":"No",
					"fiscal_year":fiscal_years,
					"company":self.company,
					"is_cancelled":0
				})
			# if sisa>0 and row.allocated>0:
			if row.allocated>0:
				# payment=row.allocated
				# if sisa < row.allocated:
				# 	payment=sisa

				# inv_payment_map[row.gold_invoice]=inv_payment_map[row.gold_invoice]-payment
				gl_piutang.append({
					"posting_date":self.posting_date,
					"account":piutang_gold,
					"party_type":"Customer",
					"party":self.customer,
					"cost_center":cost_center,
					"debit":0,
					"credit":row.allocated*row.tutupan,
					"account_currency":"GOLD",
					"debit_in_account_currency":0,
					"credit_in_account_currency":row.allocated,
					"against":account_list_idr,
					#"against":"4110.000 - Penjualan - L",
					"voucher_type":"Gold Payment",
					"against_voucher_type":"Gold Invoice",
					"against_voucher":row.gold_invoice,
					"voucher_no":self.name,
					#"remarks":"",
					"is_opening":"No",
					"is_advance":"No",
					"fiscal_year":fiscal_years,
					"company":self.company,
					"is_cancelled":0
				})
		#		credit=credit+(payment*row.tutupan)
				if row.tutupan!=self.tutupan:
					nilai_selisih_kurs=nilai_selisih_kurs+((self.tutupan-row.tutupan)*row.allocated)
		#frappe.msgprint("Invoice Payment credit = {} , debit = {}".format(credit,debit))
		
		roundoff=0
#		frappe.msgprint("Customer Return credit = {} , debit = {}".format(credit,debit))
		for row in gl_piutang:
			roundoff=roundoff+row['debit']-row['credit']
			gl_entries.append(frappe._dict(row))
		for row in gl_piutang_idr:
			roundoff=roundoff+row['debit']-row['credit']
			gl_entries.append(frappe._dict(row))
		#perlu check selisih kurs dari tutupan
		#lebih dr 0 itu debit
		dsk=0
		csk=0
		if nilai_selisih_kurs!=0:
			if nilai_selisih_kurs<0:
				dsk=nilai_selisih_kurs*-1
			else:
				csk=nilai_selisih_kurs
			print("{} = {} || {}".format(selisih_kurs,dsk,csk))
			gl[selisih_kurs]=self.gl_dict(cost_center,selisih_kurs,dsk,csk,fiscal_years)
		
		#BONUS,DISCOUNT,WRITEOFF
		if self.bonus>0:
			bonus_payment = frappe.db.get_single_value('Gold Selling Settings', 'bonus_payment')
			gl[bonus_payment]=self.gl_dict(cost_center,bonus_payment,self.bonus*self.tutupan,0,fiscal_years)
			
		#	debit=debit+(self.bonus*self.tutupan)
		#	frappe.msgprint("Bonus credit = {} , debit = {}".format(credit,debit))
		if self.discount_amount>0:
			discount_payment = frappe.db.get_single_value('Gold Selling Settings', 'discount_payment')
			gl[discount_payment]= self.gl_dict(cost_center,discount_payment,self.discount_amount*self.tutupan,0,fiscal_years)
		
		#	debit=debit+(self.discount_amount*self.tutupan)
		#	frappe.msgprint("Discount credit = {} , debit = {}".format(credit,debit))
		if self.write_off!=0:
			if self.write_off>0:
				gl[self.write_off_account]=self.gl_dict(cost_center,self.write_off_account,self.write_off_total,0,fiscal_years)
			else:
				gl[self.write_off_account]=self.gl_dict(cost_center,self.write_off_account,0,self.write_off_total*-1,fiscal_years)
		if self.total_gold_payment>0:
			warehouse_value=0
			titip={}
			for row in self.stock_payment:
				warehouse_value=warehouse_value+row.amount
			if warehouse_value>0:
				warehouse_account = get_warehouse_account_map(self.company)[self.warehouse].account
				gl[warehouse_account]=self.gl_dict(cost_center,warehouse_account,warehouse_value*self.tutupan,0,fiscal_years)
			
		# #untuk payment IDR
		# if self.total_idr_payment>0:
		# 	#journal IDR nya aja
		# 	for row in self.idr_payment:
		# 		account=get_bank_cash_account(row.mode_of_payment,self.company)["account"]
		# 		if account in gl:
		# 			if  row.amount >0:
		# 				gl[account]['debit']=gl[account]['debit']+row.amount
		# 				gl[account]['debit_in_account_currency']=gl[account]['debit']
		# 			else:
		# 				gl[account]['credit']=gl[account]['credit']-row.amount
		# 				gl[account]['credit_in_account_currency']=gl[account]['credit']
		# 		else:
		# 			if row.amount >0:
		# 				gl[account]=self.gl_dict(cost_center,account,row.amount,0,fiscal_years)
		# 			else:
		# 				gl[account]=self.gl_dict(cost_center,account,0,-1*row.amount,fiscal_years)
		roundoff=0
		against_debit=""
		against_credit=""
		for row in gl:
			roundoff=roundoff+gl[row]['debit']-gl[row]['credit']
			if gl[row]["debit"]>0:
				if gl[row]["account"] not in against_credit:
					against_credit="{} ,{}".format(against_credit,gl[row]["account"])
			else:
				if gl[row]["account"] not in against_debit:
					against_debit="{} ,{}".format(against_debit,gl[row]["account"])
		#add roundoff
		if roundoff!=0:
			roundoff_coa=frappe.db.get_value('Company', self.company, 'round_off_account')
			if roundoff>0:
				gl[roundoff_coa]=self.gl_dict(cost_center,roundoff_coa,0,roundoff,fiscal_years)
				against_debit="{} ,{}".format(against_debit,gl[row]["account"])
			else:
				gl[roundoff_coa]=gl[roundoff_coa]=self.gl_dict(cost_center,roundoff_coa,roundoff*-1,0,fiscal_years)
				against_credit="{} ,{}".format(against_credit,gl[row]["account"])
#			gl_entries.append(frappe._dict(gl[roundoff_coa]))
		for row in gl:
			if gl[row]["debit"]>0:
				gl[row]["against"]=against_debit
			else:
				gl[row]["against"]=against_credit
			gl_entries.append(frappe._dict(gl[row]))
		gl_entries = merge_similar_entries(gl_entries)
		return gl_entries
