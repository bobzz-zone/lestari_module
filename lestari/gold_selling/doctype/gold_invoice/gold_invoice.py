import frappe
from frappe.utils import now_datetime ,now
from frappe.model.document import Document
from datetime import datetime
from erpnext.accounts.utils import get_account_currency, get_fiscal_years, validate_fiscal_year
from frappe.utils import flt
from frappe.model.naming import getseries
from frappe.model.naming import make_autoname

class GoldInvoice(Document):
	def autoname(self):
		roman_list = ['0','I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII']
		post_date = datetime.strptime(self.posting_date, '%Y-%m-%d')
		year = "{}".format(post_date.year)
		if not self.no_invoice:
			naming_series = self.naming_series
			naming_series = naming_series.replace("#####", getseries(self.naming_series,5)).replace("#M#", roman_list[post_date.month]).replace("#Y#",year)
			# frappe.throw(naming_series)
		else:
			naming_series = "{0}/{1}/{2}".format(self.no_invoice,roman_list[post_date.month],year)
		self.name = naming_series

	def validate(self):
		if(self.no_invoice):
			#self.name = self.no_invoice
			#total items
			total=0
			bruto=0
			for row in self.items:
				total=total+row.amount
				bruto=bruto+row.qty
			self.total=total
			self.total_bruto=bruto
			
			self.grand_total=flt(self.total)
			self.outstanding = self.grand_total
			if self.outstanding<0:
				frappe.throw("Outstanding tidak boleh lebih kecil dari 0")
	@frappe.whitelist(allow_guest=True)
	def add_row_action(self):
		gi = frappe.db.sql("""select name,income_account from `tabGold Selling Item` where kadar="{}" and item_group="{}" """.format(self.kadar,self.category),as_list=1)
		if gi and len(gi)>0:
#			self.append("items",{"category":gi[0][0],"rate":get_gold_rate(gi[0][0],self.customer,self.customer_group)['nilai'],"kadar":self.kadar,"item_group":self.category,"income_account":gi[0][1],"qty":self.add_bruto})
			rate=flt(get_gold_rate(gi[0][0],self.customer,self.customer_group,self.subcustomer)['nilai'])
			print_rate=flt(get_gold_rate(gi[0][0],self.customer,self.customer_group,self.subcustomer)['nilai_print'])
			self.append("items",{"category":gi[0][0],"rate":rate,"kadar":self.kadar,"item_group":self.category,"income_account":gi[0][1],"qty":self.add_bruto,"amount":self.add_bruto*rate/100,"print_rate":print_rate,"print_amount":self.add_bruto*print_rate/100})
		else:
			frappe.msgprint("Product Not Found")
		self.kadar = ""
		self.category = ""
		self.add_bruto = ""
	def before_submit(self):
		if not self.posting_date:
			frappe.throw("Tanggal Invoice belum terisi")
		if self.outstanding<0:
			frappe.throw("Error, Outstanding should not be less than zero")
		if self.outstanding==0:
			self.invoice_status="Paid"
		else:
			self.invoice_status="Unpaid"

	def on_submit(self):
		if self.outstanding <= 0:
			frappe.throw(str(self.outstanding))
		else:
			self.make_gl_entries()

	def on_trash(self):
			frappe.db.sql(
				"delete from `tabGL Entry` where voucher_type=%s and voucher_no=%s", (self.doctype, self.name)
			)
			frappe.db.sql(
				"delete from `tabStock Ledger Entry` where voucher_type=%s and voucher_no=%s",
				(self.doctype, self.name),
			)
			
	def get_gl_entries(self, warehouse_account=None):
		from erpnext.accounts.general_ledger import merge_similar_entries
		#GL  Generate
		#get configurasi
		piutang_gold=self.piutang_gold
		selisih_kurs = frappe.db.get_single_value('Gold Selling Settings', 'selisih_kurs')
		piutang_idr = frappe.db.get_single_value('Gold Selling Settings', 'piutang_idr')
		cost_center = frappe.db.get_single_value('Gold Selling Settings', 'cost_center')
		gl={}
		fiscal_years = get_fiscal_years(self.posting_date, company=self.company)[0][0]
		#add GL untuk pph dan ppn
		ppn_account = frappe.db.get_single_value('Gold Selling Settings', 'ppn_account')
		gl[ppn_account]={
				"posting_date":self.posting_date,
                "account":ppn_account,
                "party_type":"",
                "party":"",
                "cost_center":cost_center,
                "debit":0,
                "credit":self.ppn,
                "account_currency":"IDR",
                "debit_in_account_currency":0,
                "credit_in_account_currency":self.ppn,
                "voucher_type":"Gold Invoice",
                "voucher_no":self.name,
                "is_opening":"No",
                "is_advance":"No",
                "fiscal_year":fiscal_years,
                "company":self.company,
                "is_cancelled":0
		}
		if self.pph >0:
			pph_account = frappe.db.get_single_value('Gold Selling Settings', 'pph_account')
			gl[pph_account]={
				"posting_date":self.posting_date,
                               	"account":pph_account,
                               	"party_type":"",
                               	"party":"",
                               	"cost_center":cost_center,
                               	"debit":0,
                               	"credit":self.pph,
                               	"account_currency":"IDR",
                               	"debit_in_account_currency":0,
                               	"credit_in_account_currency":self.pph,
                               	"voucher_type":"Gold Invoice",
                               	"voucher_no":self.name,
                               	"is_opening":"No",
                               	"is_advance":"No",
                               	"fiscal_year":fiscal_years,
                               	"company":self.company,
                               	"is_cancelled":0
			}
		gl[piutang_idr]={
								"posting_date":self.posting_date,
								"account":piutang_idr,
								"party_type":"Customer",
								"party":self.customer,
								"cost_center":cost_center,
								"debit":self.ppn+self.pph,
								"credit":0,
								"account_currency":"IDR",
								"debit_in_account_currency":self.ppn+self.pph,
								"credit_in_account_currency":0,
								#"against":"4110.000 - Penjualan - L",
								"voucher_type":"Gold Invoice",
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
									"debit":(self.grand_total*self.tutupan),
									"credit":0,
									"account_currency":"GOLD",
									"debit_in_account_currency":self.grand_total,
									"credit_in_account_currency":0,
									#"against":"4110.000 - Penjualan - L",
									"voucher_type":"Gold Invoice",
									"voucher_no":self.name,
									#"remarks":"",
									"is_opening":"No",
									"is_advance":"No",
									"fiscal_year":fiscal_years,
									"company":self.company,
									"is_cancelled":0
									}
		#2 untuk GL untuk penjualan IDR
		for row in self.items:
			if row.income_account in gl:
				gl[row.income_account]['credit']=gl[row.income_account]['credit']+(row.amount*self.tutupan)
				gl[row.income_account]['credit_in_account_currency']=gl[row.income_account]['credit']
			else:
				gl[row.income_account]={
									"posting_date":self.posting_date,
									"account":row.income_account,
									"party_type":"",
									"party":"",
									"cost_center":cost_center,
									"debit":0,
									"credit":row.amount*self.tutupan,
									"account_currency":"IDR",
									"debit_in_account_currency":0,
									"credit_in_account_currency":row.amount*self.tutupan,
									#"against":"4110.000 - Penjualan - L",
									"voucher_type":"Gold Invoice",
									"voucher_no":self.name,
									#"remarks":"",
									"is_opening":"No",
									"is_advance":"No",
									"fiscal_year":fiscal_years,
									"company":self.company,
									"is_cancelled":0
									}
		gl_entries=[]
		
		for row in gl:
			if 'remarks' in gl[row]:
				pass
			else:
				gl[row]['remarks']=""
			gl_entries.append(frappe._dict(gl[row]))
		gl_entries = merge_similar_entries(gl_entries)
		return gl_entries
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
	def on_cancel(self):
		self.flags.ignore_links=True
		
		self.make_gl_entries()
	@frappe.whitelist(allow_guest=True)
	def get_gold_payment(self):
		doc = frappe.new_doc("Gold Payment")
		doc.customer = self.customer
		doc.warehouse = self.warehouse
		doc.posting_date = now()

		doc.total_invoice = self.outstanding
		baris_baru = {
			'gold_invoice':self.name,
			'total':self.outstanding,
			'due_date':self.due_date,
			'total':self.grand_total
		}
		doc.append("invoice_table",baris_baru)
		doc.tutupan = self.tutupan
		doc.flags.ignore_permissions = True
		doc.save()
		return doc

@frappe.whitelist(allow_guest=True)
def get_gold_rate(category,customer,customer_group,customer_print):
	#check if customer has special rates
	cr=0
	pr=0
	customer_rate=frappe.db.sql("""select nilai_tukar from `tabCustomer Rates` where customer="{}" and category="{}" and valid_from<="{}" and type="Selling" and customer_type="Primary" """.format(customer,category,now_datetime()),as_list=1)
	if customer_rate and customer_rate[0]:
		cr=customer_rate[0][0]
	customer_rate_print=frappe.db.sql("""select nilai_tukar from `tabCustomer Rates` where customer="{}" and category="{}" and valid_from<="{}" and type="Selling" and customer_type="Print Out" """.format(customer_print,category,now_datetime()),as_list=1)
	if customer_rate_print and customer_rate_print[0]:
		# return {"nilai_print":customer_rate_print[0][0]}
		pr=customer_rate_print[0][0]
	if cr==0:
		customer_group_rate=frappe.db.sql("""select nilai_tukar from `tabCustomer Group Rates` where customer_group="{}" and category="{}" and valid_from<="{}"  and type="Selling" """.format(customer_group,category,now_datetime()),as_list=1)
		if customer_group_rate and customer_group_rate[0]:
			# return {"nilai":customer_group_rate[0][0]}
			cr=customer_group_rate[0][0]
	return {"nilai":cr,"nilai_print":pr}

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
