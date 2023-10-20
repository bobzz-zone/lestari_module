// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Transfer Salesman"] = {
	"filters": [
		{
			"fieldname":"bundle",
			"label": __("Bundle"),
			"fieldtype": "Link",
			"options": "Sales Stock Bundle",
			// "reqd": 1
		},
		{
			"fieldname":"sales",
			"label": __("Sales"),
			"fieldtype": "Link",
			"options": "Sales Partner",
			// "reqd": 1
		},
		{
			"fieldname":"pendamping",
			"label": __("Sales"),
			"fieldtype": "Link",
			"options": "Sales Partner",
			// "reqd": 1
		}
		,{
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
		}
	]
};
