# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
import json
import os
import ast
import requests
from frappe import _, msgprint
from frappe.model.document import Document

from frappe.utils import cstr, validate_url, get_url

class WhatsappCenter(Document):
	@frappe.whitelist()
	def get_child(self):
		doc = frappe.get_doc("Whatsapp Template", self.template)
		body = []
		for row in doc.detail:
			if row.type == 'HEADER':
				self.header_format = row.format
			
			if row.type == 'BODY':
				parts = row.text.split("{{")
				for index, e in enumerate(parts[1:]):
					body.append({
						'no': index+1
					})

			# baris_baru = {
			# 	"type": row.type,
			# 	"format": row.format,
			# 	"text": row.text,
			# 	"image": row.image,
			# 	"buttons": row.buttons,
			# 	"document": row.document,
			# 	"video": row.video
			# }

			# self.append("detail",baris_baru)
			self.set('body_table',body)

	@frappe.whitelist()
	def create_receiver_list(self):
		rec, where_clause = "", ""
		if self.send_to == "All Customer Contact":
			where_clause = " and dl.link_doctype = 'Customer'"
			if self.customer:
				where_clause += (
					" and dl.link_name = '%s'" % self.customer.replace("'", "'")
					or " and ifnull(dl.link_name, '') != ''"
				)
		if self.send_to == "All Supplier Contact":
			where_clause = " and dl.link_doctype = 'Supplier'"
			if self.supplier:
				where_clause += (
					" and dl.link_name = '%s'" % self.supplier.replace("'", "'")
					or " and ifnull(dl.link_name, '') != ''"
				)
		if self.send_to == "All Sales Partner Contact":
			where_clause = " and dl.link_doctype = 'Sales Partner'"
			if self.sales_partner:
				where_clause += (
					"and dl.link_name = '%s'" % self.sales_partner.replace("'", "'")
					or " and ifnull(dl.link_name, '') != ''"
				)
		if self.send_to in [
			"All Contact",
			"All Customer Contact",
			"All Supplier Contact",
			"All Sales Partner Contact",
		]:
			rec = frappe.db.sql(
				"""select CONCAT(ifnull(c.first_name,''), ' ', ifnull(c.last_name,'')),
				c.mobile_no from `tabContact` c, `tabDynamic Link` dl  where ifnull(c.mobile_no,'')!='' and
				c.docstatus != 2 and dl.parent = c.name%s"""
				% where_clause
			)

		elif self.send_to == "All Lead (Open)":
			rec = frappe.db.sql(
				"""select lead_name, mobile_no from `tabLead` where
				ifnull(mobile_no,'')!='' and docstatus != 2 and status='Open'"""
			)

		elif self.send_to == "All Employee (Active)":
			where_clause = (
				self.department and " and department = '%s'" % self.department.replace("'", "'") or ""
			)
			where_clause += self.branch and " and branch = '%s'" % self.branch.replace("'", "'") or ""

			rec = frappe.db.sql(
				"""select employee_name, cell_number from
				`tabEmployee` where status = 'Active' and docstatus < 2 and
				ifnull(cell_number,'')!='' %s"""
				% where_clause
			)

		elif self.send_to == "All Sales Person":
			rec = frappe.db.sql(
				"""select sales_person_name,
				tabEmployee.cell_number from `tabSales Person` left join tabEmployee
				on `tabSales Person`.employee = tabEmployee.name
				where ifnull(tabEmployee.cell_number,'')!=''"""
			)

		rec_list = ""
		for d in rec:
			rec_list += d[0] + " - " + d[1] + "\n"
		self.receiver_list = rec_list

	def get_receiver_nos(self):
		receiver_nos = []
		if self.receiver_list:
			for d in self.receiver_list.split("\n"):
				receiver_no = d
				if "-" in d:
					receiver_no = receiver_no.split("-")[1]
				if receiver_no.strip():
					receiver_nos.append(cstr(receiver_no).strip())
		else:
			msgprint(_("Receiver List is empty. Please create Receiver List"))

		return receiver_nos

	def payload_wa(self):
		def component_template():
			component = []
			if self.header_format:
				format = self.header_format.lower()
				if format in ['document', 'image', 'video']:
					body = { "link": (get_url() if not validate_url(self.get(format)) else '') + self.get(format)  }

				component.append({
					"type":"header",
					"parameters":[
						{
							"type": format,
							format: body
						}
					]
				}) 
			
			if len(self.body_table) > 0:
				body_param = []
				for row_body in self.body_table:
					body_param.append({
						"type": "text",
						"text": row_body.parameter
					})

				component.append({
					"type":"body",
					"parameters": body_param
				})

			return component

		if self.is_template == 'Yes':
			return {
				"type": "template",
				"template": {
					"name": self.template_name,
					"language": { "code": self.template_lang },
					"components": component_template()
				}
			}

	@frappe.whitelist()
	def send_wa(self):
		receiver_list = self.get_receiver_nos() or []
		
		if receiver_list:
			component = self.payload_wa()
			for i in receiver_list:
			#send_sms(receiver_list, cstr(self.message))
				wa_setting = frappe.get_doc("Whatsapp Setting")
				# component = wa_template.components.replace("'", '"')
				url = "https://graph.facebook.com/{}/{}/messages".format(wa_setting.version,wa_setting.phone_number_id)
				
				data = {
					"messaging_product": "whatsapp",
					"to": i,
					**component
				}

				payload = json.dumps(data)
				msgprint(payload)

				headers = {
					'Content-Type': 'application/json',
					'Authorization': 'Bearer {}'.format(wa_setting.user_access_token)
				}

				resp = requests.request("POST",url,headers=headers, data=payload, allow_redirects=False)
				ret = json.loads(resp.text)
				frappe.msgprint(str(ret))

	
