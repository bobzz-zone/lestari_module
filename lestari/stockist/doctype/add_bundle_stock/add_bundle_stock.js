// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Add Bundle Stock', {
	refresh: function(frm) {
		frm.set_query("item","items", function(doc, cdt, cdn) {
    			return {
    				"filters": {
    					"barang_yang_dibawa_sales":1
    				}
    			};

    		});
	}
});
