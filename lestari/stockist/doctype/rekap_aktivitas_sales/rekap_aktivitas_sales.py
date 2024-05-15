# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
import datetime
from frappe.model.document import Document
from frappe.utils import flt,getdate
from lestari.randomize import first_day_of_month,last_day_of_month, start_generate
from lestari.gold_selling.doctype.gold_invoice.gold_invoice import submit_gold_ledger

class RekapAktivitasSales(Document):
	@frappe.whitelist()
	def get_details(self):
		list_rekap = frappe.db.sql(
			"""
				SELECT
					*
					FROM
					`tabGold Ledger Entry`
					WHERE bundle = '{}'
					ORDER BY
					CASE
						WHEN proses = 'New Stock'
						THEN 1
						WHEN proses = 'Add Stock'
						THEN 2
						WHEN proses = 'Penyetoran'
						THEN 3
						WHEN proses = 'Penjualan'
						THEN 4
						END,
					posting_date ASC
		""".format(self.bundle,self.sales),as_dict = 1)
		# frappe.throw(str(list_rekap))
		# self.append("detail",
		# 		{
		# 				"id": "test",
		# 				"tgl_rekap": "2023-02-12",
		# 				"aktivitas": "Penambahan",
		# 				"6k": 0,
		# 				"8k": 0,
		# 				"8kp": 0,
		# 				"16k": 0,
		# 				"17k": 0,
		# 				"17kp": 0,
		# 				"total": 0
		# 		})
		detail = {}
		new_stock_name = []
		# frappe.msgprint(str(len(list_rekap)))
		# frappe.msgprint(str(list_rekap))
		total_dibawa = 0
		if len(list_rekap) > 0:
			for row in list_rekap:
				if row.proses == "Penyerahan":
					detail.setdefault(row.name,{
						"id": row.name,
						"tgl_rekap": row.posting_date,
						"aktivitas": row.proses,
						"6k": 0,
						"8k": 0,
						"8kp": 0,
						"16k": 0,
						"17k": 0,
						"17kp": 0,
						"total": row.qty_in
					})
				elif row.proses not in ["Penyetoran","Penjualan"]:
					detail.setdefault(row.name,{
						"id": row.name,
						"tgl_rekap": row.posting_date,
						"aktivitas": row.proses,
						"6k": 0,
						"8k": 0,
						"8kp": 0,
						"16k": 0,
						"17k": 0,
						"17kp": 0,
						"total": row.qty_out
					})
				else:
					detail.setdefault(row.name,{
						"id": row.name,
						"tgl_rekap": row.posting_date,
						"aktivitas": row.proses,
						"6k": 0,
						"8k": 0,
						"8kp": 0,
						"16k": 0,
						"17k": 0,
						"17kp": 0,
						"total": row.qty_in
					})
				if row.qty_in > 0:
					bruto = row.qty_in
				if row.qty_in <= 0:
					bruto = row.qty_out
				if row.kadar == "06K":
					detail[row.name]['6k'] = bruto
				if row.kadar == "08K":
					detail[row.name]['8k'] = bruto
				if row.kadar == "08KP":
					detail[row.name]['8kp'] = bruto
				if row.kadar == "16K":
					detail[row.name]['16k'] = bruto
				if row.kadar == "17K":
					detail[row.name]['17k'] = bruto
				if row.kadar == "17KP":
					detail[row.name]['17kp'] = bruto		
				# frappe.msgprint(str(detail[row.name]))
				self.append("detail",detail[row.name])
				
				# frappe.db.commit()
			tot_6k = 0
			tot_8k = 0
			tot_8kp = 0
			tot_16k = 0
			tot_17k = 0
			tot_17kp = 0
			grand_tot = 0
			for row in detail:
				# frappe.msgprint(detail[row]['id']+'aktivitas='+detail[row]['aktivitas'])
				# frappe.msgprint(grand_tot)
				if detail[row]['aktivitas'] not in ["Penyetoran","Penjualan"] : 
						tot_6k += flt(detail[row]["6k"])
						tot_8k += flt(detail[row]["8k"])
						tot_8kp += flt(detail[row]["8kp"])
						tot_16k += flt(detail[row]["16k"])
						tot_17k += flt(detail[row]["17k"])
						tot_17kp += flt(detail[row]["17kp"])
						grand_tot = flt(grand_tot) + flt(detail[row]["total"])
				else:
					tot_6k -= flt(detail[row]["6k"])
					tot_8k -= flt(detail[row]["8k"])
					tot_8kp -= flt(detail[row]["8kp"])
					tot_16k -= flt(detail[row]["16k"])
					tot_17k -= flt(detail[row]["17k"])
					tot_17kp -= flt(detail[row]["17kp"])
					grand_tot = flt(grand_tot) - flt(detail[row]["total"])
			self.append('detail',{
				"aktivitas":"Total",
				"6k" : tot_6k,
				"8k" : tot_8k,
				"8kp" : tot_8kp,
				"16k" : tot_16k,
				"17k" : tot_17k,
				"17kp" : tot_17kp,
				#"total" : "{:03f}".format(grand_tot),
				"total" : grand_tot,
			})
			# frappe.msgprint(str(detail))
			self.total_barang_dibawa = grand_tot
			# self.save()
		else:
			frappe.throw("Data Kosong")
	
	@frappe.whitelist()
	def get_transfer_salesman(self):
		month_name = self.bulan
		year = self.tahun

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
		first_day = first_day_of_month(datetime.date(year, month_number, 1))
		print("-- Get First Day '"+str(first_day)+"' --")
		last_day = last_day_of_month(datetime.date(year, month_number, 1))
		print("-- Get Last Day '"+str(last_day)+"' --")

		list_kss = frappe.db.get_list(
			"Kartu Stock Sales",
			filters=[
				['posting_date', 'between', [first_day, last_day]
				]
			]
		)

		if len(list_kss) > 0:
			for row in list_kss:
				frappe.delete_doc('Kartu Stock Sales',row.name)
				frappe.db.commit()

		list_gle = frappe.db.get_list(
			"Gold Ledger Entry",
			filters=[
				['posting_date', 'between', [first_day, last_day]
				]
			]
		)

		if len(list_gle) > 0:
			for row in list_gle:
				frappe.delete_doc('Gold Ledger Entry',row.name)
				frappe.db.commit()

		list_ts = frappe.db.get_list(
			"Update Bundle Stock",
			filters=[
				['date', 'between', [first_day, last_day]
				]
			]
		)

		if len(list_ts) > 0:
			for row in list_ts:
				frappe.delete_doc('Update Bundle Stock',row.name)
				frappe.db.commit()

		start_generate(self.tahun, self.bulan)

		list_ginv = frappe.db.get_list(
			"Gold Invoice",
			filters=[
				['posting_date', 'between', [first_day, last_day]
				]
			]
		)

		for row in list_ginv:
			submit_gold_ledger(row.name)

		frappe.msgprint("Generate Done")

	@frappe.whitelist()
	def get_transfer_salesman_bundle(self):
		list_kss = frappe.db.get_list("Kartu Stock Sales", filters={"bundle":self.bundle})
		for row in list_kss:
			frappe.delete_doc('Kartu Stock Sales',row.name)
			frappe.db.commit()
		list_gle = frappe.db.get_list("Gold Ledger Entry", filters={"bundle":self.bundle})
		for row in list_gle:
			frappe.delete_doc('Gold Ledger Entry',row.name)
			frappe.db.commit()
		list_ts = frappe.db.get_list("Update Bundle Stock",filters={"bundle":self.bundle})
		for row in list_ts:
			frappe.delete_doc('Update Bundle Stock',row.name)
			frappe.db.commit()
		
		start_generate(self.tahun, self.bulan, self.bundle)
		list_ginv = frappe.db.get_list("Gold Invoice", filters={"bundle":self.bundle})
		for row in list_ginv:
			submit_gold_ledger(row.name)

		frappe.msgprint("Generate Done")
		# self.get_details()