import frappe
import random

@frappe.whitelist()
def debug_make_mr():
	make_material_request("Nit65", 12, 2023)

@frappe.whitelist()
def make_material_request(item, month, year):
	get_list = frappe.db.sql(""" 
		SELECT 
		"1-20", SUM(IF(DAY(tpr.posting_date) >= 1 AND DAY(tpr.posting_date)<= 20, tpri.qty, 0)),
		"21-31", SUM(IF(DAY(tpr.posting_date) >= 21 AND DAY(tpr.posting_date)<= 31, tpri.qty, 0))

		FROM `tabPurchase Receipt Item` tpri 
		JOIN `tabPurchase Receipt` tpr ON tpr.name = tpri.parent 
		WHERE tpri.docstatus = 1
		AND tpri.item_code = "{}" AND month(tpr.posting_date) = {}
		AND YEAR(tpr.posting_date) = {}

		""".format(item,month,year))
	# ambil list
	# ambil randoman pemakaian item pembantu
	# make MR sebanyak randoman

	get_patokan = frappe.db.sql(""" 
		SELECT name FROM `tabPemakaian Bahan Pembantu` ORDER BY RAND() LIMIT 1
	""")

	print(get_list)
	print(get_patokan)
	if get_patokan:
		pemakaian = frappe.get_doc("Pemakaian Bahan Pembantu", get_patokan[0][0])

		if get_list[0][1] > 0:
			qty_satu = frappe.utils.flt(get_list[0][1])
			# buat MR 1-20
			for row in pemakaian.item:
				qty = qty_satu * row.persen / 100
				gen_mr(qty, row.department, item)

		if get_list[0][3] > 0:
			qty_dua = frappe.utils.flt(get_list[0][3])
			# buat MR 21-30
			for row in pemakaian.item:
				qty = qty_dua * row.persen / 100
				gen_mr(qty, row.department, item)
				

@frappe.whitelist()
def gen_mr(qty, department, item):
	k = random.randint(0, 1)

	mr = frappe.new_doc("Material Request")
	mr.department = department
	mr.schedule_date = mr.transaction_date

	if k == 0:
		mr.material_request_type = "Material Transfer"
	else:
		mr.material_request_type = "Material Issue"	

	print(mr.transaction_date)
	print(mr.material_request_type)

	mr.append("items",{
		"item_code" : item,
		"qty": qty,
		"schedule_date": mr.schedule_date
	})

	mr.save()
	frappe.db.commit()

@frappe.whitelist()
def masukin_pbp():
	# import pandas lib as pd
	import pandas as pd
	
	# read by default 1st sheet of an excel file
	df = pd.read_excel('/home/frappe/frappe-bench/apps/lestari/lestari/PBP.xlsx',engine='openpyxl')
	
	print(df.columns.tolist())
	counter = 0

	for index, row in df.iterrows():
		try:
			frappe.get_doc("Pemakaian Bahan Pembantu", row[0])
		except:
			pbp_baru = frappe.new_doc("Pemakaian Bahan Pembantu")
			pbp_baru.nama = row[0]
			print(pbp_baru.nama)
			for nama in df.columns.tolist():
				if row[0] != row[nama] and row[nama] and nama != "KETERANGAN":
					pbp_baru.append("item",{
						"department": nama,
						"persen": frappe.utils.flt(row[nama])
					})
					print("{}-{}-{}".format(row[0],nama,row[nama]))
			pbp_baru.save()
			frappe.db.commit()
