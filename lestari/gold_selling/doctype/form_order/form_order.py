# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class FormOrder(Document):
	@frappe.whitelist()
	def match_data(self):
		#reset valid Items
		self.items_valid=[]
		self.items_invalid=[]
		#sort all item into grouped array of category
		data={}
		valid_data={}
		map_qty_category={}
		list_category=[]
		for row in self.items:
			if row.kategori_pohon not in data:
				data[row.kategori_pohon]=[]
				valid_data[row.kategori_pohon]=[]
				map_qty_category[row.kategori_pohon]=row.qty_isi_pohon
				list_category.append(row.kategori_pohon)
			#append yang sisa saja ,sisanya masukan ke valid data
			to_made=row.qty
			while to_made >= row.qty_isi_pohon:
				valid_data[row.kategori_pohon].append({"used":0,"no_pohon":0,"model":row.model,"item_name":row.item_name,"kadar":row.kadar,"sub_kategori":row.sub_kategori,"kategori":row.kategori,"qty":row.qty_isi_pohon,"qty_isi_pohon":row.qty_isi_pohon,"kategori_pohon":row.kategori_pohon})
				to_made=to_made-row.qty_isi_pohon
			if to_made>0:
				data[row.kategori_pohon].append({"used":0,"model":row.model,"item_name":row.item_name,"kadar":row.kadar,"sub_kategori":row.sub_kategori,"kategori":row.kategori,"qty":to_made,"qty_isi_pohon":row.qty_isi_pohon,"kategori_pohon":row.kategori_pohon,"no_pohon":0})
		no_pohon=0
		for category in list_category:
			#marking valid data first
			for valid in valid_data[category]:
				no_pohon=no_pohon+1
				valid["no_pohon"]=no_pohon
				self.append("items_valid",valid)
			qty_should=map_qty_category[category]
			#check total qty pada data dan mapped it
			for row in data[category]:
				if row["used"]==0:
					row["used"]=1
					found=False
					needed_qty=qty_should-row["qty"]
					#cari yang matching qty
					for match in data[category]:
						if match["used"]==0:
							if match["qty"]==needed_qty:
								no_pohon=no_pohon+1
								row["no_pohon"]=no_pohon
								match["no_pohon"]=no_pohon
								match["used"]=1
								self.append("items_valid",row)
								self.append("items_valid",match)
								found=True
								break
					if not found:
						row["used"]=0
			#cocokan top sisa
			temp=[]
			cur_qty=0
			for row in data[category]:
				if row["used"]==0:
					qty=row["qty"]
					if qty_should - cur_qty - row["qty"]>0:
						cur_qty=cur_qty+row["qty"]
						row["used"]=1
						temp.append(row)
					else:
						qty=qty_should - cur_qty
						row["qty"]=row["qty"]-qty
						no_pohon=no_pohon+1
						for x in temp:
							x["no_pohon"]=no_pohon
							self.append("items_valid",x)
						self.append("items_valid",{"model":row["model"],"item_name":row["item_name"],"kadar":row["kadar"],"sub_kategori":row["sub_kategori"],"kategori":row["kategori"],"qty":qty,"qty_isi_pohon":row["qty_isi_pohon"],"kategori_pohon":row["kategori_pohon"],"no_pohon":no_pohon})
						if row["qty"]==0:
							row["used"]=1
						#reset
						temp=[]
						cur_qty=0
			#masukan invalid kalau ada sisa
			for row in data[category]:
				if row["used"]==0:
					self.append("items_invalid",row)
			#masukan tekp sisa
			for row in temp:
				self.append("items_invalid",row)
			self.total_pohon=no_pohon