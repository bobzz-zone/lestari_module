frappe.listview_settings['Form Order'] = {
	add_fields: ["status"],
	get_indicator: function (doc) {
		if (doc.status === "Ordered PPIC") {
			return [__("Ordered PPIC"), "green", "status,=,Ordered PPICed"];
	    }
	},
};
