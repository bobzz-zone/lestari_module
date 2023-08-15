// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Serah Terima Payment Stock", {
  refresh: function (frm) {
    // frm.fields_dict.details.grid.grid_buttons.addClass("hidden");
    // frm.set_df_property("details", "cannot_add_rows", true);
    // frm.set_df_property("details", "cannot_delete_rows", true);
  
    frm.set_query("sales_bundle", function () {
			return {
				"filters": [
					["Sales Stock Bundle", "aktif", "=", 1],
          ["Sales Stock Bundle", "sales", "=", cur_frm.doc.sales]
				]
			};
		  });
  },
  reset: function(frm){
    cur_frm.clear_table("details")
    // cur_frm.clear_table("items")
    cur_frm.refresh_fields()
  }
});
// frappe.ui.form.on("Serah Terima Stock Item Detail", {
//   // refresh: function(frm) {

//   // }
//   before_details_remove: function (frm, cdt, cdn) {
//     var d = locals[cdt][cdn];
//     console.log(d.idx)
//     // cur_frm.get_field("items").grid.grid_rows_by_docname[d.name].remove();
//     cur_frm.get_field("items").grid.grid_rows[d.idx - 1].remove();
//     cur_frm.refresh_field("items");
//   },
// });
