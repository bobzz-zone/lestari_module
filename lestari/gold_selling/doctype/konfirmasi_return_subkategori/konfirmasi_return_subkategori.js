// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt
function hitung(){
	var total_berat_input = 0
	if (cur_frm.doc.items.length > 0 ){
		// console.log(total_berat_input)
		$.each(cur_frm.doc.items, function(i,e){
			if(e.terima_berat != null){
			total_berat_input += e.terima_berat
			// console.log(e.terima_berat)
			}
		})
		cur_frm.set_value("total_berat_input",total_berat_input)
		cur_frm.refresh_field('total_berat_input')
	}
}

var list_kat = [];
frappe.ui.form.on('Konfirmasi Return Subkategori', {
	setup: function(frm){
		// cur_frm.fields_dict.items.grid.setup_grid_pagination = 100
		// cur_frm.fields_dict.items.grid.wrapper.on('keypress',function(event){
		// 	if(event.keyCode === 13){
		// 	return false;
		// 	}
		//   })
	},
	refresh: function(frm) {
		cur_frm.fields_dict.items.grid.wrapper.on("keypress", function(evt){
			// Code specified here will run when a key is pressed on the customer field.
			if(evt.keyCode === 13){
				// console.log('testtete')
				return false;
			}
			});
		// cur_frm.fields_dict['items'].grid.grid_rows.sortable('refresh');
		frm.get_field('items').grid.grid_pagination.page_length = 100;
		frm.get_field('items').grid.reset_grid();
		frm.fields_dict.items.grid.add_custom_button(__("Copy Row"), () => {
			let selected_children = frm.fields_dict.items.grid.get_selected_children();
			selected_children.forEach(doc => {
				doc.__checked = 0;			
				let row = frm.add_child("items", {});
				row.idx_konfirmasi = doc.idx_konfirmasi;
				row.item = doc.item;
				row.customer = doc.customer;
				row.child_table = doc.child_table;
				row.child_id = doc.child_id;
				row.voucher_type = doc.voucher_type;
				row.voucher_no = doc.voucher_no;
			});	
			if(selected_children){
				frm.fields_dict.items.grid.refresh();
			}
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
		frm.set_query("no_konfirmasi", function () {
			return {
				"filters": [
					["Konfirmasi Payment Return", "docstatus", "=", 1],
					["Konfirmasi Payment Return", "sales_bundle", "=", cur_frm.doc.sales_bundle],
				]
			};
		  });
		
	},no_konfirmasi: function(frm){
		if(cur_frm.doc.items){
			if(cur_frm.doc.items.length > 0){
				cur_frm.clear_table("items")
				cur_frm.refresh_field('items')
			}else{
				frappe.call({
					method: "get_konfirmasi",
					doc: frm.doc,
					callback: function (r){
						cur_frm.refresh_fields();	
						}
					})
			}
		}else{
			frappe.call({
				method: "get_konfirmasi",
				doc: frm.doc,
				callback: function (r){
					cur_frm.refresh_fields();
					}
				})
			}
	}
	
	// items_add: function(frm,cdt,cdn){
	// 	cur_frm.fields_dict['items'].grid.grid_rows.sortable('refresh');
	// },
	// items_remove: function(frm,cdt,cdn){
	// 	cur_frm.fields_dict['items'].grid.grid_rows.sortable('refresh');
	// },
});
frappe.ui.form.on('Konfirmasi Stock Subkategori Item', {
	items_add: function(frm, cdt,cdn){
		frappe.model.set_value(cdt, cdn,"sub_kategori","");
		frappe.model.set_value(cdt, cdn,"terima_berat","");
	},items_remove: function(frm, cdt,cdn){
		hitung();
	},
	terima_berat: function(frm,cdt,cdn){
		var d = locals[cdt][cdn]
		hitung();
	},
	duplicate: function(frm, cdt,cdn){
		cur_frm.get_field('items').grid.grid_rows_by_docname[cdn].duplicate_row_using_keys()
		// var d = locals[cdt][cdn]
		// console.log(cdt)
		// console.log(cdn)
		// let row = frm.add_child("items", {});
		// row.idx_konfirmasi = d.idx_konfirmasi;
		// row.item = d.item;
		// row.customer = d.customer;
		// row.child_table = d.child_table;
		// row.child_id = d.child_id;
		// row.voucher_type = d.voucher_type;
		// row.voucher_no = d.voucher_no;
		// cur_frm.refresh_field('items')
	}
})