# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt

# def execute(filters=None):
# 	columns, data = ["Date:Date:150","Type:Data:150","Voucher No:Data:150","Customer:Data:150","SubCustomer:Data:150","Sales:Data:150","Outstanding:Float:150","Balance Gold:Float:150","Total Titipan Rupiah:Currency:150"], []
	
# 	mutasi=frappe.db.sql("""select x.posting_date,x.type,x.voucher_no,x.customer,x.subcustomer, sb.sales,x.outstanding,x.titipan from 
# 		(select gi.posting_date ,"Gold Invoice" as "type" ,gi.name as "voucher_no" ,gi.customer,gi.subcustomer, gi.bundle as "sales_bundle", outstanding , 0 as "titipan"
# 		from `tabGold Invoice` gi where docstatus=1 and outstanding>0 and (customer="{0}" or subcustomer="{0}")
# 		UNION 
# 		select cd.posting_date,"Customer Deposit" as "type" , cd.name as "voucher_no" ,cd.customer,cd.subcustomer,cd.sales_bundle, (gold_left*-1) as outstanding , (idr_left*-1) as "titipan"
# 		from `tabCustomer Deposit` cd where docstatus=1 and (idr_left >0  or gold_left >0) and (customer="{0}" or subcustomer="{0}")
# 		) x left join `tabSales Stock Bundle` sb on x.sales_bundle = sb.name
# 		order by x.posting_date asc
# 		""".format(filters.get("customer")), as_list=1)
# 	balance=0
# 	for row in mutasi:
# 		balance=balance+flt(row[6])
# 		data.append([row[0],row[1],row[2],row[3],row[4],row[5],row[6],balance,row[7]])
# 	return columns, data

def execute(filters=None):
	columns, data = ["Date:Date:150","Type:Data:150","Voucher No:Data:150","Customer:Data:150","SubCustomer:Data:150","Sales:Data:150","Debit:Float:150","Kredit:Float:150","Balance Gold:Float:150","Total Titipan Rupiah:Currency:150"], []
	
	mutasi=frappe.db.sql("""select x.posting_date,x.type,x.voucher_no,x.customer,x.subcustomer, sb.sales,x.debit,x.kredit,x.titipan,x.is_convert , x.total_value_converted from 
		
		(
		select gi.posting_date ,"Gold Invoice" as "type" ,gi.name as "voucher_no" ,gi.customer,gi.subcustomer, gi.bundle as "sales_bundle", grand_total as debit, 0 as "kredit" , 0 as "titipan" ,0 as is_convert , 0 as total_value_converted
		from `tabGold Invoice` gi where docstatus=1  and (customer="{0}" or subcustomer="{0}")
		UNION 
		select cd.posting_date,"Customer Deposit" as "type" , cd.name as "voucher_no" ,cd.customer,cd.subcustomer,cd.sales_bundle, 0 as debit , total_gold_deposit as "kredit" , (total_idr_deposit ) as "titipan" , is_convert , total_value_converted
		from `tabCustomer Deposit` cd where docstatus=1 and (customer="{0}" or subcustomer="{0}") and deposit_payment=0
		UNION 
		select cd.posting_date,"Gold Payment" as "type" , cd.name as "voucher_no" ,cd.customer,cd.subcustomer,cd.sales_bundle, 0 as debit , (total_gold_payment+total_idr_gold) as "kredit" , 0 as "titipan" , 0 as is_convert , 0 as total_value_converted
		from `tabGold Payment` cd where docstatus=1 and (customer="{0}" or subcustomer="{0}") 
		
		) x 

		left join `tabSales Stock Bundle` sb on x.sales_bundle = sb.name
		order by x.posting_date asc
		""".format(filters.get("customer")), as_list=1)
	balance=0
	for row in mutasi:
		balance=balance+flt(row[6])-flt(row[7])
		titipan = row[8]
		if row[9]==1:
			titipan = row[9]*-1
		data.append([row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],balance,titipan])
	return columns, data