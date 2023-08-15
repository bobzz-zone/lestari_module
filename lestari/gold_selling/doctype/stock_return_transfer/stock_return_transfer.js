// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stock Return Transfer', {
	// refresh: function(frm) {

	// }
	get_details: function(frm){
		if(cur_frm.doc.transfer_details){
				cur_frm.clear_table("transfer_details")
				cur_frm.refresh_fields()
		}
		frappe.call({
			method: "get_kpr",
			doc: frm.doc,
			callback: function (r){
				frm.refresh();	
			}
		})
	}
});
