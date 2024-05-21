# Copyright (c) 2024, DAS and contributors
# For license information, please see license.txt

import frappe
import random
import calendar
from datetime import datetime, timedelta

from frappe.model.document import Document

class PemakaianBahanPembantuPerBulan(Document):

	def make_mr(self):
		item_code = frappe.db.get_value('Pemakaian Bahan Pembantu', {'nama': self.pemakaian_bahan_pembantu}, ['item_code'])
		generate_mr(item_code,self.bulan,self.tahun)

@frappe.whitelist()
def debug_generate_mr():
	generate_mr("WashBen",12,2023)

@frappe.whitelist()	
def generate_mr(item_code,bulan,tahun):

	item_name = frappe.db.get_value('Pemakaian Bahan Pembantu', {'item_code': item_code}, ['name'])
	pbp = frappe.get_doc('Pemakaian Bahan Pembantu', item_name)
	pemakaian = frappe.db.get_value('Pemakaian Bahan Pembantu Per Bulan', {
		'pemakaian_bahan_pembantu': item_name,
		'bulan':bulan,
		'tahun':tahun,
		}, ['pemakaian'])
	
	jenis_dokumen = "Non Stock"

	for department in pbp.item:
		pakai = department.persen * pemakaian / 100
		pemakaian_mr = pecah_pemakaian(pakai)
		for qty in pemakaian_mr:
			tanggal = str(rand_tgl(bulan,tahun))
			k = random.randint(0,1)
			if k == 0:
				material_request_type = "Material Transfer"
			else:
				material_request_type = "Material Issue"
			print("make mr untuk department "+department.department+" qty "+str(qty)+" tanggal "+tanggal)
			new_mr = frappe.get_doc({
					'doctype': 'Material Request',
					'material_request_type': material_request_type,
					'jenis_dokumen': jenis_dokumen,
					'transaction_date': tanggal,
					'schedule_date': tanggal,
					'department': department.department,
					'items': [
						{
							'item_code': item_code,
							'schedule_date': tanggal,
							'qty': pemakaian,
						}
					]
				})
			new_mr.save()

	frappe.db.commit()

def pecah_pemakaian(pemakaian):
	data = []
		
	jumlah_mr = random.randint(1, 5)
	persen = 100 
	for i in range(0,jumlah_mr-1):
		if persen > 1:
			sub_persen = random.randint(1, persen)
			data.append(sub_persen*pemakaian/100)
			persen = persen - sub_persen
			
	if persen != 0:
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
