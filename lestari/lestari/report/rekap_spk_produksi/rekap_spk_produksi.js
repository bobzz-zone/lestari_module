// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Rekap SPK Produksi"] = {
	"filters": [
		{
			"fieldname":"no_spk",
			"label": __("No SPK"),
			"fieldtype": "Link",
			"options": "SPK Produksi",
			// "reqd": 1
		},
		{
			"fieldname":"form_order",
			"label": __("No FO"),
			"fieldtype": "Data",
			"options": "Form Order",
			// "reqd": 1
		},
		{
			"fieldname":"type",
			"label": __("Type"),
			"fieldtype": "Data",
			// "options": ['','STA','STP','STO','Customer'],
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
		// {
		// 	"fieldname":"kategori",
		// 	"label": __("Kategori"),
		// 	"fieldtype": "Link",
		// 	"options": "Item Group",
		// 	get_query: () => {
		// 		// var company = frappe.query_report.get_filter_value('kategori');
		// 		return {
		// 			filters: {
		// 				'parent_item_group': "Products"
		// 			}
		// 		}
		// 	}
		// 	// "reqd": 1
		// },
		{
			"fieldname":"sub_kategori",
			"label": __("Sub Kategori"),
			"fieldtype": "Link",
			"options": "Item Group",
			// get_query: () => {
			// 	// var company = frappe.query_report.get_filter_value('kategori');
			// 	return {
			// 		filters: {
			// 			'parent_item_group': company
			// 		}
			// 	}
			// }
			// "reqd": 1
		},{
			"fieldname":"produk_id",
			"label": __("Produk ID"),
			"fieldtype": "Link",
			"options": "Item",
			// "reqd": 1
		}
	]
};
