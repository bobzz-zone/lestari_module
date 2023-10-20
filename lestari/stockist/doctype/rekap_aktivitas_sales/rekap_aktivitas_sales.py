# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class RekapAktivitasSales(Document):
	@frappe.whitelist()
	def get_details(self):
		list_rekap = frappe.db.sql(
			"""
				SELECT
					a.name,
					a.sales,
					a.bundle,
					a.type,
					a.docstatus,
					a.total_bruto,
					a.date,
					b.kadar,
					b.bruto
					FROM
					`tabUpdate Bundle Stock` a
					JOIN
					`tabUpdate Bundle Stock Kadar` b
					ON
					a.name = b.parent
					WHERE a.bundle = '{}' AND a.sales = '{}' AND a.docstatus = 1
					ORDER BY
					CASE
						WHEN TYPE = 'New Stock'
						THEN 1
						WHEN TYPE = 'Add Stock'
						THEN 2
						WHEN TYPE = 'Deduct Stock'
						THEN 3
						END,
						a.creation
		""".format(self.bundle,self.sales),as_dict = 1)
		# frappe.throw(str(list_rekap))
		detail = {}
		new_stock_name = []
		# frappe.msgprint(str(len(list_rekap)))
		# frappe.msgprint(str(list_rekap))
		total_dibawa = 0
		if len(list_rekap) > 0:
			for row in list_rekap:
				if row.type == "New Stock":
					detail.setdefault(row.name,{
						"id": row.name,
						"tgl_rekap": row.date,
						"aktivitas": row.type,
						"6k": 0,
						"8k": 0,
						"8kp": 0,
						"16k": 0,
						"17k": 0,
						"17kp": 0,
						"total": row.total_bruto
					})
				elif row.type == "Deduct Stock":
					detail.setdefault(row.name,{
						"id": row.name,
						"tgl_rekap": row.date,
						"aktivitas": row.type,
						"6k": 0,
						"8k": 0,
						"8kp": 0,
						"16k": 0,
						"17k": 0,
						"17kp": 0,
						"total": row.total_bruto
					})
				else:
					detail.setdefault(row.name,{
						"id": row.name,
						"tgl_rekap": row.date,
						"aktivitas": row.type,
						"6k": 0,
						"8k": 0,
						"8kp": 0,
						"16k": 0,
						"17k": 0,
						"17kp": 0,
						"total": row.total_bruto
					})
				if row.kadar == "06K":
					detail[row.name]['6k'] = row.bruto
				if row.kadar == "08K":
					detail[row.name]['8k'] = row.bruto
				if row.kadar == "08KP":
					detail[row.name]['8kp'] = row.bruto
				if row.kadar == "16K":
					detail[row.name]['16k'] = row.bruto
				if row.kadar == "17K":
					detail[row.name]['17k'] = row.bruto
				if row.kadar == "17KP":
					detail[row.name]['17kp'] = row.bruto		
				self.append("detail",detail[row.name])
			tot_6k = 0
			tot_8k = 0
			tot_8kp = 0
			tot_16k = 0
			tot_17k = 0
			tot_17kp = 0
			grand_tot = 0
			for row in detail:
				if detail[row]['aktivitas'] != "Deduct Stock":
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
				"total" : "{:.3f}".format(grand_tot),
			})
			self.total_barang_dibawa = grand_tot
			self.save()
		else:
			frappe.throw("Data Kosong")
