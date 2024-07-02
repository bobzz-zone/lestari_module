// Copyright (c) 2024, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Generate Bahan Pembantu', {
	refresh: function(frm) {

	},
	bahan_pembantu: function(frm) {
		frm.clear_table("list_department")
		frm.clear_table("detail")
		frm.refresh_fields()
		frm.call("get_detail", { throw_if_missing: true }).then((r) => {
			cur_frm.refresh_fields();
		});
	},
	generate_pemakaian: function(frm){
		frm.call("generate_random_mr", { throw_if_missing: true }).then((r) => {
			cur_frm.refresh_fields();
		});
	}
});
