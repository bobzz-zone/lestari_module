// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Gold Invoice", {
	// setup:function(frm){
	// 	frm.events.make_custom_buttons(frm);
	// },
	before_save: function (frm) {
		// if (!cur_frm.doc.no_invoice) {
			// cur_frm.set_df_property("no_invoice", "hidden", 1);
			
		// }

		// var roman_list = ['I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII']
		// var no_invoice = cur_frm.doc.no_invoice
		// var posting_date = frappe.datetime.str_to_obj(cur_frm.doc.posting_date)
		// var bulan = posting_date.getMonth()
		// var tahun = posting_date.getFullYear()
		// no_invoice = no_invoice+"/"+roman_list[bulan]+"/"+tahun
		// cur_frm.set_value("no_invoice",no_invoice)
		// cur_frm.refresh_field("no_invoice")
	},
	refresh: function (frm) {
	// your code here
	frm.set_query("bundle", function(){
		return {
			"filters": [
				["Sales Stock Bundle","aktif", "=", "1"],
			]
		}
	});
	frm.set_query("category","items", function(){
		return {
			"filters": [
				["Gold Selling Item","Enable", "=", "1"],
			]
		}
	});
		frm.events.make_custom_buttons(frm);
		if (!cur_frm.doc.tutupan) {
			frappe.call({
				method: "lestari.gold_selling.doctype.gold_rates.gold_rates.get_latest_rates",
				args: { type: cur_frm.doc.type_emas || "LD"},
				callback: function (r) {
					cur_frm.doc.tutupan = r.message.nilai;
					cur_frm.refresh_field("tutupan");
				},
			});
		}
	if (frm.doc.docstatus > 0) {
		cur_frm.add_custom_button(
		__("Accounting Ledger"),
		function () {
			frappe.route_options = {
			voucher_no: frm.doc.name,
			from_date: frm.doc.posting_date,
			to_date: moment(frm.doc.modified).format("YYYY-MM-DD"),
			company: frm.doc.company,
			group_by: "Group by Voucher (Consolidated)",
			show_cancelled_entries: frm.doc.docstatus === 2,
			};
			frappe.set_route("query-report", "General Ledger");
		},
		__("View")
		);
	}
	frm.set_query("category", function (doc) {
		return {
		filters: {
			// "is_group":1
			parent_item_group: "Products",
		},
		};
	});
	},
	make_custom_buttons: function (frm) {
	if (frm.doc.docstatus === 1) {
		frm.add_custom_button(__("Quick Payment"), () => frm.events.get_gold_payment(frm));
	}
	},
	get_gold_payment: function (frm) {
	frm.call("get_gold_payment", { throw_if_missing: true }).then((r) => {
		if (r.message) {
		console.log(r.message);
		frappe.set_route("Form", r.message.doctype, r.message.name);
		}
	});
	},
	customer:function (frm){
		cur_frm.set_value("contact_address",cur_frm.doc.customer+"-Billing")
		cur_frm.refresh_field("contact_address")
	},
	type_kurs:function (frm) {
		frappe.call({
			method: "lestari.gold_selling.doctype.gold_rates.gold_rates.get_latest_rates",
			args: { type: frm.doc.type_kurs},
			callback: function (r) {
				frm.doc.tutupan = r.message.nilai;
				refresh_field("tutupan");
			},
		});
	},
	posting_date:function(frm){
		frappe.call({
				method: "lestari.gold_selling.doctype.gold_rates.gold_rates.get_latest_rates",
				args: { type: frm.doc.type_emas || "CT"},
				callback: function (r) {
					frm.doc.tutupan = r.message.nilai;
					refresh_field("tutupan");
				},
			});
	},
	tutupan: function (frm) {
		var idr = 0;
		hitung_rate_all(frm);
		frm.doc.total_idr_in_gold = idr / frm.doc.tutupan;
		frm.doc.outstanding = frm.doc.grand_total - frm.doc.total_advance;
		refresh_field("outstanding");
		refresh_field("total_idr_in_gold");
		
	},
	ppn: function (frm){
		var ppn_rate=110;
		var pph_rate=25;
		if(frm.doc.is_skb==1){
			pph_rate=0;
		}else if (!frm.doc.tax_id){
			ppn_rate=165;
			pph_rate=0;
		}
		// frm.doc.ppn=Math.floor(frm.doc.total_sebelum_pajak * ppn_rate / 10000);
		frm.doc.total_pajak=frm.doc.ppn+frm.doc.pph;
		frm.doc.sisa_pajak=frm.doc.total_pajak;
		frm.doc.total_setelah_pajak = frm.doc.total_sebelum_pajak + frm.doc.total_pajak
		console.log(frm.doc.total_pajak)
		refresh_field("total_pajak");
		refresh_field("sisa_pajak");
		refresh_field("total_setelah_pajak");	
	},
	pph: function (frm){
		var ppn_rate=110;
		var pph_rate=25;
		if(frm.doc.is_skb==1){
			pph_rate=0;
		}else if (!frm.doc.tax_id){
			ppn_rate=165;
			pph_rate=0;
		}
		// frm.doc.pph=Math.floor(frm.doc.total_sebelum_pajak * pph_rate / 10000);
		frm.doc.total_pajak=frm.doc.ppn+frm.doc.pph;
		frm.doc.sisa_pajak=frm.doc.total_pajak;
		frm.doc.total_setelah_pajak = frm.doc.total_sebelum_pajak + frm.doc.total_pajak
		console.log(frm.doc.total_pajak)
		refresh_field("total_pajak");
		refresh_field("sisa_pajak");
		refresh_field("total_setelah_pajak");	
	},
	total_sebelum_pajak: function (frm){
		sebelum_pajak(frm)
	},
});
function sebelum_pajak(frm){
	var ppn_rate=110;
		var pph_rate=25;
		if(frm.doc.is_skb==1){
			pph_rate=0;
		}else if (!frm.doc.tax_id){
			ppn_rate=165;
			pph_rate=0;
		}
		frm.doc.grand_total = frm.doc.total_sebelum_pajak / frm.doc.tutupan
		refresh_field("grand_total");
		frm.doc.ppn=Math.floor(frm.doc.total_sebelum_pajak * ppn_rate / 10000);
		frm.doc.pph=Math.floor(frm.doc.total_sebelum_pajak * pph_rate / 10000);
		refresh_field("ppn");
		refresh_field("pph");
		console.log(frm.doc.ppn)
		console.log(frm.doc.pph)

		frm.doc.total_pajak=frm.doc.ppn+frm.doc.pph;
		frm.doc.sisa_pajak=frm.doc.total_pajak;
		frm.doc.total_setelah_pajak = frm.doc.total_sebelum_pajak + frm.doc.total_pajak
		
		refresh_field("total_pajak");
		refresh_field("sisa_pajak");
		refresh_field("total_setelah_pajak");
}
function hitung_ppn(ppn_rate, frm){
	frm.doc.ppn=Math.floor(cur_frm.doc.total_sebelum_pajak * ppn_rate / 10000);
	refresh_field("ppn");
}
function hitung_pph(pph_rate, frm){
	frm.doc.pph=Math.floor(cur_frm.doc.total_sebelum_pajak * pph_rate / 10000);
	refresh_field("pph");
}
function hitung_pajak(frm){
	// if (frm.doc.tax_status=="Tax"){
		//semua pajak di bagi 10.000
		var ppn_rate=110;
		var pph_rate=25;
		if(frm.doc.is_skb==1){
			pph_rate=0;
		}else if (!frm.doc.tax_id){
			ppn_rate=165;
			pph_rate=0;
		}
		hitung_ppn(ppn_rate, frm)
		hitung_pph(pph_rate, frm)
		
		var total=0;
		$.each(frm.doc.items, function (i, g) {
			total = total + g.jumlah;
		}); 
		frm.doc.total_sebelum_pajak=total;
		//frm.doc.total_tax_in_gold = (frm.doc.ppn+frm.doc.pph) / frm.doc.tutupan;
		frm.doc.total_pajak=frm.doc.ppn+frm.doc.pph;
		frm.doc.sisa_pajak=frm.doc.total_pajak;
		frm.doc.total_setelah_pajak = frm.doc.total_sebelum_pajak + frm.doc.total_pajak
		
		refresh_field("total_pajak");
		refresh_field("sisa_pajak");
		refresh_field("total_sebelum_pajak");
		refresh_field("total_setelah_pajak");
	// }
}

function hitung_rate(frm,cdt,cdn,update_all){
	console.log('test')
	var d = locals[cdt][cdn];
	if (update_all){
		frappe.model.set_value(cdt, cdn, "amount", Math.floor((d.rate * d.qty) *10)/1000);
		frappe.model.set_value(cdt, cdn, "print_amount", Math.floor((d.print_rate * d.qty)*10)/1000);
	}
		frappe.model.set_value(cdt, cdn, "jumlah", d.amount * cur_frm.doc.tutupan);
		var total = 0;
		var total_bruto = 0;
		var total_rp=0
		$.each(frm.doc.items, function (i, g) {
			g.jumlah=g.amount*frm.doc.tutupan;
			total = total + g.amount;
			total_bruto = total_bruto + g.qty;
			total_rp = total + g.jumlah;
		});
		frm.doc.total = total;
		frm.doc.total_bruto = total_bruto;
		if (!frm.doc.discount_amount) {
			frm.doc.discount_amount = 0;
		}
		frm.doc.grand_total = total_rp;
		hitung_pajak(frm);
		frm.doc.outstanding = frm.doc.grand_total - frm.doc.total_advance;
		refresh_field("outstanding");
		refresh_field("total");
		refresh_field("total_print");
		refresh_field("total_bruto");
		refresh_field("discount_amount");
		refresh_field("grand_total");
}
function hitung_rate_all(frm){
		var total = 0;
		var total_bruto = 0;
		var total_rp=0
		$.each(frm.doc.items, function (i, g) {
			g.jumlah=g.amount*frm.doc.tutupan;
			total = total + g.amount;
			total_bruto = total_bruto + g.qty;
			total_rp = total + g.jumlah;
		});
		frm.doc.total = total;
		frm.doc.total_bruto = total_bruto;
		if (!frm.doc.discount_amount) {
			frm.doc.discount_amount = 0;
		}
		frm.doc.grand_total = total_rp;
		hitung_pajak(frm);
		frm.doc.outstanding = frm.doc.grand_total - frm.doc.total_advance;
		refresh_field("outstanding");
		refresh_field("total");
		refresh_field("total_print");
		refresh_field("total_bruto");
		refresh_field("discount_amount");
		refresh_field("grand_total");
}
frappe.ui.form.on("Gold Invoice Item", {
	items_remove: function(frm, cdt, cdn){
		hitung_rate(frm,cdt,cdn,false)
	},
	category: function (frm, cdt, cdn) {
		// your code here
		var d = locals[cdt][cdn];
		if (!d.category) {
			return;
		}
		frappe.call({
			method: "lestari.gold_selling.doctype.gold_invoice.gold_invoice.get_gold_rate",
			args: { category: d.category, customer: frm.doc.customer, customer_group: frm.doc.customer_group,customer_print : frm.doc.subcustomer || "" },
			callback: function (r) {
				frappe.model.set_value(cdt, cdn, "rate", r.message.nilai);
				frappe.model.set_value(cdt, cdn, "print_rate", r.message.nilai_print);
				hitung_rate(frm,cdt,cdn)
			},
		});
	},
	qty: function (frm, cdt, cdn) {
		hitung_rate(frm,cdt,cdn,true)
	},
	rate: function (frm, cdt, cdn) {
		hitung_rate(frm,cdt,cdn,true)
	},
	amount: function (frm, cdt, cdn){
		hitung_rate(frm,cdt,cdn,false)
	}
});
