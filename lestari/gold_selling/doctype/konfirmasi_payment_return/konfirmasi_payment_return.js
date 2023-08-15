// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt

var list_kat = [];
frappe.ui.form.on('Konfirmasi Payment Return', {
	refresh: function(frm) {
		frappe.db.get_list('Item Group', {
			filters: {
				parent_item_group: 'Products'
			}
		}).then(records => {
			for(var i = 0; i<= records.length; i++){
				list_kat.push(records[i].name)
			}
		})
		frm.set_query("sub_kategori", "detail_perhiasan", function () {
			return {
				"filters": [
					["Item Group", "parent_item_group", "in", list_kat],
				]
			};
		  });
	},
	serah_terima: function(frm) {
		frappe.call({
			method: "get_serah_terima",
			doc: frm.doc,
			callback: function (r){
				frm.refresh();	
				}
			})
	}
});

function hitung(){
	var totalberat = 0;
	var tolak = 0;
	var terima = 0;
	var totals = {};
	var total_tolak = {};
	var total_terima = {};
	if(cur_frm.doc.detail_rongsok.length > 0){
		$.each(cur_frm.doc.detail_rongsok, function(i,e){
			// console.log(e.qty_penambahan)
			if(e.qty != null){
			totalberat = parseFloat(totalberat) + parseFloat(e.qty)
			tolak = parseFloat(tolak) + parseFloat(e.tolak_qty)
			terima = parseFloat(terima) + parseFloat(e.terima_qty)
			} 
		})
	}
	if(cur_frm.doc.detail_perhiasan.length > 0){
		$.each(cur_frm.doc.detail_perhiasan, function(i,e){
			// console.log(e.qty_penambahan)
			if(e.qty != null){
				totalberat = parseFloat(totalberat) + parseFloat(e.qty)
				tolak = parseFloat(tolak) + parseFloat(e.tolak_qty)
				terima = parseFloat(terima) + parseFloat(e.terima_qty)
			}
		})
	}
	cur_frm.set_value("total_terima",terima)
	cur_frm.set_value("total_tolak",tolak)
	cur_frm.set_value("total_berat",totalberat)
	console.log(totalberat)
	cur_frm.refresh_fields()
	cur_frm.clear_table("detail_kadar")
	cur_frm.doc.detail_perhiasan.forEach(function(row) {
		var kadar = row.kadar;
		if (!totals[kadar]) {
			totals[kadar] = 0;
			total_tolak[kadar] = 0;
			total_terima[kadar] = 0;
		// }else{	
			// console.log('hallo')
		}
		totals[kadar] += parseFloat(row.qty);
		total_tolak[kadar] += parseFloat(row.tolak_qty);
		total_terima[kadar] +=  parseFloat(row.terima_qty);
	});
	cur_frm.doc.detail_rongsok.forEach(function(row) {
		var kadar = row.kadar;
		if (!totals[kadar]) {
			totals[kadar] = 0;
			total_tolak[kadar] = 0;
			total_terima[kadar] = 0;
		// }else{	
			// console.log('hallo')
		}
		totals[kadar] += parseFloat(row.qty);
		total_tolak[kadar] += parseFloat(row.tolak_qty);
		total_terima[kadar] +=  parseFloat(row.terima_qty);
	});
	for (var kadar in totals) {
		var total_berat = totals[kadar];
		var totalterima = total_terima[kadar];
		var totaltolak = total_tolak[kadar];
		var child = cur_frm.add_child('detail_kadar');
		child.kadar = kadar;
		child.qty = total_berat;
		child.total_berat = total_berat;
		child.terima_qty = totalterima;
		child.tolak_qty = totaltolak;
	}
	cur_frm.refresh_field('detail_kadar');
}

frappe.ui.form.on('Konfirmasi Payment Return Perhiasan', {
	terima_qty: function(frm, cdt, cdn){
		var d=locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn,"tolak_qty",d.qty-d.terima_qty);
		frappe.model.set_value(cdt, cdn,"total_berat",d.terima_qty+d.tolak_qty);
		hitung()
	},
	tolak_qty: function(frm, cdt, cdn){
		var d=locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn,"terima_qty",d.qty-d.tolak_qty);
		frappe.model.set_value(cdt, cdn,"total_berat",d.terima_qty+d.tolak_qty);
		hitung()
	}
	});
frappe.ui.form.on('Konfirmasi Payment Return Rongsok', {
	terima_qty: function(frm, cdt, cdn){
		var d=locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn,"tolak_qty",d.qty-d.terima_qty);
		frappe.model.set_value(cdt, cdn,"total_berat",d.terima_qty+d.tolak_qty);
		hitung()
	},
	tolak_qty: function(frm, cdt, cdn){
		var d=locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn,"terima_qty",d.qty-d.tolak_qty);
		frappe.model.set_value(cdt, cdn,"total_berat",d.terima_qty+d.tolak_qty);
		hitung()
	}
})
