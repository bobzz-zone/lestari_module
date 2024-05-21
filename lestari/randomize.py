import frappe
import random
import pandas as pd
import datetime
from frappe.utils import getdate
from datetime import datetime, timedelta, date
from faker import Faker
# from lestari.stockist.doctype.update_bundle_stock.update_bundle_stock import create_gdle

def save_to_excel(log_data, filename):
    df = pd.DataFrame(log_data)
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Log', index=False)
    writer.save()

def get_monday_of_date(date_str):
    # Konversi string tanggal ke objek datetime
    tgl = datetime.strptime(str(date_str), '%Y-%m-%d')
    # Hitung perbedaan antara hari Senin dan hari saat ini
    offset = (tgl.weekday() - 0) % 7
    # Kurangi offset dari tanggal saat ini untuk mendapatkan hari Senin
    monday = tgl - timedelta(days=offset)

    return monday.strftime('%Y-%m-%d')

    # # Contoh input tanggal penjualan
    # str(date_str) = "09-05-2023"

    # # Dapatkan hari Senin untuk tanggal penjualan
    # monday = get_monday_of_date(date_str)

    # print(monday.strftime('%Y-%m-%d'))

def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)

def first_day_of_month(any_day):
	next_month = any_day.replace(day=1)
	return next_month


@frappe.whitelist()
def debug_print_calendar():
	print_calendar("2024-01-01","2024-01-18")

@frappe.whitelist()
def print_calendar(str_start_date,str_end_date):
	# PERLU PIP INSTALL FAKER
	fake = Faker()

	start_date = datetime.strptime(str(str_start_date), '%Y-%m-%d')
	end_date = datetime.strptime(str(str_end_date), '%Y-%m-%d') - timedelta(days=1)

	check = 0 

	while check == 0:
		# final_date = fake.date_between(start_date=start_date, end_date=end_date)
		final_date = get_monday_of_date(str_end_date)
		# print(final_date)
		check_holiday = frappe.db.sql(""" SELECT name FROM `tabHoliday` WHERE holiday_date = "{}" """.format(str(final_date)))
		if len(check_holiday) == 0:
			check = 1
	
	print(final_date)
	return(str(final_date))


@frappe.whitelist()
def debug_start_generate():
	start_generate(2023,"May","SKS230501")

@frappe.whitelist()
def start_generate(year,month,bundle=None):
	print("-- Initiate Generate --")
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

	month_number = int(month_number)
	year = int(year)
	
	print("-- Get Month Name '"+month_name+"' --")
	first_day = first_day_of_month(date(year, month_number, 1))
	print("-- Get First Day '"+str(first_day)+"' --")
	last_day = last_day_of_month(date(year, month_number, 1))
	print("-- Get Last Day '"+str(last_day)+"' --")

	addons = ""
	if bundle:
		addons = """ AND gi.bundle = "{}" """.format(bundle)

	lis_gold_invoice = frappe.db.sql(""" 
		SELECT gi.name,gi.sales_partner as sales_partner,gi.posting_date, gii.kadar, SUM(gii.qty) as qty, gi.bundle FROM 
		`tabGold Invoice` gi
		JOIN `tabGold Invoice Item` gii ON gii.parent = gi.name
		WHERE DATE(gi.posting_date) >= DATE("{}")
		AND DATE(gi.posting_date) <= DATE("{}")
		
		{}

		AND gi.docstatus = 1

		GROUP BY gi.sales_partner,gi.posting_date, gii.kadar, gi.bundle
		ORDER BY gi.sales_partner,gi.posting_date, gi.bundle, gii.kadar 
		
		""".format(str(first_day),str(last_day),addons),as_dict=1, debug=True)
	print("-- Get List Gold Invoice "+str(len(lis_gold_invoice))+"--")
	# frappe.throw(str(len(lis_gold_invoice)))
	print("-- Start Looping List Gold Invoice --")


	index = 0
	total_need = 0
	for row in lis_gold_invoice:
		total_need = 0

		print("-- Begin Index 0 --")
		check_penyerahan = frappe.db.sql(""" SELECT 
				ubs.name
				FROM `tabUpdate Bundle Stock` ubs JOIN
				`tabDetail Penambahan Stock` dps ON dps.parent = ubs.name
				WHERE ubs.`sales` = "{}" AND dps.`kadar` = "{}" 
				AND ubs.type = "New Stock" AND ubs.bundle = "{}" 
		""".format(row.sales_partner,row.kadar,row.bundle),debug=True)

		print("-- Get Penyerahan {}-{}-{}-{} --".format(row.sales_partner, row.kadar, row.bundle, len(check_penyerahan)))
		# frappe.throw(str(len(check_penyerahan)))

		bundle_doc = frappe.get_doc("Sales Stock Bundle", row.bundle)

		new_doc = frappe.new_doc("Update Bundle Stock")
		print("-- Create New Transfer Salesman '"+str(new_doc)+"' --")

		print("-- Set Posting Date '"+str(new_doc.date)+"' --")
		new_doc.bundle = row.bundle
		print("-- Set Bundle '"+new_doc.bundle+"' --")

		if len(check_penyerahan) == 0:
			new_doc.type = "New Stock"
			# 1. ganti dengan posting date di bundle + 2. 
			# frappe.throw("aaaa")
			bundle_date = frappe.db.get_value("Sales Stock Bundle",row.bundle,"date")
			bundle_date = datetime.strptime(str(bundle_date), '%Y-%m-%d')
			# new_doc.date = print_calendar(first_day,bundle_date)
			new_doc.date = bundle_date
		else:
			new_doc.type = "Add Stock"
			# kalau penambahan liat dari Tanggal Gold Invoice
			new_doc.date = print_calendar(first_day,row.posting_date)

		print("-- Set Type '"+new_doc.type+"' --")
		new_doc.s_warehouse = "Stockist - LMS"
		new_doc.purpose = "Sales"
		new_doc.sales = row.sales_partner
		new_doc.warehouse = frappe.db.get_value("Sales Partner",new_doc.sales,"warehouse")
		# 6K: Venda 1240
		# 8K: Yeni 1147
        # 16K: Nirma 1194
		# 17K, 19K, 20K, 10K 8K putih): Ika 1225
		# PCB, 17K Putih): Mujiati 1656
		if row.kadar == "06K":
			new_doc.pic = "HR-EMP-00489"
			new_doc.id_employee = 1240
		if row.kadar == "08K":
			new_doc.pic = "HR-EMP-00485"
			new_doc.id_employee = 1147
		if row.kadar == "16K":
			new_doc.pic = "HR-EMP-00486"
			new_doc.id_employee = 1194
		if row.kadar == "17K" or row.kadar == "19K" or row.kadar == "20K" or row.kadar == "10K" or row.kadar == "08KP":
			new_doc.pic = "HR-EMP-00487"
			new_doc.id_employee = 1225
		if row.kadar == "PCB" or row.kadar == "17KP":
			new_doc.pic = "HR-EMP-00490"
			new_doc.id_employee = 1656
		print("-- SET PIC '"+new_doc.pic+"' --") 
		print("-- Start Generate Item Kadar Per Sub Kategori --")
		item = frappe.get_doc("Item",{"kadar":row.kadar,"item_group":"Perhiasan","item_group_parent":"Pembayaran"})
		print("-- Get Item Kadar Per Sub Kategori '"+item.name+"' --")
		print("-- Initiate To Child Per Sub Kategori --")
		new_doc.per_sub_category = []
		# for new_doc_row in new_doc.items:
		input_warehouse = new_doc.s_warehouse
		input_kadar = row.kadar
		kebutuhan = row.qty
		print("-- Start Randomizer --")
		result = randomizer(input_warehouse, input_kadar, kebutuhan, new_doc.type, row.kadar, row.bundle, new_doc.date)
		print("-- End Randomizer --")

		for baris_result in result:
			total_need += frappe.utils.flt(baris_result[1])
			print("-- Append To Child Per Sub Kategori "+baris_result[0]+"--")
			new_doc.append("per_sub_category",{
				"item": baris_result[0] ,
				"item_name": frappe.db.get_value("Item",baris_result[0],"item_name"),
				"bruto": frappe.utils.flt(baris_result[1]),
				"kadar": row.kadar
			})
		print("-- Append To Child Items --")
		new_doc.append("items",{
			"sub_category" : "Perhiasan",
			"kadar" : row.kadar,
			"qty_penambahan" : total_need,
			"item": item.name ,
			"gold_selling_item": item.gold_selling_item
		})
		print("-- Append To Child Per Kadar --")
		new_doc.append("per_kadar",{
			"kadar" : row.kadar,
			"bruto" : total_need,
		})
		new_doc.total_bruto = total_need
		new_doc.save()
		frappe.db.commit()
		("-- Save Doc --")
		# frappe.msgprint(str(new_doc))
		
		# create_gdle(new_doc)
		
		index += 1
		if index == len(lis_gold_invoice):
			print("-- End Index 0 --")
	
	frappe.db.commit()

	import time
	time.sleep(1)

	# generate pengembalian
	list_pengembalian = frappe.db.sql(""" 
		SELECT gi.name,gi.sales_partner AS sales_partner,
		gi.posting_date, gii.kadar, SUM(gii.qty) AS qty, gi.bundle FROM 
		`tabGold Invoice` gi
		JOIN `tabGold Invoice Item` gii ON gii.parent = gi.name

		WHERE DATE(gi.posting_date) >= DATE("{}")
		AND DATE(gi.posting_date) <= DATE("{}")

		AND gi.docstatus = 1

		{}

		GROUP BY gi.sales_partner, gii.kadar, gi.bundle
		ORDER BY gi.sales_partner,gi.posting_date 
	; """.format(str(first_day),str(last_day),addons),as_dict=1)

	# print("masuk list_pengembalian")
	print("Banyak Pengembalian "+str(len(list_pengembalian)))
	for row in list_pengembalian:
		get_transfer_salesman = frappe.db.sql(""" 
			SELECT ubs.`bundle`, ubs.`sales`, ubss.kadar, SUM(ubss.bruto)
			FROM 
			 `tabUpdate Bundle Stock` ubs 
			JOIN `tabUpdate Bundle Stock Sub` ubss ON ubss.parent = ubs.name 

			WHERE ubs.`bundle` = "{}"
			AND ubs.`sales` = "{}"
			AND ubss.kadar = "{}"
			AND ubss.bruto IS NOT NULL
			GROUP BY ubs.bundle, ubss.kadar, ubs.`sales`;

		""".format(row.bundle, row.sales_partner, row.kadar))
		if get_transfer_salesman:
			keluar = get_transfer_salesman[0][3]
			# print(str(get_transfer_salesman[0][3]))
		else:
			keluar = 0
		masuk = row.qty

		if frappe.utils.flt(keluar) >= frappe.utils.flt(masuk):
			new_doc = frappe.new_doc("Update Bundle Stock")
			# print(str(last_day))
			# 6K: Venda 1240
			# 8K: Yeni 1147
			# 16K: Nirma 1194
			# 17K, 19K, 20K, 10K 8K putih): Ika 1225
			# PCB, 17K Putih): Mujiati 1656
			if row.kadar == "06K":
				new_doc.pic = "HR-EMP-00489"
				new_doc.id_employee = 1240
			if row.kadar == "08K":
				new_doc.pic = "HR-EMP-00485"
				new_doc.id_employee = 1147
			if row.kadar == "16K":
				new_doc.pic = "HR-EMP-00486"
				new_doc.id_employee = 1194
			if row.kadar == "17K" or row.kadar == "19K" or row.kadar == "20K" or row.kadar == "10K" or row.kadar == "08KP":
				new_doc.pic = "HR-EMP-00487"
				new_doc.id_employee = 1225
			if row.kadar == "PCB" or row.kadar == "17KP":
				new_doc.pic = "HR-EMP-00490"
				new_doc.id_employee = 1656

			new_doc.date = getdate(last_day)
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

			maksimal_total = frappe.utils.flt(keluar) - frappe.utils.flt(masuk)

			# get_per_kadar_bundle
			get_transfer_stock = frappe.db.sql(""" 
				SELECT ubss.item, ubss.bruto, ubs.`bundle`, ubs.`sales`, ubss.kadar, ubss.item
				FROM 
				 `tabUpdate Bundle Stock` ubs 
				JOIN `tabUpdate Bundle Stock Sub` ubss ON ubss.parent = ubs.name 

				WHERE ubs.`bundle` = "{}"
				AND ubss.kadar = "{}"
				AND ubss.bruto IS NOT NULL
				GROUP BY ubss.item
			""".format(row.bundle, row.kadar),as_dict=1,debug=1)

			item_pengembalian = []

			for row_sub_category in get_transfer_stock:
				item_pengembalian.append([row_sub_category.item, row_sub_category.bruto])

			retur_result = generate_list_retur(item_pengembalian, maksimal_total)
			# print(retur_result)

			for result_row in retur_result:
				new_doc.append("per_sub_category",{
					"item": result_row[0] ,
					"item_name": frappe.db.get_value("Item",result_row[0],"item_name"),
					"bruto": frappe.utils.flt(result_row[1]),
					"kadar": row.kadar
				})

			new_doc.save()
			# frappe.db.commit()
			# create_gdle(new_doc)
	
	frappe.db.commit()


@frappe.whitelist()
def start_generate_hanya_setor(year,month,bundle=None):
	print("-- Initiate Generate --")
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

	month_number = int(month_number)
	year = int(year)
	
	print("-- Get Month Name '"+month_name+"' --")
	first_day = first_day_of_month(date(year, month_number, 1))
	print("-- Get First Day '"+str(first_day)+"' --")
	last_day = last_day_of_month(date(year, month_number, 1))
	print("-- Get Last Day '"+str(last_day)+"' --")

	addons = ""
	if bundle:
		addons = """ AND gi.bundle = "{}" """.format(bundle)

	lis_gold_invoice = frappe.db.sql(""" 
		SELECT gi.name,gi.sales_partner as sales_partner,gi.posting_date, gii.kadar, SUM(gii.qty) as qty, gi.bundle FROM 
		`tabGold Invoice` gi
		JOIN `tabGold Invoice Item` gii ON gii.parent = gi.name
		WHERE DATE(gi.posting_date) >= DATE("{}")
		AND DATE(gi.posting_date) <= DATE("{}")
		
		{}

		AND gi.docstatus = 1

		GROUP BY gi.sales_partner,gi.posting_date, gii.kadar, gi.bundle
		ORDER BY gi.sales_partner,gi.posting_date, gi.bundle, gii.kadar 
		
		""".format(str(first_day),str(last_day),addons),as_dict=1, debug=True)
	print("-- Get List Gold Invoice "+str(len(lis_gold_invoice))+"--")
	# frappe.throw(str(len(lis_gold_invoice)))
	print("-- Start Looping List Gold Invoice --")


	index = 0
	total_need = 0

	# generate pengembalian
	list_pengembalian = frappe.db.sql(""" 
		SELECT gi.name,gi.sales_partner AS sales_partner,
		gi.posting_date, gii.kadar, SUM(gii.qty) AS qty, gi.bundle FROM 
		`tabGold Invoice` gi
		JOIN `tabGold Invoice Item` gii ON gii.parent = gi.name

		WHERE DATE(gi.posting_date) >= DATE("{}")
		AND DATE(gi.posting_date) <= DATE("{}")

		AND gi.docstatus = 1

		{}

		GROUP BY gi.sales_partner, gii.kadar, gi.bundle
		ORDER BY gi.sales_partner,gi.posting_date 
	; """.format(str(first_day),str(last_day),addons),as_dict=1)

	# print("masuk list_pengembalian")
	print("Banyak Pengembalian "+str(len(list_pengembalian)))
	for row in list_pengembalian:
		get_transfer_salesman = frappe.db.sql(""" 
			SELECT ubs.`bundle`, ubs.`sales`, ubss.kadar, SUM(ubss.bruto)
			FROM 
			 `tabUpdate Bundle Stock` ubs 
			JOIN `tabUpdate Bundle Stock Sub` ubss ON ubss.parent = ubs.name 

			WHERE ubs.`bundle` = "{}"
			AND ubs.`sales` = "{}"
			AND ubss.kadar = "{}"
			AND ubss.bruto IS NOT NULL
			GROUP BY ubs.bundle, ubss.kadar, ubs.`sales`;

		""".format(row.bundle, row.sales_partner, row.kadar))
		if get_transfer_salesman:
			keluar = get_transfer_salesman[0][3]
			# print(str(get_transfer_salesman[0][3]))
		else:
			keluar = 0
		masuk = row.qty

		if frappe.utils.flt(keluar) >= frappe.utils.flt(masuk):
			new_doc = frappe.new_doc("Update Bundle Stock")
			# print(str(last_day))
			# 6K: Venda 1240
			# 8K: Yeni 1147
			# 16K: Nirma 1194
			# 17K, 19K, 20K, 10K 8K putih): Ika 1225
			# PCB, 17K Putih): Mujiati 1656
			if row.kadar == "06K":
				new_doc.pic = "HR-EMP-00489"
				new_doc.id_employee = 1240
			if row.kadar == "08K":
				new_doc.pic = "HR-EMP-00485"
				new_doc.id_employee = 1147
			if row.kadar == "16K":
				new_doc.pic = "HR-EMP-00486"
				new_doc.id_employee = 1194
			if row.kadar == "17K" or row.kadar == "19K" or row.kadar == "20K" or row.kadar == "10K" or row.kadar == "08KP":
				new_doc.pic = "HR-EMP-00487"
				new_doc.id_employee = 1225
			if row.kadar == "PCB" or row.kadar == "17KP":
				new_doc.pic = "HR-EMP-00490"
				new_doc.id_employee = 1656

			new_doc.date = getdate(last_day)
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

			maksimal_total = frappe.utils.flt(keluar) - frappe.utils.flt(masuk)

			# get_per_kadar_bundle
			get_transfer_stock = frappe.db.sql(""" 
				SELECT ubss.item, ubss.bruto, ubs.`bundle`, ubs.`sales`, ubss.kadar, ubss.item
				FROM 
				 `tabUpdate Bundle Stock` ubs 
				JOIN `tabUpdate Bundle Stock Sub` ubss ON ubss.parent = ubs.name 

				WHERE ubs.`bundle` = "{}"
				AND ubss.kadar = "{}"
				AND ubss.bruto IS NOT NULL
				GROUP BY ubss.item
			""".format(row.bundle, row.kadar),as_dict=1,debug=1)

			item_pengembalian = []

			for row_sub_category in get_transfer_stock:
				item_pengembalian.append([row_sub_category.item, row_sub_category.bruto])

			retur_result = generate_list_retur(item_pengembalian, maksimal_total)
			# print(retur_result)

			for result_row in retur_result:
				new_doc.append("per_sub_category",{
					"item": result_row[0] ,
					"item_name": frappe.db.get_value("Item",result_row[0],"item_name"),
					"bruto": frappe.utils.flt(result_row[1]),
					"kadar": row.kadar
				})

			# new_doc.save()
			# frappe.db.commit()
			# create_gdle(new_doc)
	
	frappe.db.commit()
	frappe.msgprint("Generate Done")

@frappe.whitelist()
def randomizer_debug():
	warehouse = "Pembayaran Penjualan - LMS"
	item_group = "Logam"
	kadar = "06K"

	list_item = frappe.db.sql(""" 
		SELECT tb.item_code,tb.actual_qty FROM `tabBin` tb
		JOIN `tabItem` ti ON ti.name = tb.item_code
		WHERE tb.actual_qty > 0
		
		AND ti.barang_yang_dibawa_sales = "{}"
		AND ti.kadar = "{}"
	""".format(1, kadar),debug=1)

	
	total_item = 0
	kebutuhan = 10
	for row in list_item:
		total_item = total_item+frappe.utils.flt(row[1])

	kebutuhan_min = kebutuhan * 1.05
	kebutuhan_max = min(kebutuhan * 1.10, total_item)

	if total_item < kebutuhan:
		frappe.throw("Item dengan kadar {} tidak cukup barang di gudang Stockist. {}".format(kadar, total_item))

	if frappe.utils.flt(kebutuhan_min) == frappe.utils.flt(total_item):
		for row in list_item:
			result.append([row[0],row[1]])
	else:
		result = generate_list(list_item, kebutuhan_min, kebutuhan_max)

	# print(result)


@frappe.whitelist()
def randomizer(input_warehouse,input_kadar,kebutuhan, type, kadar, bundle, tanggal):
	warehouse = input_warehouse
	item_group = "Pembayaran"
	kadar = input_kadar

	list_item = frappe.db.sql(""" 
		SELECT tb.item_code,tb.actual_qty FROM `tabBin` tb
		JOIN `tabItem` ti ON ti.name = tb.item_code
		WHERE tb.actual_qty > 0
		AND tb.warehouse = "{}"
		AND ti.barang_yang_dibawa_sales = "{}"
		AND ti.item_group = "{}"
		AND ti.kadar = "{}"
	""".format(warehouse,1,item_group,kadar))
	print("-- Get List Item "+str(len(list_item))+" --")
	
	total_item = 0
	for row in list_item:
		total_item = total_item+frappe.utils.flt(row[1])

	kebutuhan_min = kebutuhan * 1.10
	kebutuhan_max = min(kebutuhan * 1.20, total_item)

	if total_item < kebutuhan:
		frappe.throw("Item dengan kadar {} tidak cukup barang di gudang Stockist.".format(kadar))

	if frappe.utils.flt(kebutuhan_min) == frappe.utils.flt(total_item):
		for row in list_item:
			result.append([row[0],row[1]])
	else:
		result = generate_list(list_item, kebutuhan_min, kebutuhan_max, type, kadar, bundle, tanggal)

	return result

def generate_list(list_item, kebutuhan_min, kebutuhan_max, type, kadar, bundle, tanggal):
    if not list_item:
        raise ValueError("List item tidak boleh kosong")
    
    temp_list = list(list_item)
    result_list = []
    # log_data = []
    counter = 0

    while True:
        counter += 1
        random.shuffle(temp_list)
        result_list = []
        kebutuhan = 0
        for item in temp_list:
            item_code, actual_qty = item
            if actual_qty <= 0:
                continue  # Skip item dengan qty <= 0
            qty_random = round(random.uniform(0, min(actual_qty, kebutuhan_min)), 2)
            result_list.append([item_code, qty_random])
            kebutuhan += qty_random

            if kebutuhan >= kebutuhan_min:
                if kebutuhan <= kebutuhan_max:
                    # save_to_excel(log_data, 'log_data.xlsx')
                    print(f"Looping selesai setelah {counter} kali iterasi.")
                    return result_list
                break  # Keluar dari loop jika kebutuhan melebihi kebutuhan_max

        if counter > 1000:  # Batas maksimal iterasi untuk menghindari infinite loop
            raise Exception("Terlalu banyak iterasi, periksa parameter input")
        
        # save_to_excel(log_data, 'log_data.xlsx')


def generate_list_retur(list_item, maksimal_total):
	if not list_item:
		raise ValueError("List item tidak boleh kosong")

	temp_list = list(list_item)
	result_list = []
	# log_data = []
	counter = 0

	while True:
		counter += 1
		random.shuffle(temp_list)
		result_list = []
		kebutuhan = 0
		for item in temp_list:
			item_code, actual_qty = item

			selisih = frappe.utils.flt(maksimal_total) - frappe.utils.flt(kebutuhan)

			if selisih < 5 and selisih > 0:
				qty_random = frappe.utils.flt(selisih,2)
				result_list.append([item_code, qty_random])
				return result_list

			elif selisih == 0:
				return result_list
			else:
				qty_random = round(random.uniform(0, actual_qty), 2)
				result_list.append([item_code, qty_random])
				kebutuhan += qty_random

		if counter > 1000:  # Batas maksimal iterasi untuk menghindari infinite loop
			raise Exception("Terlalu banyak iterasi, periksa parameter input")
	    
        # save_to_excel(log_data, 'log_data.xlsx')
