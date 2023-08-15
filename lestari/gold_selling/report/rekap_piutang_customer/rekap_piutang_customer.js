// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Rekap Piutang Customer"] = {
	"filters": [
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
			"reqd": 1
		}
	]
};
