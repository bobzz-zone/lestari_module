
import frappe
import random

import datetime

def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    return next_month - datetime.timedelta(days=next_month.day)

def first_day_of_month(any_day):
	next_month = any_day.replace(day=1)
	return next_month


@frappe.whitelist()
def debug_start_generate():
	start_generate(2024,"January")

@frappe.whitelist()
def start_generate(year,month):
	month_name = month
	month_number = 0
	if month_name == "January":
		month_number = 1
	elif month_name == "February":
		month_number = 2
	elif month_name == "March":
		month_number = 3
	elif month_name == "April":
		month_number = 4
	elif month_name == "May":
		month_number = 5
	elif month_name == "June":
		month_number = 6
	elif month_name == "July":
		month_number = 7
	elif month_name == "August":
		month_number = 8
	elif month_name == "September":
		month_number = 9
	elif month_name == "October":
		month_number = 10
	elif month_name == "November":
		month_number = 11
	elif month_name == "December":
		month_number = 12

	first_day = first_day_of_month(datetime.date(int(year), month_number, 1))
	last_day = last_day_of_month(datetime.date(int(year), month_number, 1))

	lis_gold_invoice = frappe.db.sql(""" 
		SELECT gi.name,gi.sales_partner as sales_partner,gi.posting_date, gii.kadar, SUM(gii.qty) as qty, gi.bundle FROM 
		`tabGold Invoice` gi
		JOIN `tabGold Invoice Item` gii ON gii.parent = gi.name

		WHERE DATE(gi.posting_date) >= DATE("{}")
		AND DATE(gi.posting_date) <= DATE("{}")

		GROUP BY gi.sales_partner,gi.posting_date, gii.kadar, gi.bundle
		ORDER BY gi.sales_partner,gi.posting_date 
		
		""".format(str(first_day),str(last_day)),as_dict=1)
	log = ""
	for row in lis_gold_invoice:
		check_penyerahan = frappe.db.sql(""" SELECT 
				ubs.name
				FROM `tabUpdate Bundle Stock` ubs JOIN
				`tabDetail Penambahan Stock` dps ON dps.parent = ubs.name
				WHERE ubs.`sales` = "{}" AND dps.`kadar` = "{}" 
				AND ubs.type = "New Stock" AND ubs.bundle = "{}" """.format(row.sales_partner,row.kadar,row.bundle))
		
		new_doc = frappe.new_doc("Update Bundle Stock")
		new_doc.posting_date = row.posting_date
		new_doc.bundle = row.bundle

		if len(check_penyerahan) == 0:
			new_doc.type = "New Stock"
		else:
			new_doc.type = "Add Stock"

		new_doc.s_warehouse = "Stockist - LMS"
		new_doc.purpose = "Sales"
		new_doc.sales = row.sales_partner
		new_doc.warehouse = frappe.get_doc("Sales Partner",new_doc.sales).warehouse
		if row.kadar == "06K":
			new_doc.id_employee = 1240
		if row.kadar == "08K":
			new_doc.id_employee = 1147
		if row.kadar == "16K":
			new_doc.id_employee = 1194
		if row.kadar == "08KP" or row.kadar == "10K" or row.kadar == "17K" or row.kadar == "19K" or row.kadar == "20K":
			new_doc.id_employee = 1225
		else:
			new_doc.id_employee = 1656		

		item = frappe.get_doc("Item",{"kadar":row.kadar,"item_group":"Perhiasan","item_group_parent":"Pembayaran"})

		new_doc.append("items",{
			"sub_category" : "Perhiasan",
			"kadar" : row.kadar,
			"qty_penambahan" : row.qty,
			"item": item.name ,
			"gold_selling_item": item.gold_selling_item
		})

		new_doc.append("per_kadar",{
			"kadar" : row.kadar,
			"bruto" : row.qty,
		})

		new_doc.per_sub_category = []
		for new_doc_row in new_doc.items:
			input_warehouse = new_doc.s_warehouse
			input_kadar = row.kadar
			kebutuhan = row.qty

			result = randomizer(input_warehouse, input_kadar, kebutuhan)

			for baris_result in result:
				new_doc.append("per_sub_category",{
					"item": baris_result[0] ,
					"item_name": frappe.get_doc("Item",baris_result[0]).item_name,
					"bruto": frappe.utils.flt(baris_result[1]),
					"kadar": row.kadar
				})

		new_doc.save()
		frappe.db.commit()

		if log != "":
			log += ("{}-{}-{}-{}-{}".format(datetime.datetime.now(),new_doc.name,row.sales_partner, row.kadar, row.bundle, len(check_penyerahan)))
		else:
			log = ("{}-{}-{}-{}-{}".format(datetime.datetime.now(),new_doc.name,row.sales_partner, row.kadar, row.bundle, len(check_penyerahan)))
		
		doc_log = frappe.get_doc("Randomizer Bundle")
		doc_log.log = log
		doc_log.save()
		doc_log.reload()

	# generate pengembalian
	list_pengembalian = frappe.db.sql(""" 
		SELECT gi.name,gi.sales_partner AS sales_partner,
		gi.posting_date, gii.kadar, SUM(gii.qty) AS qty, gi.bundle FROM 
		`tabGold Invoice` gi
		JOIN `tabGold Invoice Item` gii ON gii.parent = gi.name

		WHERE DATE(gi.posting_date) >= DATE("{}")
		AND DATE(gi.posting_date) <= DATE("{}")

		GROUP BY gi.sales_partner, gii.kadar, gi.bundle
		ORDER BY gi.sales_partner,gi.posting_date 
	; """.format(str(first_day),str(last_day)),as_dict=1)

	for row in list_pengembalian:
		get_transfer_salesman = frappe.db.sql(""" SELECT ubs.`bundle`, ubs.`sales`, ubss.kadar, SUM(ubss.bruto)
			FROM 
			 `tabUpdate Bundle Stock` ubs 
			JOIN `tabUpdate Bundle Stock Sub` ubss ON ubss.parent = ubs.name 

			WHERE ubs.`bundle` = "{}"
			AND ubs.`sales` = "{}"
			AND ubss.kadar = "{}"
			AND ubss.bruto IS NOT NULL
			GROUP BY ubs.bundle, ubss.kadar, ubs.`sales`;

		""".format(row.bundle, row.sales_partner, row.kadar))

		keluar = get_transfer_salesman[0][3]
		masuk = row.qty

		if frappe.utils.flt(keluar) > frappe.utils.flt(masuk):
			new_doc = frappe.new_doc("Update Bundle Stock")
			new_doc.posting_date = last_day
			new_doc.bundle = row.bundle
			new_doc.type = "Deduct Stock"
			
			new_doc.s_warehouse = "Stockist - LMS"
			new_doc.purpose = "Sales"
			new_doc.sales = row.sales_partner
			new_doc.warehouse = frappe.get_doc("Sales Partner",new_doc.sales).warehouse

			item = frappe.get_doc("Item",{"kadar":row.kadar,"item_group":"Perhiasan","item_group_parent":"Pembayaran"})

			new_doc.append("items",{
				"sub_category" : "Perhiasan",
				"kadar" : row.kadar,
				"qty_penambahan" : frappe.utils.flt(keluar) - frappe.utils.flt(masuk),
				"item": item.name ,
				"gold_selling_item": item.gold_selling_item
			})

			new_doc.append("per_kadar",{
				"kadar" : row.kadar,
				"bruto" : frappe.utils.flt(keluar) - frappe.utils.flt(masuk),
			})

			new_doc.save()
			frappe.db.commit()




@frappe.whitelist()
def generate_list():
	lis_gold_invoice = frappe.db.sql(""" 
		SELECT gi.name,gi.sales_partner,gi.posting_date, gii.kadar, gii.qty FROM 
		`tabGold Invoice` gi
		JOIN `tabGold Invoice Item` gii ON gii.parent = gi.name

		WHERE DATE(gi.posting_date) >= DATE("2024-01-01")
		AND DATE(gi.posting_date) <= DATE("2024-01-31")

		ORDER BY gi.sales_partner,gi.posting_date  """)

@frappe.whitelist()
def randomizer_debug():
	warehouse = "Stockist - LMS"
	item_group = "Pembayaran"
	kadar = "09K"

	list_item = frappe.db.sql(""" 
		SELECT tb.item_code,tb.actual_qty FROM `tabBin` tb
		JOIN `tabItem` ti ON ti.name = tb.item_code
		WHERE tb.actual_qty > 0
		AND tb.warehouse = "{}"
		AND ti.barang_yang_dibawa_sales = "{}"
		AND ti.item_group = "{}"
		AND ti.kadar = "{}"
	""".format(warehouse,1,item_group,kadar))

	
	total_item = 0
	kebutuhan = 842
	for row in list_item:
		total_item = total_item+frappe.utils.flt(row[1])

	kebutuhan_min = kebutuhan * 1.05
	kebutuhan_max = min(kebutuhan * 1.10, total_item)

	if total_item < kebutuhan:
		frappe.msgprint("Item dengan kadar {} tidak cukup barang di gudang Stockist.".format(kadar))

	if frappe.utils.flt(kebutuhan_min) == frappe.utils.flt(total_item):
		for row in list_item:
			result.append([row[0],row[1]])
	else:
		result = generate_list(list_item, kebutuhan_min, kebutuhan_max)

	print(result)


@frappe.whitelist()
def randomizer(input_warehouse,input_kadar,kebutuhan):
	warehouse = input_warehouse
	item_group = "Pembayaran"
	kadar = input_kadar
	result = []
	list_item = frappe.db.sql(""" 
		SELECT tb.item_code,tb.actual_qty FROM `tabBin` tb
		JOIN `tabItem` ti ON ti.name = tb.item_code
		WHERE tb.actual_qty > 0
		AND tb.warehouse = "{}"
		AND ti.barang_yang_dibawa_sales = "{}"
		AND ti.item_group = "{}"
		AND ti.kadar = "{}"
	""".format(warehouse,1,item_group,kadar))

	
	total_item = 0
	for row in list_item:
		total_item = total_item+frappe.utils.flt(row[1])

	kebutuhan_min = kebutuhan * 1.10
	kebutuhan_max = min(kebutuhan * 1.20, total_item)

	if total_item < kebutuhan:
		frappe.msgprint("Item dengan kadar {} tidak cukup barang di gudang Stockist.".format(kadar))
		return result

	if frappe.utils.flt(kebutuhan_min) == frappe.utils.flt(total_item):
		for row in list_item:
			result.append([row[0],row[1]])
	else:
		result = generate_list(list_item, kebutuhan_min, kebutuhan_max)

	return result

def generate_list(list_item, kebutuhan_min, kebutuhan_max):
    temp_list = list(list_item)  # Create a copy of the original list
    result_list = []

    while True:
        random.shuffle(temp_list)
        result_list = []
        kebutuhan = 0
        for item in temp_list:
            item_code, actual_qty = item
            qty_random = round(random.uniform(0, min(actual_qty, kebutuhan_min)), 2)
            
            result_list.append([item_code, qty_random])
            kebutuhan += qty_random

            if kebutuhan >= kebutuhan_min and kebutuhan <= kebutuhan_max:
                return result_list