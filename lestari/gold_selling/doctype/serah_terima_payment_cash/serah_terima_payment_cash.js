// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Serah Terima Payment Cash', {
	refresh: function (frm) {
		// frm.fields_dict.details.grid.grid_buttons.addClass("hidden");
		// frm.set_df_property("details", "cannot_add_rows", true);
		// frm.set_df_property("details", "cannot_delete_rows", true);
	  },
	sales: function (frm){
		frm.set_query("bundle", function(){
			return {
				"filters": [
					["Sales Stock Bundle", "sales", "=", frm.doc.sales],
				]
			}
		});
	}
});
frappe.ui.form.on("Serah Terima Payment Cash Deposit", {
	// refresh: function(frm) {
  
	// }
	// before_payment_remove: function (frm, cdt, cdn) {
	//   var d = locals[cdt][cdn];
	  // cur_frm.get_field("items").grid.grid_rows_by_docname[d.name].remove();
	//   cur_frm.get_field("details").grid.grid_rows[d.idx - 1].remove();
	//   cur_frm.refresh_field("details");
	// },
  });