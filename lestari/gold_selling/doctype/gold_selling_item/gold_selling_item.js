// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gold Selling Item', {
	refresh: function(frm) {
		frm.set_query("item_group", function(doc) {
    			return {
    				"filters": {
    					"is_group":1
    				}
    			};

    		});
	}
});
