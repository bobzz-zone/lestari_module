// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Rekap Form Order"] = {
	"filters": [
		{
			"fieldname":"no_fo",
			"label": __("No FO"),
			"fieldtype": "Link",
			"options": "Form Order",
			// "reqd": 1
		},
		{
			"fieldname":"type",
			"label": __("Type"),
			"fieldtype": "Select",
			"options": ['','STA','STP','STO','Customer'],
			// "reqd": 1
		},{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			// "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},{
			"fieldname":"kadar",
			"label": __("Kadar"),
			"fieldtype": "Link",
			"options": "Data Logam",
			// "reqd": 1
		},
		{
			"fieldname":"kategori",
			"label": __("Kategori"),
			"fieldtype": "Link",
			"options": "Item Group",
			get_query: () => {
				// var company = frappe.query_report.get_filter_value('kategori');
				return {
					filters: {
						'parent_item_group': "Products"
					}
				}
			}
			// "reqd": 1
		},
		{
			"fieldname":"sub_kategori",
			"label": __("Sub Kategori"),
			"fieldtype": "Link",
			"options": "Item Group",
			get_query: () => {
				var company = frappe.query_report.get_filter_value('kategori');
				return {
					filters: {
						'parent_item_group': company
					}
				}
			}
			// "reqd": 1
		},{
			"fieldname":"model",
			"label": __("Jenis"),
			"fieldtype": "Link",
			"options": "Item",
			// "reqd": 1
		}
	]
};
