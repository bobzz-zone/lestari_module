// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Laporan Kas Bank"] = {
	"filters": [
		{
			"fieldname":"account",
			"label": __("Account"),
			"fieldtype": "Link",
			"options": "Account",
			"reqd": 1
		},{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			// "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -24),
			"reqd": 1
		},{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
/**		{
			"fieldname":"against",
				"label": __("Against"),
				"fieldtype": "Link",
				"options": "Account",
		},*/
		{
			"fieldname":"cost_center",
				"label": __("Cost Center"),
				"fieldtype": "Link",
				"options": "Cost Center",
		}
	]
};
