// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Transfer Barang Jadi', {
	setup: function(frm){
		frm.set_value('posting_time', frappe.datetime.now_time());
		frm.set_value('posting_date', frappe.datetime.get_today());
	},
	refresh: function(frm) {
		if (cur_frm.is_new()){
			frappe.db.get_value("Employee", { "user_id": frappe.session.user }, ["name"]).then(function (responseJSON) {
				cur_frm.set_value("employee", responseJSON.message.name);
				cur_frm.refresh_field("employee");
				frm.set_value('posting_time', frappe.datetime.now_time());
				frm.set_value('posting_date', frappe.datetime.get_today());
			});
		}
		frm.set_query("penerima", ()=>{
			return {
				"filters":[
					["department","=","Stockist - LMS"]
				]
			}
		})
	},
	kadar: function(frm){
		
	}
});
frappe.ui.form.on('Transfer Barang Jadi Item', {
	before_items_remove: function(frm,cdt,cdn){
		var d = locals[cdt][cdn]
		cur_frm.doc.total_qty -= d.qty				
		frm.refresh_field("total_qty")
		cur_frm.doc.total_berat -= d.berat				
		frm.refresh_field("total_berat")
	},
	no_spk: function(frm, cdt, cdn){
		// var d = locals[cdt][cdn]
		// frappe.call({
		// 	method: 'lestari.lestari.doctype.transfer_barang_jadi.transfer_barang_jadi.get_spk_ppic',
		// 	args: {
		// 		'no_spk': d.no_spk,
		// 		'kadar': frm.doc.kadar
		// 	},
		// 	callback: function(r) {
		// 		if (!r.exc) {
		// 			console.log(r.message)
		// 			d.kadar = r.message.kadar
		// 			d.sub_kategori = r.message.sub_kategori
		// 			d.no_fo = r.message.no_fo
		// 			cur_frm.refresh_field("items")
		// 		}
		// 	}
		// });
	},
	qty: function(frm,cdt,cdn){
		var d = locals[cdt][cdn]
		cur_frm.doc.total_qty += d.qty				
		frm.refresh_field("total_qty")
		// frm.refresh_field("items")
	},
	berat: function(frm,cdt,cdn){
		var d = locals[cdt][cdn]
		cur_frm.doc.total_berat = cur_frm.doc.total_berat + d.berat				
		frm.refresh_field("total_berat")
		// frm.refresh_field("items")
	}
})