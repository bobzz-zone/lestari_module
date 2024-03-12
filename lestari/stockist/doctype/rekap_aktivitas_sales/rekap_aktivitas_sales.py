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
						creation
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
				frappe.msgprint(detail[row]['id']+'aktivitas='+detail[row]['aktivitas'])
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
