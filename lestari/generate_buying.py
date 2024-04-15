import json
import frappe
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cint, cstr, flt, get_link_to_form, getdate, new_line_sep, nowdate

@frappe.whitelist()
def generate_mr(doctype,filters,from_data=None):
	# frappe.msgprint(str(doctype))
	# frappe.msgprint(str(filters))
	name = json.loads(filters)
	# name = json.dumps(name)
	if from_data:
		for row in name:
			frappe.msgprint(str(row))
			mr = frappe.get_doc("Material Request", row)
			po = make_purchase_order(mr.name)
			po.transaction_date = mr.transaction_date
			po.schedule_date = mr.schedule_date
			po.save()
			po.submit()
			frappe.db.commit()
			frappe.msgprint(str(po.name))
			po_get = frappe.get_doc("Purchase Order", po.name)
			# print('== Purchase Order ==')
			pr = make_purchase_receipt(po_get.name)
			pr.transaction_date = po_get.transaction_date
			pr.schedule_date = po_get.schedule_date
			pr.save()
			pr.submit()
			frappe.db.commit()
			frappe.msgprint(str(pr.name))
			poinv = frappe.get_doc("Purchase Order", po.name)
			# print('== Purchase Invoice ==')
			pinv = make_purchase_invoice(poinv.name)
			pinv.transaction_date = poinv.transaction_date
			pinv.schedule_date = poinv.schedule_date
			pinv.save()
			pinv.submit()
			frappe.db.commit()
			frappe.msgprint(str(pinv.name))
	else:
		frappe.msgprint(str(name['name']))
		mr = frappe.get_doc("Material Request", name['name'])
		po = make_purchase_order(mr.name)
		po.transaction_date = mr.transaction_date
		po.schedule_date = mr.schedule_date
		po.save()
		po.submit()
		frappe.db.commit()
		frappe.msgprint(str(po.name))
		po_get = frappe.get_doc("Purchase Order", po.name)
		# print('== Purchase Order ==')
		pr = make_purchase_receipt(po_get.name)
		pr.transaction_date = po_get.transaction_date
		pr.schedule_date = po_get.schedule_date
		pr.save()
		pr.submit()
		frappe.db.commit()
		frappe.msgprint(str(pr.name))
		poinv = frappe.get_doc("Purchase Order", po.name)
		# print('== Purchase Invoice ==')
		pinv = make_purchase_invoice(poinv.name)
		pinv.transaction_date = poinv.transaction_date
		pinv.schedule_date = poinv.schedule_date
		pinv.save()
		pinv.submit()
		frappe.db.commit()
		frappe.msgprint(str(pinv.name))

def make_purchase_order(source_name, target_doc=None, args=None):
	doclist = get_mapped_doc(
		"Material Request",
		source_name,
		{
			"Material Request": {
				"doctype": "Purchase Order",
				"validation": {"docstatus": ["=", 1], "material_request_type": ["=", "Purchase"]},
			},
			"Material Request Item": {
				"doctype": "Purchase Order Item",
				"field_map": [
					["name", "material_request_item"],
					["parent", "material_request"],
					["uom", "stock_uom"],
					["uom", "uom"],
				],
			},
		},
	)

	return doclist

@frappe.whitelist()
def make_purchase_receipt(source_name, target_doc=None):
	def update_item(obj, target, source_parent):
		target.qty = flt(obj.qty) - flt(obj.received_qty)
		target.stock_qty = (flt(obj.qty) - flt(obj.received_qty)) * flt(obj.conversion_factor)
		target.amount = (flt(obj.qty) - flt(obj.received_qty)) * flt(obj.rate)
		target.base_amount = (
			(flt(obj.qty) - flt(obj.received_qty)) * flt(obj.rate) * flt(source_parent.conversion_rate)
		)

	doc = get_mapped_doc(
		"Purchase Order",
		source_name,
		{
			"Purchase Order": {
				"doctype": "Purchase Receipt",
				"field_map": {"supplier_warehouse": "supplier_warehouse"},
				"validation": {
					"docstatus": ["=", 1],
				},
			},
			"Purchase Order Item": {
				"doctype": "Purchase Receipt Item",
				"field_map": {
					"name": "purchase_order_item",
					"parent": "purchase_order",
					"bom": "bom",
					"material_request": "material_request",
					"material_request_item": "material_request_item",
					"sales_order": "sales_order",
					"sales_order_item": "sales_order_item",
					"wip_composite_asset": "wip_composite_asset",
				},
				"postprocess": update_item,
				"condition": lambda doc: abs(doc.received_qty) < abs(doc.qty)
				and doc.delivered_by_supplier != 1,
			},
			"Purchase Taxes and Charges": {"doctype": "Purchase Taxes and Charges", "add_if_empty": True},
		},
		target_doc,
<<<<<<< HEAD
=======

>>>>>>> 833acfa3a363eb3c48792d21a305c3ecc159e5f9
	)

	return doc

@frappe.whitelist()
def make_purchase_invoice(source_name, target_doc=None):
	
	fields = {
		"Purchase Order": {
			"doctype": "Purchase Invoice",
			"field_map": {
				"party_account_currency": "party_account_currency",
				"supplier_warehouse": "supplier_warehouse",
			},
			"field_no_map": ["payment_terms_template"],
			"validation": {
				"docstatus": ["=", 1],
			},
		},
		"Purchase Order Item": {
			"doctype": "Purchase Invoice Item",
			"field_map": {
				"name": "po_detail",
				"parent": "purchase_order",
				"wip_composite_asset": "wip_composite_asset",
			},
		},
		"Purchase Taxes and Charges": {"doctype": "Purchase Taxes and Charges", "add_if_empty": True},
	}

	doc = get_mapped_doc(
		"Purchase Order",
		source_name,
		fields,
		target_doc,
	)

	return doc