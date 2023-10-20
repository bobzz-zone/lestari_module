// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Rekap Aktivitas Sales', {
	refresh: function(frm) {
		frm.add_custom_button(__("Reset"), () => frm.events.reset_form(frm));
		$(":button[data-label='Reset']").css("background-color", "red");
    	$(":button[data-label='Reset']").css("color", "white");
		cur_frm.meta.default_print_format = "Rekap Aktivitas Sales"
		cur_frm.page.add_menu_item(
			__("Print"),
			function () {
				frm.print_doc();
			},
			true
		);
		cur_frm.print_icon = cur_frm.page.add_action_icon(	
			"printer",
			function () {
				frm.print_doc();
			},
			"",
			__("Print")
		);
	},
	sales: function(frm){
		frm.set_query("bundle", function(){
			return {
				"filters": [
					["Sales Stock Bundle", "sales", "=", frm.doc.sales],
				]
			}
		});
	},
	get_details: function(frm){
		if(frm.doc.sales && frm.doc.bundle){
			frm.clear_table("detail")
			frm.refresh_fields()
			frm.call("get_details", { throw_if_missing: true }).then((r) => {})
		}else{
			frappe.msgprint("Isikan Sales dan no Bundle dahulu !!")
		}
	},
	reset_form: function(frm){
		frm.doc.sales = ""
		frm.doc.bundle = ""
		frm.doc.pendamping = ""
		frm.doc.total_barang_dibawa = 0
		frm.doc.total_barang_terjual = 0
		frm.doc.sisa_barang = 0
		frm.doc.lebih_kurang = 0
		frm.clear_table("detail")
		frm.refresh_fields()
		
	}
});
