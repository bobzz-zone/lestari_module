# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class WorkOrderLilin(Document):

	def validate(self):
		if not self.barcode:
			self.barcode = self.name

	@frappe.whitelist()
	def create_wo_lilin(self):
		sumber_doc = frappe.get_doc("Data Pohon Lilin", self.pohon_id)
		# target_doc.employee_id = sumber_doc.created_by
		self.created_date = sumber_doc.created_date
		self.pohon_id = sumber_doc.name
		self.warehouse_tujuan = "Lilin - L"
		self.kadar = sumber_doc.kadar

		sumber_resep = frappe.db.sql("""
		SELECT
		dplr.no_spk,
		dplr.resep_mul_karet,
		dplr.mul_karet,
		dplr.produk_id,
		dplr.logo,
		dplr.inject,
		dplr.qty
		FROM `tabData Pohon Lilin` dpl
		JOIN `tabData Pohon Lilin Resep` dplr ON dplr.parent = dpl.name
		WHERE dplr.parent = "{}"
		""".format(self.pohon_id),as_dict=1)

		kadar = []
		for row in sumber_resep:
			# qty = str(row.qty)
			gambar = frappe.get_doc("Item", row.produk_id).image
			kadar = frappe.get_doc("Item", row.produk_id).kadar
			# html = "<img src='"+gambar+"' class='img-responsive' style='width:50%'/>"
			inject = row.qty / row.inject
			# frappe.msgprint(html)
			baris_baru = {
					"no_spk": row.no_spk,
					"resep_mul_karet": row.resep_mul_karet,
					"mul_karet": row.mul_karet,
					"produk_id": row.produk_id,
					"image": gambar,
					"logo": row.logo,
					"inject": inject,
					"qty" : row.qty,
					# "gambar": html
					}

			self.append("tabel_pohon",baris_baru)

			# frappe.msgprint(str(kadar))
			self.kadar = kadar
		sumber_batu = frappe.db.sql("""
		SELECT DISTINCT
		item.item_code,
		rmk.rubber_mould as mul_karet,
		rmk.name as resep_mul_karet,
		rilb.qty as qty,
		(rilb.qty * dplr.qty) AS total
		FROM `tabItem` item
		JOIN `tabResep Investment Lilin Batu` rilb ON rilb.batu = item.item_code
		JOIN `tabResep Mul Karet` rmk ON rmk.name = rilb.parent
		JOIN `tabData Pohon Lilin Resep` dplr ON dplr.resep_mul_karet = rmk.name
		WHERE dplr.parent = "{}"
		ORDER BY item.item_code DESC
		""".format(self.pohon_id),as_dict=1)

		temp = []
		total = 0
		material = ""
		for row in sumber_batu:
			if len(temp) < 1:
				temp.append({
					"mul_karet": row['mul_karet'],
					"resep_mul_karet" : row['resep_mul_karet'],
					"item_code" : row['item_code'],
					"qty" : row['qty'],
					"total": row['total']
				})
			else:
				for check in temp:
					if check['item_code'] == row['item_code']:
						check['total'] = check['total'] + row['total']
					else:
						status = True
						for check_2 in temp:
							if check_2['item_code'] == row['item_code']:
								status = False
						if status:
							temp.append({
								"mul_karet": row['mul_karet'],
								"resep_mul_karet" : row['resep_mul_karet'],
								"item_code" : row['item_code'],
								"qty" : row['qty'],
								"total": row['total']
							})
						
		for row in sumber_batu:
			# frappe.msgprint(str(row))
			baris_baru = {
			"mul_karet": row['mul_karet'],
			"resep_mul_karet" : row['resep_mul_karet'],
			"batu" : row['item_code'],
			"qty" : row['qty'],
			"total_qty": row['total']
			} 
			self.append("tabel_batu",baris_baru)

		# self.flags.ignore_permissions = True
		# self.save()  

	def on_submit(self):
		sumber_doc = self
		#------ Form Hasil Work Order -------
		target_doc = frappe.new_doc("NTHKO Lilin")
		target_doc.pohon_id = sumber_doc.pohon_id
		target_doc.work_order_id = sumber_doc.name
		target_doc.warehouse_tujuan = "Supermarket - LMS"
		target_doc.kadar = sumber_doc.kadar
		target_doc.ukuran_base_karet = sumber_doc.ukuran_base_karet
		target_doc.nomor_base_karet = sumber_doc.nomor_base_karet
		# target_doc.area = sumber_doc.area
		# target_doc.proses = "Finish"
		target_doc.sprue_utama = sumber_doc.sprue_utama
		# target_doc.kepala_line = sumber_doc.kepala_line
		target_doc.no_line = sumber_doc.no_line
		target_doc.operator = sumber_doc.operator
		# target_doc.no_mesin = sumber_doc.no_mesin
		target_doc.no_kotak = sumber_doc.no_kotak

		target_doc2 = frappe.new_doc("Form Kebutuhan Mul Karet")
		target_doc2.pohon_id = sumber_doc.pohon_id
		target_doc2.work_order_id = sumber_doc.name

		if sumber_doc.tabel_batu:
			target_doc1 = frappe.new_doc("Form Berat Material Pohon")
			target_doc1.pohon_id = sumber_doc.pohon_id
			target_doc1.work_order_id = sumber_doc.name
			target_doc1.berat_base_karet = sumber_doc.berat_base_karet

			sumber_batu = frappe.db.sql("""
			SELECT DISTINCT
				woltp.no_spk,
				woltp.produk_id,
				woltp.logo,
				woltb.total_qty AS qty_pesan,
				woltb.resep_mul_karet,
				woltb.mul_karet,
				woltb.batu,
				woltb.qty,
				woltb.total_qty,
				woltb.warna_batu
				FROM `tabWork Order Lilin` wol
				LEFT JOIN `tabWork Order Lilin Batu` woltb ON woltb.parent = wol.name
				LEFT JOIN `tabWork Order Lilin Item` woltp ON woltp.parent = wol.name
				WHERE wol.name = "{}"
			""".format(sumber_doc.name),as_dict=1)

			total_qty_batu = 0
			for batu in sumber_batu:
				if batu:
					total_qty_batu += batu.total_qty
					baris_baru = {
						"no_spk": batu.no_spk,
						"produk_id": batu.produk_id,
						"mul_karet": batu.mul_karet,
						"resep_mul_karet": batu.resep_mul_karet,
						"qty_pesan": batu.qty_pesan,
						"batu": batu.batu,
						"qty": batu.qty,
						"total_qty": batu.total_qty,
						"warna_batu": batu.warna_batu
					}
					target_doc1.append("material_batu",baris_baru)
					target_doc1.total_qty_batu = total_qty_batu
			target_doc1.flags.ignore_permission = True
			target_doc1.save()

		sumber_mul = frappe.db.sql("""
		SELECT
		woltp.no_spk,
		woltp.produk_id,
		woltp.mul_karet,
		woltp.mul_karet_id,
		woltp.resep_mul_karet,
		woltp.qty
		FROM `tabWork Order Lilin` wol
		JOIN `tabWork Order Lilin Item` woltp ON woltp.parent = wol.name
		WHERE wol.name = "{}"
		""".format(sumber_doc.name),as_dict=1)
		for mul in sumber_mul:
			baris_baru = {
				"no_spk": mul.no_spk,
				"produk_id": mul.produk_id,
				"mul_karet": mul.mul_karet,
				"mul_karet_id": mul.mul_karet_id
			}
			target_doc2.append("tabel_mul_karet",baris_baru)
		target_doc2.flags.ignore_permission = True
		target_doc2.save()		
		qty = 0
		if sumber_doc.tabel_batu:
			for row in sumber_batu:
				qty += qty + row.qty
				baris_baru = {
					"no_spk": row.no_spk,
					"produk_id": row.produk_id,
					"mul_karet": row.mul_karet,
					"logo": row.logo,
					"batu": row.batu,
					"qty": row.qty,
					"total_qty": row.total_qty,
					"warna_batu": row.warna_batu,
					"resep_mul_karet": row.resep_mul_karet,
					"qty_pesan":row.qty_pesan
				}
				target_doc.append("tabel_batu",baris_baru)

		baris_baru = {
			"no_spk":sumber_doc.tabel_pohon[0].no_spk,
			"pohon_id":sumber_doc.pohon_id,
			"tanggal_pohonan":sumber_doc.created_date,
			"kadar":sumber_doc.kadar,
			"ukuran_base_karet":sumber_doc.ukuran_base_karet,
			"nomor_base_karet":sumber_doc.nomor_base_karet
			}
		target_doc.append("tabel_detail",baris_baru)

		target_doc.flags.ignore_permission = True
		target_doc.save()

		target_doc3 = frappe.get_doc('Data Pohon Lilin', self.pohon_id)
		target_doc3.warehouse = "Supermarket - L"
		target_doc3.nomor_base_karet = self.nomor_base_karet
		target_doc3.ukuran_base_karet = self.ukuran_base_karet
		target_doc3.sprue_utama = self.sprue_utama
		target_doc3.workflow_state = "Supermarket"
		baris_baru = {
				"warehouse": "Supermarket - L",
				"nomor_wo": self.name
			}
		target_doc3.append("lokasi",baris_baru)
		target_doc3.flags.ignore_permission = True
		target_doc3.save()