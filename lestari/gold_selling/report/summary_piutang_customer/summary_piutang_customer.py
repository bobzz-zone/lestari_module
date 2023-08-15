# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt

def execute(filters=None):
	columns, data = ["Customer:Link/Customer:150","Total Invoice:Float:150","Total Paid:Float:150","Invoice Outstanding:Float:150","Total Titipan Gold:Float:150","Total Titipan Rupiah:Currency:150"], []
	#data Gold Invoice
	gold_invoice=frappe.db.sql("""select customer,sum(grand_total) as total, sum(outstanding) as sisa from `tabGold Invoice` where outstanding >0 and docstatus=1 group by customer""",as_dict=1)
	customer_data={}
	for row in gold_invoice:
		customer_data[row["customer"]]={}
		customer_data[row["customer"]]["customer"]=row["customer"]
		customer_data[row["customer"]]["total"]=row["total"]
		customer_data[row["customer"]]["paid"]=flt(row["total"])-flt(row["sisa"])
		customer_data[row["customer"]]["outstanding"]=row["sisa"]
		customer_data[row["customer"]]["idr"]=0
		customer_data[row["customer"]]["gold"]=0
	deposit=frappe.db.sql("""select customer, sum(idr_left) as "idr", sum(gold_left) as "gold" from `tabCustomer Deposit` where docstatus=1 and (idr_left >0  or gold_left >0) group by customer  """,as_dict=1)
	for row in deposit:
		if row["customer"] not in customer_data:
			customer_data[row["customer"]]={}
			customer_data[row["customer"]]["customer"]=0
			customer_data[row["customer"]]["total"]=0
			customer_data[row["customer"]]["paid"]=0
			customer_data[row["customer"]]["outstanding"]=0
		customer_data[row["customer"]]["idr"]=row["idr"]
		customer_data[row["customer"]]["gold"]=row["gold"]
	for row in customer_data:
		data.append([row,customer_data[row]["total"],customer_data[row]["paid"],customer_data[row]["outstanding"],customer_data[row]["gold"],customer_data[row]["idr"]])
	return columns, data
