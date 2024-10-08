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
	data_holiday = frappe.db.sql(""" SELECT holiday_date FROM `tabHoliday` """)
	print_calendar("2024-01-01","2024-01-18",data_holiday)

@frappe.whitelist()
def print_calendar(str_start_date,str_end_date, data_holiday, senin):
	final_date = ""
	try:
		check_holiday = data_holiday.index(str(senin))

		# PERLU PIP INSTALL FAKER
		fake = Faker()

		start_date = datetime.strptime(str(str_start_date), '%Y-%m-%d')
		end_date = datetime.strptime(str(str_end_date), '%Y-%m-%d') - timedelta(days=1)

		check = 0 

		

		while check == 0:
			if final_date == "":
				final_date = get_monday_of_date(str_end_date)
			
			try:
				check_holiday = data_holiday.index(str(final_date))
				final_date = fake.date_between(start_date=start_date, end_date=end_date)
			except:
				check = 1
				
	except:
		final_date = senin

	return str(final_date)

def debug_start_generate():
	start_generate(2023,"September","JPT230901")

@frappe.whitelist()
def start_generate(year, month, bundle=None):
	frappe.msgprint("-- Initiate Generate --")
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

	# frappe.msgprint(str(bundle))
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
		SELECT 
		gi.name,
		gi.sales_partner as sales_partner, 
		IF(MONTH(DATE_ADD(gi.posting_date, INTERVAL - WEEKDAY(gi.posting_date) DAY)) != MONTH(gi.posting_date), gi.`posting_date`,DATE_ADD(gi.posting_date, INTERVAL - WEEKDAY(gi.posting_date) DAY)) AS senin, 
		gii.kadar, 
		SUM(gii.qty) as qty, 
		gi.bundle,
		gi.posting_date

		FROM 
		`tabGold Invoice` gi
		JOIN `tabGold Invoice Item` gii ON gii.parent = gi.name
		WHERE DATE(gi.posting_date) >= DATE("{}")
		AND DATE(gi.posting_date) <= DATE("{}")
		
		{}

		AND gi.docstatus = 1

		GROUP BY gi.sales_partner, senin, gii.kadar, gi.bundle
		ORDER BY gi.sales_partner, gi.posting_date, gi.bundle, gii.kadar 
		
		""".format(str(first_day),str(last_day),addons),as_dict=1, debug=True)
	
	print("-- Get List Gold Invoice "+str(len(lis_gold_invoice))+"--")
	# frappe.throw(str(len(lis_gold_invoice)))
	print("-- Start Looping List Gold Invoice --")

	data_holiday = frappe.db.sql(""" SELECT holiday_date FROM `tabHoliday` """)

	data_penyerahan = frappe.db.sql(""" SELECT 
		ubs.name, ubs.`sales`,dps.`kadar`,ubs.`bundle`
		FROM `tabUpdate Bundle Stock` ubs JOIN
		`tabDetail Penambahan Stock` dps ON dps.parent = ubs.name
		WHERE ubs.type = "New Stock"
		AND DATE(ubs.date) >= DATE("{}")
		AND DATE(ubs.date) <= DATE("{}")
	""".format(str(first_day), str(last_day)),debug=True)

	penyerahan_array = []
	penambahan_array = []

	for row in data_penyerahan:
		penyerahan_array.append(
			"{}|{}|{}".format(row[1],row[2],row[3])
		)

	index = 0
	total_need = 0

	for row in lis_gold_invoice:
		total_need = 0

		print("-- Begin Index 0 --")
		ada_penyerahan_sebelumnya = 0

		try:
			penyerahan_array.index("{}|{}|{}".format(row.sales_partner, row.kadar, row.bundle))
			ada_penyerahan_sebelumnya = 1
		except:
			ada_penyerahan_sebelumnya = 0

		print("-- Get Penyerahan {}-{}-{}-{} --".format(row.sales_partner, row.kadar, row.bundle, ada_penyerahan_sebelumnya))
		
		new_doc = frappe.new_doc("Update Bundle Stock")
		print("-- Create New Transfer Salesman '"+str(new_doc)+"' --")

		print("-- Set Posting Date '"+str(new_doc.date)+"' --")
		new_doc.bundle = row.bundle
		print("-- Set Bundle '"+new_doc.bundle+"' --")

		if ada_penyerahan_sebelumnya == 0:
			new_doc.type = "New Stock"
			bundle_date = frappe.db.get_value("Sales Stock Bundle", row.bundle, "date", cache=1)
			bundle_date = datetime.strptime(str(bundle_date), '%Y-%m-%d')
			new_doc.date = bundle_date
		else:
			new_doc.type = "Add Stock"
			# new_doc.date = print_calendar(first_day,row.posting_date,data_holiday)
			new_doc.date = print_calendar(first_day,row.posting_date,data_holiday,row.senin)

		print("-- Set Type '"+new_doc.type+"' --")
		new_doc.s_warehouse = "Stockist - LMS"
		new_doc.purpose = "Sales"
		new_doc.sales = row.sales_partner
		new_doc.warehouse = frappe.db.get_value("Sales Partner",new_doc.sales,"warehouse", cache=1)
		
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
		item = frappe.get_cached_doc("Item", {"kadar":row.kadar, "item_group":"Perhiasan","item_group_parent":"Pembayaran"})
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
				"item_name": frappe.db.get_value("Item", baris_result[0], "item_name", cache=1),
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

		if ada_penyerahan_sebelumnya == 0:
			penyerahan_array.append(
				"{}|{}|{}".format(new_doc.sales,row.kadar,new_doc.bundle)
			)

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
		SELECT gi.name, gi.sales_partner AS sales_partner, gi.posting_date, gii.kadar, SUM(gii.qty) AS qty, gi.bundle FROM 
		`tabGold Invoice` gi
		JOIN `tabGold Invoice Item` gii ON gii.parent = gi.name

		WHERE DATE(gi.posting_date) >= DATE("{}")
		AND DATE(gi.posting_date) <= DATE("{}")

		AND gi.docstatus = 1

		{}

		GROUP BY gi.sales_partner, gii.kadar, gi.bundle
		ORDER BY gi.sales_partner, gi.posting_date 
	; """.format(str(first_day),str(last_day),addons),as_dict=1,debug=1)

	# get_transfer_salesman = frappe.db.sql(""" 
	# 	SELECT ubs.`bundle`, ubs.`sales`, ubss.kadar, SUM(ubss.bruto)
	# 	FROM 
	# 	 `tabUpdate Bundle Stock` ubs 
	# 	JOIN `tabUpdate Bundle Stock Sub` ubss ON ubss.parent = ubs.name 

	# 	WHERE ubs.`bundle` = "{}"
	# 	AND ubs.`sales` = "{}"
	# 	AND ubss.kadar = "{}"
	# 	AND ubss.bruto IS NOT NULL
	# 	GROUP BY ubs.bundle, ubss.kadar, ubs.`sales`;

	# """.format(row.bundle, row.sales_partner, row.kadar))

	data_pengembalian = frappe.db.sql(""" 
		SELECT ubs.`bundle`, ubs.`sales`, ubss.kadar, SUM(ubss.bruto)
		FROM 
		 `tabUpdate Bundle Stock` ubs 
		JOIN `tabUpdate Bundle Stock Sub` ubss ON ubss.parent = ubs.name 

		WHERE 
		DATE(ubs.date) >= DATE("{}")
		AND DATE(ubs.date) <= DATE("{}")
		AND ubss.bruto IS NOT NULL
		GROUP BY ubs.bundle, ubss.kadar, ubs.`sales`;

	""".format(str(first_day),str(last_day)))

	# get_transfer_stock = frappe.db.sql(""" 
	# 	SELECT ubss.item, ubss.bruto, ubs.`bundle`, ubs.`sales`, ubss.kadar, ubss.item
	# 	FROM 
	# 	 `tabUpdate Bundle Stock` ubs 
	# 	JOIN `tabUpdate Bundle Stock Sub` ubss ON ubss.parent = ubs.name 

	# 	WHERE ubs.`bundle` = "{}"
	# 	AND ubss.kadar = "{}"
	# 	AND ubss.bruto IS NOT NULL
	# 	GROUP BY ubss.item
	# """.format(row.bundle, row.kadar), as_dict=1, debug=1)

	data_transfer_stock = frappe.db.sql(""" 
		SELECT ubss.item, sum(ubss.bruto) as bruto, ubs.`bundle`, ubs.`sales`, ubss.kadar, ubss.item
		FROM 
		 `tabUpdate Bundle Stock` ubs 
		JOIN `tabUpdate Bundle Stock Sub` ubss ON ubss.parent = ubs.name 

		WHERE 
		DATE(ubs.date) >= DATE("{}")
		AND DATE(ubs.date) <= DATE("{}")
		AND ubss.bruto IS NOT NULL
		GROUP BY ubss.item, ubs.bundle, ubs.kadar
	""".format(str(first_day),str(last_day)), as_dict=1, debug=1)

	pengembalian_dict = {}
	for row in data_pengembalian:
		pengembalian_dict.setdefault((row[0],row[1],row[2]), 0)
		pengembalian_dict[(row[0],row[1],row[2])] += row[3]

	# print("masuk list_pengembalian")
	print("Banyak Pengembalian "+str(len(list_pengembalian)))
	for row in list_pengembalian:

		keluar = pengembalian_dict.get((row.bundle, row.sales_partner, row.kadar), 0)
		
		masuk = row.qty

		if frappe.utils.flt(keluar) >= frappe.utils.flt(masuk):
			new_doc = frappe.new_doc("Update Bundle Stock")
			
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
			new_doc.warehouse = frappe.db.get_value("Sales Partner",new_doc.sales, "warehouse", cache=1)

			item = frappe.get_cached_doc("Item", { "kadar":row.kadar, "item_group": "Perhiasan","item_group_parent": "Pembayaran" })

			new_doc.append("items", {
				"sub_category" : "Perhiasan",
				"kadar" : row.kadar,
				"qty_penambahan" : frappe.utils.flt(keluar) - frappe.utils.flt(masuk),
				"item": item.name ,
				"gold_selling_item": item.gold_selling_item
			})

			new_doc.append("per_kadar", {
				"kadar" : row.kadar,
				"bruto" : frappe.utils.flt(keluar) - frappe.utils.flt(masuk),
			})

			maksimal_total = frappe.utils.flt(keluar) - frappe.utils.flt(masuk)

			# get_per_kadar_bundle
		
			item_pengembalian = []

			for row_sub_category in data_transfer_stock:
				if row.kadar == row_sub_category.kadar and new_doc.bundle == row_sub_category.bundle:
					item_pengembalian.append({row_sub_category.item:row_sub_category.bruto})
			print("=====GENERATE RETUR======")

			# untuk margin 0.001-0.001
			print("=====NAMBAH JUMLAH======")
			maksimal_total = maksimal_total + round(random.uniform(0.001, 0.01), 2)
			retur_result = generate_list_retur(item_pengembalian, maksimal_total)
			

			item_index = [list(per_item.keys())[0] for per_item in retur_result]
			qty_index = [list(per_item.values())[0] for per_item in retur_result]
	
			for per_index in range(len(item_index)):
				new_doc.append("per_sub_category",{
					"item": item_index[per_index] ,
					"item_name": frappe.db.get_value("Item",item_index[per_index],"item_name"),
					"bruto": frappe.utils.flt(qty_index[per_index]),
					"kadar": row.kadar
				})

			new_doc.save()
			# frappe.db.commit()
			# create_gdle(new_doc)
	
	frappe.db.commit()


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

	list_item_temp = frappe.db.sql(""" 
		SELECT tb.item_code,tb.qty_after_transaction FROM `tabStock Ledger Entry` tb
		JOIN `tabItem` ti ON ti.name = tb.item_code
		WHERE tb.qty_after_transaction > 0
		AND tb.warehouse = "{}"
		AND ti.barang_yang_dibawa_sales = "{}"
		AND ti.item_group = "{}"
		AND ti.kadar = "{}"
		AND tb.posting_date < "{}"
		
        ORDER BY TIMESTAMP(tb.posting_date,tb.posting_time) DESC
	""".format(warehouse,1,item_group,kadar,tanggal),debug=1)
	print("-- Get List Item "+str(len(list_item_temp))+" --")
	list_item=[]
	item_added=[]
	for row in list_item_temp:
		if row[1] not in item_added:
			list_item.append(row)
			item_added.append(row[1])
	total_item = 0
	for row in list_item:
		total_item = total_item+frappe.utils.flt(row[1])

	kebutuhan_min = kebutuhan * 1.10
	kebutuhan_max = min(kebutuhan * 1.20, total_item)

	if total_item < kebutuhan:
		frappe.msgprint("Kebutuhan Kebutuhan = {}".format(kebutuhan))
		frappe.msgprint("Kebutuhan Min = {}".format(kebutuhan_min))
		frappe.msgprint("Kebutuhan Max = {}".format(kebutuhan_max))
		frappe.msgprint("Total Item = {}".format(total_item))
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


# def old_generate_list_retur(list_item, maksimal_total):
# 	if not list_item:
# 		raise ValueError("List item tidak boleh kosong")

# 	temp_list = list(list_item)
# 	result_list = []
# 	# log_data = []
# 	counter = 0

# 	while True:
# 		counter += 1
# 		random.shuffle(temp_list)
# 		result_list = []
# 		kebutuhan = 0
# 		for item in temp_list:
# 			item_code, actual_qty = item

# 			selisih = frappe.utils.flt(maksimal_total) - frappe.utils.flt(kebutuhan)

# 			if selisih < 5 and selisih > 0:
# 				qty_random = frappe.utils.flt(selisih,2) + round(random.uniform(0.001, 0.01), 2)
# 				result_list.append([item_code, qty_random])
# 				return result_list

# 			elif selisih == 0 or (selisih > 0.001 and selisih < 0.01) :
# 				return result_list

# 			elif selisih < 0:
# 				kebutuhan -= qty_random
# 				qty_random = round(random.uniform(0, actual_qty), 2)
# 				result_list.append([item_code, qty_random])
# 				kebutuhan += qty_random
# 			else:
# 				qty_random = round(random.uniform(0, actual_qty), 2)
# 				result_list.append([item_code, qty_random])
# 				kebutuhan += qty_random

		# if counter > 100:  # Batas maksimal iterasi untuk menghindari infinite loop
		# 	raise Exception("Terlalu banyak iterasi, periksa parameter input")
	    
        # save_to_excel(log_data, 'log_data.xlsx')

def generate_list_retur(list_item, maksimal_total):
	random.shuffle(list_item)
	
	item_index = [list(per_item.keys())[0] for per_item in list_item]
	qty_index = [list(per_item.values())[0] for per_item in list_item]
	
	current_sum = 0
	remaining_sum = maksimal_total

	result = []

	for index in range(len(item_index)):
		if remaining_sum > 0:
			if index == len(item_index) - 1:
				if qty_index[index] != remaining_sum:
					value = min(qty_index[index], remaining_sum)
				else:
					value = qty_index[index]

				if value > 0:
					value = round(value,2)
					result.append({item_index[index]: value})
					remaining_sum -= value
			else:
				# For other elements, ensure the sum with the last element does not exceed the max value
				max_possible = min(qty_index[index], remaining_sum)
				value = round(random.uniform(0, max_possible), 2)
				if value > 0:
					result.append({item_index[index]: value})
					remaining_sum -= value
	return result


@frappe.whitelist()
def start_generate_multi(first_day, last_day, bundle=None):
	from frappe.utils import flt

	def _emp():	
		emp = {}	
		if row.kadar == "06K":
			emp["pic"] = "HR-EMP-00489"
			emp["id_employee"] = 1240
		elif row.kadar == "08K":
			emp["pic"] = "HR-EMP-00485"
			emp["id_employee"] = 1147
		elif row.kadar == "16K":
			emp["pic"] = "HR-EMP-00486"
			emp["id_employee"] = 1194
		elif row.kadar in ["17K", "19K", "20K", "10K", "08KP"]:
			emp["pic"] = "HR-EMP-00487"
			emp["id_employee"] = 1225
		elif row.kadar in ["PCB", "17KP"]:
			emp["pic"] = "HR-EMP-00490"
			emp["id_employee"] = 1656

		return emp
	
	frappe.msgprint("-- Initiate Generate --")
	addons = ""
	if bundle:
		addons = " AND gi.bundle = '%s' " % bundle

	list_ginv = frappe.db.sql("""
		SELECT 
			gi.name, gi.sales_partner, gi.posting_date, gii.kadar, gii.qty, gi.bundle 
		FROM `tabGold Invoice` gi
		JOIN `tabGold Invoice Item` gii ON gii.parent = gi.name
		WHERE posting_date between %s and %s
		{}
		AND gi.docstatus = 1
		
		ORDER BY gi.posting_date
	""".format(addons), [first_day, last_day])
	
	gold_invoice_sup, list_kadar = {}, set()

	# def _set_list_gold_inv(name, sales_partner, posting_date, kadar, qty, bundle):
	# 	return {"name": name, "sales_partner": sales_partner, "posting_date": posting_date, "kadar": kadar, "qty": qty, "bundle": bundle}

	for row in list_ginv:
		# res = _set_list_gold_inv(*row)
		g_inv = gold_invoice_sup.setdefault((row[1], row[3], row[5]), {"total": []})
		g_inv[row[2]].append(row[4])
		g_inv["total"].append(row[4])

		list_kadar.add(key[3])
		# gold_invoice_sup.setdefault((row[1], row[2], row[3], row[5]), []).append(row[4])

	key = list(gold_invoice_sup.keys())

	query = """ SELECT 
		SELECT DISTINCT
			ubs.sales,
			dps.kadar,
			ubs.bundle
		FROM `tabUpdate Bundle Stock` ubs
		JOIN `tabDetail Penambahan Stock` dps ON dps.parent = ubs.name
		WHERE ubs.type = 'New Stock'
		AND (ubs.sales, dps.kadar, ubs.bundle) IN ({})
	""".format(','.join(['(%s, %s, %s)'] * len(key)))
	
	# Flatten the keys for the query parameters
	query_params = [item for sublist in key for item in sublist]

	# Execute the query once
	data_penyerahan = frappe.db.sql(query, query_params)
	penyerahan_sup = {(row[0], row[1], row[2]) for row in data_penyerahan}

	perhiasan_list = frappe.db.sql(""" SELECT 
		SELECT name, gold_selling_item, kadar
		FROM `tabItem` 
		WHERE item_group = "Perhiasan" and item_group_parent = "Pembayaran" and disabled != 1
		AND kadar IN ({})
		GROUP BY kadar
	""", list(list_kadar))

	item_perhiasan = {}
	for row in perhiasan_list:
		item_perhiasan.setdefault(row[2], {"name": row[0], "gold_selling_item": row[1]})

	data_holiday = frappe.db.sql(""" SELECT holiday_date FROM `tabHoliday` """)
	# key 0 = sales, key 1 = kadar, key 2 = bundle
	for key_sup, posting_date in gold_invoice_sup.items():
		sales, kadar, i_bundle = key
		for pd, qty in posting_date.items():
			new_doc = frappe.new_doc("Update Bundle Stock")
			new_doc.bundle = i_bundle

			if (sales, kadar, i_bundle) in penyerahan_sup:
				new_doc.type = "Add Stock"
				new_doc.date = print_calendar(first_day, key_sup[1], data_holiday)
			else:
				new_doc.type = "New Stock"
				new_doc.date = frappe.db.get_value("Sales Stock Bundle", i_bundle, "date", cache=1)
				penyerahan_sup.add((sales, kadar, i_bundle))

			new_doc.s_warehouse = "Stockist - LMS"
			new_doc.purpose = "Sales"
			new_doc.sales = row.sales_partner
			new_doc.warehouse = frappe.db.get_value("Sales Partner", new_doc.sales, "warehouse", cache=1)

			if emp := _emp(kadar):
				new_doc.update(emp)

			# for new_doc_row in new_doc.items:
			# result = randomizer(new_doc.s_warehouse, row.kadar, flt(sum([qty]), 2), new_doc.type, row.kadar, row.bundle, new_doc.date)

	# Prepare the SQL query for all keys
	query = """
		SELECT 
			ubs.bundle, ubs.sales, ubss.kadar, SUM(ubss.bruto) AS total_bruto
		FROM `tabUpdate Bundle Stock` ubs 
		JOIN `tabUpdate Bundle Stock Sub` ubss 
		ON ubss.parent = ubs.name 
		WHERE ubs.sales, ubss.kadar, ubs.bundle IN ({})
			AND ubss.bruto IS NOT NULL
		GROUP BY ubs.bundle, ubss.kadar, ubs.sales
	""".format(','.join(['(%s, %s, %s)'] * len(key)))

	# Flatten the keys for the query parameters
	query_params = [item for sublist in key for item in sublist]

	# Execute the query once
	data_transfer_salesman = frappe.db.sql(query, query_params)

	# Convert the result to a dictionary for easy lookup
	transfer_salesman_dict = {(row[1], row[2], row[0]): row[3] for row in data_transfer_salesman}
	
	# key 0 = sales, key 1 = kadar, key 2 = bundle
	for key_peng, qty in gold_invoice_sup.items():
		sales, kadar, i_bundle = key

		masuk = flt(sum(qty), 2)
		total_bruto = transfer_salesman_dict.get(key_peng, 0)
		
		if flt(total_bruto, 2) >= masuk:
			new_doc = frappe.new_doc("Update Bundle Stock")

			if emp := _emp(kadar):
				new_doc.update(emp)

			new_doc.date = getdate(last_day)
			new_doc.bundle = i_bundle
			new_doc.type = "Deduct Stock"

			new_doc.s_warehouse = "Stockist - LMS"
			new_doc.purpose = "Sales"
			new_doc.sales = sales
			new_doc.warehouse = frappe.db.get_value("Sales Partner", sales, "warehouse", cache=1)

			item = item_perhiasan.get(kadar)
			if not item:
				raise ValueError("List item tidak boleh kosong")
			
			maksimal_total = flt(keluar - masuk, 2)
			new_doc.append("items", {
				"sub_category" : "Perhiasan",
				"kadar" : kadar,
				"qty_penambahan" : maksimal_total,
				"item": item["name"],
				"gold_selling_item": item["gold_selling_item"]
			})

			new_doc.append("per_kadar", {
				"kadar" : kadar,
				"bruto" : maksimal_total,
			})
