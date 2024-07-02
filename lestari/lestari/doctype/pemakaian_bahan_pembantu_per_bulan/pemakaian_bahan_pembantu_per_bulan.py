# Copyright (c) 2024, DAS and contributors
# For license information, please see license.txt

import frappe
import random
import calendar
from datetime import datetime, timedelta

from frappe.model.document import Document

class PemakaianBahanPembantuPerBulan(Document):
	pass

@frappe.whitelist()
def debug_generate_mr():
	generate_mr("Bor41415",12,2023)

@frappe.whitelist()	
def generate_mr(item_code,bulan,tahun):

	item_name = frappe.db.get_value('Pemakaian Bahan Pembantu', {'item_code': item_code}, ['name'])
	pbp = frappe.get_doc('Pemakaian Bahan Pembantu', item_name)
	pemakaian = frappe.db.get_value('Pemakaian Bahan Pembantu Per Bulan', {
		'pemakaian_bahan_pembantu': item_name,
		'bulan':bulan,
		'tahun':tahun,
		}, ['pemakaian'])
	
	jenis_dokumen = "Stock"

	for department in pbp.item:
		pakai = department.persen * pemakaian / 100
		pemakaian_mr = pecah_pemakaian(pakai, item_code)
		for qty in pemakaian_mr:
			tanggal = str(rand_tgl(bulan,tahun))
			material_request_type = "Material Issue"
			draf_mr = frappe.db.get_list('Material Request',
								filters={'docstatus':0,'hasil_generate':1,'schedule_date':tanggal,'department':department.department},
								fields=['name'],pluck='name')
			
			if len(draf_mr) == 0:			
				print("make mr untuk department "+department.department+" qty "+str(qty)+" tanggal "+tanggal)
				new_mr = frappe.get_doc({
						'doctype': 'Material Request',
						'material_request_type': material_request_type,
						'jenis_dokumen': jenis_dokumen,
						'transaction_date': tanggal,
						'schedule_date': tanggal,
						'department': department.department,
						'hasil_generate': 1,
						'items': [
							{
								'item_code': item_code,
								'schedule_date': tanggal,
								'qty': qty,
								'warehouse': "inventory General - LMS"
							}
						]
					})
				new_mr.save()
			else:
				print("update draft mr department "+department.department+" qty "+str(qty)+" tanggal "+tanggal)
				description = frappe.db.get_value('Item', {'item_code': item_code}, ['description'])
				stock_uom = frappe.db.get_value('Item', {'item_code': item_code}, ['stock_uom'])
				uom = frappe.db.get_list('UOM Conversion Detail',filters={'parent':item_code},fields=['uom','conversion_factor'])
				add_mr = frappe.get_doc({
					'doctype': 'Material Request Item',
					'parent': draf_mr[0],
					'parentfield': 'items',
					'parenttype': 'Material Request',
					'item_code': item_code,
					'schedule_date': tanggal,
					'qty': qty,
					'warehouse': "inventory General - LMS",
					'description': description,
					'stock_uom': stock_uom,
					'uom': uom[0]['uom'],
					'conversion_factor': uom[0]['conversion_factor']
				})
				add_mr.insert(ignore_permissions=True)

			
	frappe.db.commit()

def pecah_pemakaian(pemakaian, item_code):
	data = []
	
	jumlah_mr = random.randint(1, 5)
	persen = 100 
	import math
	for i in range(0,jumlah_mr-1):
		if persen > 1:
			sub_persen = random.randint(1, persen)
			if frappe.get_doc("Item",item_code).stock_uom == "Pcs":
				qty = math.ceil(sub_persen*pemakaian/100)
				print(qty)
				if qty != 0:
					data.append(qty)
			else:
				data.append(sub_persen*pemakaian/100)
			
	if persen != 0:
		if frappe.get_doc("Item",item_code).stock_uom == "Pcs":
			qty = math.ceil(persen*pemakaian/100)
			print(qty)
			if qty != 0:
				data.append(qty)
		else:
			data.append(persen*pemakaian/100)
	
	return data

def rand_tgl(bulan,tahun):
	holiday = frappe.db.get_list('Holiday',filters={'parent': tahun},fields=['holiday_date'],pluck='holiday_date')
	
	start_date = datetime(tahun,bulan,1)
	last_day = calendar.monthrange(tahun, bulan)[1]
	end_date = datetime(tahun, bulan, last_day)
	
	random_days = random.randint(0,(end_date - start_date).days)
	random_date = start_date + timedelta(days=random_days)
	hasil = datetime.strptime(str(random_date.date()), "%Y-%m-%d").date()
	
	while hasil in holiday:
		print(str(hasil)+" hari libur, generate baru ") 
		random_days = random.randint(0,(end_date - start_date).days)
		random_date = start_date + timedelta(days=random_days)
		hasil = datetime.strptime(str(random_date.date()), "%Y-%m-%d").date()
	
	return hasil
