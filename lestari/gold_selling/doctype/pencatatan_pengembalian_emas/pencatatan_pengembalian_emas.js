// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Pencatatan Pengembalian Emas', {
	// refresh: function(frm) {

	// }
	sales_bundle: function(frm){
		frappe.call({
			method: "lestari.gold_selling.doctype.pencatatan_pengembalian_emas.pencatatan_pengembalian_emas.get_serah_terima_stock",
			args:{"customer":frm.doc.customer,"sales_bundle":frm.doc.sales_bundle},
			callback: function (r){
				console.log(r.message)
				var total_bruto = 0;
				$.each(r.message, function (i, item) {
					var addnew = frappe.model.add_child(cur_frm.doc, "Pencatatan Pengembalian Emas Item", "items");
					addnew.item = item.item;
					addnew.category = item.category;
					addnew.item_group = item.item_group;
					addnew.qty = item.qty;
					addnew.gold_payment_no = item.gold_payment_no;
					total_bruto += item.qty; 
					cur_frm.set_value("total_bruto", total_bruto);
					cur_frm.refresh_field("total_bruto");
				})
				cur_frm.refresh_field("items");
			}})
	}
});
