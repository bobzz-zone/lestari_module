// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt

function hitung(){
	var totaldibawa = 0,
	totaldikembalikan = 0,
	totalberat = 0;
		$.each(cur_frm.doc.items, function(i,e){
		// console.log(e.qty_penambahan)
		if(e.total_dibawa_sales != null){
		totaldibawa = parseFloat(totaldibawa) + parseFloat(e.total_dibawa_sales)
		// console.log(totaldibawa)
		}
		if(e.total_dikembalikan != null){
		totaldikembalikan = parseFloat(totaldikembalikan) + parseFloat(e.total_dikembalikan)
		// console.log(totaldikembalikan)
		}
		// e.total_closing = parseFloat(totaldibawa) + parseFloat(totaldikembalikan)
	})
	totalberat = parseFloat(totaldibawa) + parseFloat(totaldikembalikan)
	cur_frm.set_value("total_bruto", totalberat)
	cur_frm.refresh_field("total_bruto")

	cur_frm.clear_table("per_kadar")
		cur_frm.refresh_field('per_kadar');
		var totals = {};
		var dibawas = {};
		var dikembalikans = {};
			cur_frm.doc.items.forEach(function(row) {
				// console.log(row)
				var kadar = row.kadar;
				var dibawa = parseFloat(row.total_dibawa_sales);
				var dikembalikan = parseFloat(row.total_dikembalikan);
				// var closing = parseFloat(row.total_closing);
				if (!totals[kadar]) {
					totals[kadar] = 0;
					dibawas[kadar] = 0;
					dikembalikans[kadar] = 0;
				}
				totals[kadar] += dibawa + dikembalikan;
				dibawas[kadar] += dibawa;
				dikembalikans[kadar] += dikembalikan;
				console.log(dikembalikans[kadar])
			});
			for (var kadar in totals) {
				var child = cur_frm.add_child('per_kadar');
				child.kadar = kadar;
				child.total_closing = totals[kadar];
				child.total_dikembalikan = dikembalikans[kadar];
				child.total_dibawa = dibawas[kadar];
				// console.log(total_berat);
			}
			cur_frm.refresh_field('per_kadar');
}


var list_kat = [];
frappe.ui.form.on('Close Bundle Stock', {
	refresh: function(frm) {
		cur_frm.get_field("bundle").set_focus()
		// if( connected == 0){
		frm.add_custom_button(__("Connect"), () => frm.events.get_connect(frm));
		// }else{
		frm.add_custom_button(__("Disconnect"), () => frm.events.get_disconnect(frm));
		// }

		frm.set_query("bundle", function(){
			return {
				"filters": [
					["Sales Stock Bundle", "aktif", "=", "1"],
				]
			}
		});
		frappe.db.get_value("Employee", { "user_id": frappe.session.user }, ["name","id_employee"]).then(function (responseJSON) {
			cur_frm.set_value("pic", responseJSON.message.name);
			// cur_frm.set_value("id_employee", responseJSON.message.id_employee);
			cur_frm.get_field("bundle").set_focus()
			cur_frm.refresh_field("pic");
			// cur_frm.refresh_field("id_employee");
		  //   console.log(responseJSON)
		});
		frappe.db.get_list('Item Group', {
			filters: {
				parent_item_group: 'Products'
			}
		}).then(records => {
			for(var i = 0; i<= records.length; i++){
				list_kat.push(records[i].name)
			}
		})
		frm.set_query("sub_kategori", "items", function () {
			return {
				"filters": [
					["Item Group", "parent_item_group", "in", list_kat],
				]
			};
		  });
		
	},
	bundle: function(frm){
		// if(cur_frm.doc.items != null){
		// 	cur_frm.clear_table("items")
		// 	cur_frm.refresh_field('items');
		// }
		frappe.call({
			method: 'lestari.stockist.doctype.close_bundle_stock.close_bundle_stock.get_detail_bundle',
			args: {
				bundle: cur_frm.doc.bundle
			},
			callback: (r) => {
				// on success
				console.log(r.message)
				r.message.forEach(element => {
					console.log(element)
					cur_frm.add_child('items',{
						sub_kategori: element.sub_kategori,
						kategori: element.kategori,
						total_dibawa_sales: element.total_dibawa_sales,
						kadar: element.kadar,
						gold_selling_item: element.gold_selling_item 	
					})
					cur_frm.refresh_field('items');
				});
			},
			error: (r) => {
				// on error
			}
		})
	},
	
});
frappe.ui.form.on('Detail Close Stock', {
	items_add: function (frm, cdt, cdn){
		var d = locals[cdt][cdn];
        var idx = d.idx;
        var prev_kadar = 0;
		$.each(frm.doc.items, function(i,g){
			if(g.kadar != null){
				prev_kadar = g.kadar;
			}else{
				g.kadar = prev_kadar
			}
			cur_frm.refresh_field("item")
		})
		d.kadar = prev_kadar
        cur_frm.refresh_field('items');
	},
	sub_kategori: function (doc,cdt, cdn){
		var d = locals[cdt][cdn];
		if(d.kadar != null){
		frappe.call({
			method: 'lestari.stockist.doctype.update_bundle_stock.update_bundle_stock.get_sub_item',
			args: {
				'kadar': d.kadar,
				'sub_kategori': d.sub_kategori
			},
			callback: function(r) {
				if (!r.exc) {
					d.item = r.message[0][0]
					d.gold_selling_item = r.message[0][1]
					cur_frm.refresh_field("items")
				}
			}
		});
		}
	}, 
	items_remove: function(frm,cdt,cdn){
		hitung()
	},
	total_dibawa_sales:function(frm,cdt,cdn){
		hitung()
		var d = locals[cdt][cdn];
		var total_closing = parseFloat(d.total_dibawa_sales) + parseFloat(d.total_dikembalikan)
		frappe.model.set_value(cdt, cdn, 'total_closing', total_closing);
		cur_frm.refresh_field("items")
	},
	total_dikembalikan:function(frm,cdt,cdn){
		hitung()
		var d = locals[cdt][cdn];
		var total_closing = parseFloat(d.total_dibawa_sales) + parseFloat(d.total_dikembalikan)
		frappe.model.set_value(cdt, cdn, 'total_closing', total_closing);
		cur_frm.refresh_field("items")
	 }
	
})