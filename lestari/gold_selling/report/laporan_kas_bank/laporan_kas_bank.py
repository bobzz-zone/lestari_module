# Copyright (c) 2013, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
from collections import OrderedDict

import frappe
from frappe import _, _dict
from frappe.utils import getdate,flt

from erpnext import get_company_currency, get_default_company

# to cache translations
TRANSLATIONS = frappe._dict()

def execute(filters=None):
	if not filters:
		return [], []
		
	validate_filters(filters)

	columns = get_column()
	
	update_translations()

	data = get_result(filters)

	return columns, data

def update_translations():
	TRANSLATIONS.update(
		dict(OPENING=_("Opening"), TOTAL=_("Total"), CLOSING_TOTAL=_("Closing (Opening + Total)"))
	)

def validate_filters(filters):
	if not filters.get("account"):
		frappe.throw(
			_("{0} are mandatory").format(frappe.bold(_("Account")))
		)

	if not filters.get("from_date") and not filters.get("to_date"):
		frappe.throw(
			_("{0} and {1} are mandatory").format(frappe.bold(_("From Date")), frappe.bold(_("To Date")))
		)

	if filters.from_date > filters.to_date:
		frappe.throw(_("From Date must be before To Date"))

def get_result(filters):
	gl_entries = get_gl_entries(filters)
#	gl_opening = get_gl_opening(filters)
	data = get_data_with_opening_closing(filters, gl_entries)

	result = get_result_as_list(data, filters)

	return result

#def get_gl_opening(filters):
#	gl_entries = frappe.db.sql(
#		"""
#		SELECT 
#			gl.name as gl_entry,
#			gl.posting_date,
#			acc.account_name as buku,
#			gl.cost_center,
#			gl.remarks as keterangan,
#			gl.account,
#			gl.against,
#			gl.debit,
#			gl.credit,
#			gl.voucher_type,
#			gl.voucher_no
#			FROM `tabGL Entry` gl
#			JOIN `tabAccount` acc ON acc.name = gl.account
#			JOIN `tabCurrency` cur ON cur.name = gl.account_currency
#		WHERE is_cancelled = 0
#		{conditions}
#		ORDER BY gl.voucher_no
#		""".format(
#			conditions=get_conditions(filters),
#		),
#		filters,as_dict=1
#	)
#	return gl_entries
def get_gl_entries(filters):
	gl_entries = frappe.db.sql("""
		SELECT 
			gl.name as gl_entry, gl.posting_date, 
			a.account_name as buku, a.account_number as lawan,
			gl.cost_center,
			gl.remarks as keterangan, gl.account as against, gl.against as account,
			gl.debit as credit, gl.credit as debit,
			gl.voucher_type, gl.voucher_no
			FROM `tabGL Entry` gl left join `tabAccount` a on gl.account=a.name
		WHERE gl.is_cancelled = 0
		{conditions}
		order by gl.posting_date, gl.voucher_type, gl.voucher_no
	""".format(
			conditions=get_conditions(filters),
		),
		 as_dict=1, debug=1
	)

	return gl_entries

def get_conditions(filters):
	conditions = []

	if filters.account:
		#conditions.append(" (gl.against = %(account)s or gl.account= %(account)s) ")
		#conditions.append(" gl.against = %(account)s ")
		#frappe.msgprint(""" gl.against LIKE "%{}%" """.format(filters.get("account")))
		conditions.append(""" is_opening="No" and gl.against LIKE "%{0}%" and gl.account != "{0}" """.format(filters.get("account")))
#	if filters.against: 
#		conditions.append("account = %(against)s")

	if filters.cost_center:
		conditions.append("""gl.cost_center = {} """.format(filters.get("cost_center")))

	conditions.append(""" gl.posting_date <= "{}" and gl.posting_date >= "{}" """.format(filters.get("to_date"),filters.get("from_date")))

	return "and {}".format(" and ".join(conditions)) if conditions else ""

def get_data_with_opening_closing(filters, gl_entries):
	data = []
	opening = frappe.db.sql("select sum(debit-credit) as total from `tabGL Entry` where (posting_date <'{}'  or is_opening='Yes') and account='{}' and is_cancelled = 0 group by account ".format(filters.get("from_date"),filters.get("account")),as_list=1)
	nilai_opening=0
	if opening:
		nilai_opening=flt(opening[0][0])
	totals, entries = get_accountwise_gle(filters, gl_entries , nilai_opening)

	# Opening for filtered account
	data.append(totals.opening)

	data += entries

	# totals
	data.append(totals.total)

	# closing
	data.append(totals.closing)

	return data

def get_totals_dict():
	def _get_debit_credit_dict(label):
		return _dict(
			buku="{0}".format(label),
			lawan="{0}".format(label),
			debit=0.0,
			credit=0.0,
			debit_in_account_currency=0.0,
			credit_in_account_currency=0.0,
		)

	return _dict(
		opening=_get_debit_credit_dict(TRANSLATIONS.OPENING),
		total=_get_debit_credit_dict(TRANSLATIONS.TOTAL),
		closing=_get_debit_credit_dict(TRANSLATIONS.CLOSING_TOTAL),
	)

def get_accountwise_gle(filters, gl_entries,opening):
	totals = get_totals_dict()
	entries = []
	consolidated_gle = OrderedDict()

	def update_value_in_dict(data, key, gle):
		data[key].debit += gle.debit
		#data[key].debit += gle.credit
		data[key].credit += gle.credit
		#data[key].credit += gle.debit

	from_date, to_date = getdate(filters.from_date), getdate(filters.to_date)
	if opening > 0 :
		totals["opening"].debit += opening
		totals["closing"].debit += opening
	else:
		totals["opening"].credit += opening*-1
		totals["closing"].credit += opening*-1
	for gle in gl_entries:
		#frappe.msgprint("{}".format(gle))
		group_by_value = gle.get('account')
#		if gle.posting_date < from_date:
#			update_value_in_dict(totals, "opening", gle)
#			update_value_in_dict(totals, "closing", gle)
#		el
		if gle.posting_date <= to_date:
			keylist = [
				gle.get("voucher_type"),
				gle.get("voucher_no"),
				gle.get("account"),
				gle.get("gl_entry")
			]

			key = tuple(keylist)
			if key not in consolidated_gle:
				consolidated_gle.setdefault(key, gle)
			else:
				update_value_in_dict(consolidated_gle, key, gle)
	
	for key, value in consolidated_gle.items():
		update_value_in_dict(totals, "total", value)
		update_value_in_dict(totals, "closing", value)
		entries.append(value)

	return totals, entries

def get_result_as_list(data, filters):
	balance, balance_in_account_currency = 0, 0

	for d in data:
		if not d.get("posting_date"):
			balance, balance_in_account_currency = 0, 0

		balance = get_balance(d, balance, "debit", "credit")
		d["balance"] = balance

	return data

def get_balance(row, balance, debit_field, credit_field):
	balance += row.get(debit_field, 0) - row.get(credit_field, 0)

	return balance

def get_column():
	company = get_default_company()
	currency = get_company_currency(company)

	columns = [
		{"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
		{
			"label": _("Buku"), 
			"fieldname": "buku", 
			"fieldtype": "Data", 
			"width": 150
		},
		{
			"label": _("Lawan"), 
			"fieldname": "lawan", 
			"fieldtype": "Data", 
			"width": 150
		},
		{
			"label": _("Cost Center"),
			"fieldname": "cost_center",
			"fieldtype": "Link",
			"options": "Cost Center",
			"width": 150
		},
		{
			"label": _("Keterangan"), 
			"fieldname": "keterangan", 
			"fieldtype": "Data", 
			"width": 150
		},
		# {
		# 	"label": _("Debit"), 
		# 	"fieldname": "account", 
		# 	"fieldtype": "Link",
		# 	"options": "Account",
		# 	"width": 150
		# },
		# {
		# 	"label": _("Credit"), 
		# 	"fieldname": "against", 
		# 	"fieldtype": "Link",
		# 	"options": "Account",
		# 	"width": 150
		# },
		{
			"label": _("Masuk ({0})").format(currency),
			"fieldname": "debit",
			"fieldtype": "Float",
			"width": 150,
		},
		{
			"label": _("Keluar ({0})").format(currency),
			"fieldname": "credit",
			"fieldtype": "Float",
			"width": 150,
		},
		{
			"label": _("Saldo ({0})").format(currency),
			"fieldname": "balance",
			"fieldtype": "Float",
			"width": 150,
		},
		{
			"label": _("Proses"), 
			"fieldname": "proses", 
			"fieldtype": "Data", 
			"width": 150
		},
		{
			"label": _("Penyebab"), 
			"fieldname": "voucher_type", 
			"fieldtype": "Data", 
			"width": 150
		},
		{
			"label": _("Dok No"), 
			"fieldname": "voucher_no", 
			"fieldtype": "Dynamic Link",
			"options": "voucher_type",
			"width": 150
		},
	]
	# columns = [
	# 	"Name:Link/GL Entry:150",
	# 	"Keterangan:Data:150",
	# 	"Cost Center:Link/Cost Center:150",
	# 	"Remarks:Data:150",
	# 	"Debit:Link/Account:150",
	# 	"Credit:Link/Account:150",
	# 	"Masuk:Data:150",
	# 	"Keluar:Data:150",
	# 	"Saldo:Data:150",
	# 	"Proses:Data:150",
	# 	"Penyebab:Data:150",
	# 	"Dok No:Data:150",
	# ]

	return columns
