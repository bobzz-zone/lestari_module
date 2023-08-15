// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Purchase Request', {
	// refresh: function(frm) {

	// }
	template: function(frm){
		frappe.call({
			method: "lestari.prepurchase.doctype.purchase_request.purchase_request.get_template",
			args: {
				template: frm.doc.template,
			},
			callback: function(r) {
				if(r.message && !r.exc) {
					console.log(r.message)
					me.frm.set_value("items", r.message);
				}
			}
		})
	}
});
