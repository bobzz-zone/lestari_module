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
# 		select gp.posting_date,"Customer Deposit" as "type" , gp.name as "voucher_no" ,gp.customer,gp.subcustomer,gp.sales_bundle, (gold_left*-1) as outstanding , (idr_left*-1) as "titipan"
# 		from `tabCustomer Deposit` gp where docstatus=1 and (idr_left >0  or gold_left >0) and (customer="{0}" or subcustomer="{0}")
# 		) x left join `tabSales Stock Bundle` sb on x.sales_bundle = sb.name
# 		order by x.posting_date asc
# 		""".format(filters.get("customer")), as_list=1)
# 	balance=0
# 	for row in mutasi:
# 		balance=balance+flt(row[6])
# 		data.append([row[0],row[1],row[2],row[3],row[4],row[5],row[6],balance,row[7]])
# 	return columns, data

def execute(filters=None):
	columns, data = ["Date:Date:150","Type:Data:150","Voucher No:Data:150","Customer:Data:150", "Sales Bundle:Data:150","Remark:Data:150","Invoice:Currency:150","Pembayaran:Currency:150","Saldo:Currency:150"], []
	mutasi = frappe.db.sql("""select gl.posting_date,gl.account,gl.voucher_type,gl.voucher_no,gl.party,gi.bundle,gl.debit,gl.credit 
		from `tabGL Entry` gl left join `tabGold Invoice` gi on gl.voucher_type="Gold Invoice" and gl.voucher_no=gi.name
		where gl.voucher_type in ("Gold Invoice","Gold Payment") and gl.is_cancelled=0 
		and gl.posting_date >="{0}" and gl.posting_date <="{1}" 
		 and voucher_no in (select voucher_no from `tabGL Entry` gld where gld.party="{2}" and gld.party_type="Customer" and gld.voucher_type in ("Gold Invoice","Gold Payment") and gld.is_cancelled=0 and gld.posting_date >="{0}" and gld.posting_date <="{1}")
		order by posting_date asc,voucher_no
		""".format(filters.get("from_date"),filters.get("to_date"),filters.get("customer")),as_dict=1)
	frappe.msgprint("""select gl.posting_date,gl.account,gl.voucher_type,gl.voucher_no,gl.party,gi.bundle,gl.debit,gl.credit 
		from `tabGL Entry` gl left join `tabGold Invoice` gi on gl.voucher_type="Gold Invoice" and gl.voucher_no=gi.name
		where gl.voucher_type in ("Gold Invoice","Gold Payment") and gl.is_cancelled=0 
		and gl.posting_date >="{0}" and gl.posting_date <="{1}" 
		 and voucher_no in (select voucher_no from `tabGL Entry` gld where gld.party="{2}" and gld.party_type="Customer" and gld.voucher_type in ("Gold Invoice","Gold Payment") and gld.is_cancelled=0 and gld.posting_date >="{0}" and gld.posting_date <="{1}")
		order by posting_date asc,voucher_no
		""".format(filters.get("from_date"),filters.get("to_date"),filters.get("customer")))
	gp_data = frappe.db.sql("""select gp.name,GROUP_CONCAT(d.gold_invoice SEPARATOR ',') as inv, gp.sales_bundle , gp.customer
		from `tabGold Payment Invoice` d join `tabGold Payment` gp on d.parent=gp.name 
		where gp.customer="{}" and gp.posting_date >="{}" and gp.posting_date <="{}"  group by d.parent
		""".format(filters.get("customer"),filters.get("from_date"),filters.get("to_date")),as_dict=1)
	gp_info = {}
	for row in gp_data:
		gp_info[row['name']]={}
		gp_info[row['name']]["sales_bundle"]=row['sales_bundle']
		gp_info[row['name']]["inv"]=row['inv']
		gp_info[row['name']]["party"]=row['customer']
	
	balance=0
	for row in mutasi:
		if row['voucher_type']=="Gold Payment" and row['party']:
			continue
		elif row['voucher_type']=="Gold Invoice":
			balance=balance+flt(row['debit'])
			data.append([row['posting_date'],row['voucher_type'],row['voucher_no'],filters.get("customer"),row['bundle'],row["account"],row['debit'],0,balance])
		else:
			balance=balance-flt(row['debit'])
			data.append([row['posting_date'],row['voucher_type'],row['voucher_no'],filters.get("customer"),gp_info[row['voucher_no']]["sales_bundle"],"{} => {}".format(row["account"],gp_info[row['voucher_no']['inv']]),0,row['debit'],balance])
	return columns, data
# def execute(filters=None):
# 	columns, data = ["Date:Date:150","Type:Data:150","Voucher No:Data:150","Customer:Data:150", "Sales Bundle:Data:150","Sales:Data:150","Debit:Currency:150","Kredit:Currency:150","Saldo:Currency:150"], []

# 	mutasi = frappe.db.sql("""
# 		SELECT
# 		a.posting_date,
# 		a.name AS voucher_no,
# 		a.customer,
# 		a.sales_bundle,
# 		a.write_off,
# 		a.`allocated_payment`,
# 		a.`tutupan`,
# 		a.`total_idr_payment`,
# 		a.`total_gold_payment`,
# 		b.`gold_invoice`,
# 		b.`tutupan`,
# 		b.`allocated`,
# 		b.`tax_allocated`,
# 		c.`mode_of_payment`,
# 		c.`amount`
# 		FROM
# 		`tabGold Payment` a
# 		JOIN
# 		`tabGold Payment Invoice` b
# 		ON a.name = b.parent
# 		JOIN
# 		`tabIDR Payment` c
# 		ON a.name = c.parent AND b.idx = c.idx
# 	WHERE a.customer = "{}" AND a.docstatus = 1
# 	ORDER BY b.gold_invoice ASC
# 	""".format(filters.get("customer")), as_dict=1)
# 	# mutasi = frappe.db.get_list("Gold Payment", filters={"customer":filters.get("customer")}, order_by="name ASC")
# 	# frappe.msgprint(str(mutasi))
# 	index = 0 
# 	lengthmutasi = len(mutasi)
# 	# frappe.msgprint(str(lengthmutasi))
# 	for row in mutasi:
# 	# 	doc = frappe.get_doc("Gold Payment",row.name)
# 		sales = frappe.db.get_value("Sales Stock Bundle", row.sales_bundle, 'sales')
# 		debit = (row.allocated*row.tutupan)+row.tax_allocated
# 		if row.total_gold_payment:
# 			if row.total_gold_payment > 0:
# 				kredit = ( row.allocated * row.tutupan ) + row.amount
# 		else:
# 			kredit = row.amount

# 		if index == 0:
# 			saldo = debit
# 			data.append(["","Opening","","","","",0,0,saldo])
# 			saldo = debit
# 			data.append([row.posting_date,"Gold Invoice",row.gold_invoice,row.customer,row.sales_bundle,sales,debit,0,saldo])
# 			saldo = debit - kredit
# 			data.append([row.posting_date,"Pembayaran Penjualan",row.voucher_no,row.customer,row.sales_bundle,sales,0,kredit,saldo])
# 			if saldo < 0.000:
# 				data.append([row.posting_date,"Write Off",row.voucher_no,row.customer,row.sales_bundle,sales,0,saldo,saldo])
# 			elif saldo > 0.000:
# 				data.append([row.posting_date,"Write Off",row.voucher_no,row.customer,row.sales_bundle,sales,saldo,0,saldo])
# 		else:
# 			saldo = saldo + debit
# 			data.append([row.posting_date,"Gold Invoice",row.gold_invoice,row.customer,row.sales_bundle,sales,debit,0,saldo])
# 			saldo = saldo - kredit
# 			data.append([row.posting_date,"Pembayaran Penjualan",row.voucher_no,row.customer,row.sales_bundle,sales,0,kredit,saldo])
# 			if saldo < 0.000:
# 				data.append([row.posting_date,"Write Off",row.voucher_no,row.customer,row.sales_bundle,sales,(saldo*-1),0,saldo])
# 			elif saldo > 0.000:
# 				data.append([row.posting_date,"Write Off",row.voucher_no,row.customer,row.sales_bundle,sales,0,saldo,saldo])


# 		if index < lengthmutasi-1:
# 			index += 1
# 		else:
# 			saldo = saldo + debit - kredit
# 			data.append(["","Closing","","","","",0,0,saldo])
# 	return columns, data



	# mutasi=frappe.db.sql("""SELECT
	# 	ab.posting_date,
	# 	ab.type,
	# 	ab.voucher_no,
	# 	ab.customer,
	# 	ab.sales_bundle,
	# 	sb.sales,
	# 	ab.write_off,
	# 	ab.debit,
	# 	ab.kredit
	# 	FROM
	# 	(SELECT
	# 		gi.posting_date,
	# 		"Gold Invoice" AS "type",
	# 		gi.name AS "voucher_no",
	# 		gi.customer,
	# 		gi.bundle AS "sales_bundle",
	# 		0 AS write_off,
	# 		(total_setelah_pajak) AS debit,
	# 		0 AS "kredit"
	# 	FROM
	# 		`tabGold Invoice` gi
	# 	WHERE gi.docstatus = 1
	# 		AND gi.customer = "{0}"
	# 	UNION
	# 	SELECT
	# 		gp.posting_date,
	# 		"Pembayaran Penjualan" AS "type",
	# 		gp.name AS "voucher_no",
	# 		gp.customer,
	# 		gp.sales_bundle,
	# 		(gp.write_off * gp.tutupan) AS write_off,
	# 		0 AS debit,
	# 		(
	# 		(
	# 			gp.allocated_payment * gp.tutupan
	# 		) + gp.total_idr_payment
	# 		) AS "kredit"
	# 	FROM
	# 		`tabGold Payment` gp
	# 	WHERE gp.docstatus = 1
	# 		AND gp.customer = "{0}") ab
	# 	LEFT JOIN `tabSales Stock Bundle` sb
	# 		ON ab.sales_bundle = sb.name
	# ORDER BY ab.posting_date ASC
	# 	""".format(filters.get("customer")), as_dict=1)
	# frappe.msgprint(str(mutasi))