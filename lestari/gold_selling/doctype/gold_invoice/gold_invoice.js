// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Gold Invoice", {
	// setup:function(frm){
	// 	frm.events.make_custom_buttons(frm);
	// },
	validate: function (frm) {
		if (!cur_frm.doc.no_invoice) {
			cur_frm.set_df_property("no_invoice", "hidden", 1);
		}
		
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
		$.each(frm.doc.invoice_advance, function (i, g) {
			if (g.idr_allocated) {
			idr = idr + g.idr_allocated;
			}
		});
		frm.doc.total_idr_in_gold = idr / frm.doc.tutupan;
		frm.doc.total_advance = frm.doc.total_gold + frm.doc.total_idr_in_gold;
		frm.doc.outstanding = frm.doc.grand_total - frm.doc.total_advance;
		refresh_field("outstanding");
		refresh_field("total_idr_in_gold");
		refresh_field("total_advance");
	},
	ppn: function (frm){
		hitung_pajak(frm)
	},
	pph: function (frm){
		hitung_pajak(frm)
	},
	total_sebelum_pajak: function (frm){
		hitung_pajak(frm)
	},
	total_setelah_pajak: function (frm){
		hitung_pajak(frm)
	}
});
function hitung_ppn(frm){
	
}
function hitung_pph(frm){
	
}
function hitung_pajak(frm){
	// if (frm.doc.tax_status=="Tax"){
		//semua pajak di bagi 10.000
		var ppn_rate=110;
		var pph_rate=25;
		if (frm.doc.non_pph==1){
			if(frm.doc.is_skb==1){
				pph_rate=0;
			}else{
				ppn_rate=165;
				pph_rate=0;
			}
		}
		frm.doc.ppn=Math.floor(frm.doc.grand_total * frm.doc.tutupan * ppn_rate / 10000);
		frm.doc.pph=Math.floor(frm.doc.grand_total * frm.doc.tutupan * pph_rate / 10000);
		frm.doc.total_sebelum_pajak = Math.floor(frm.doc.grand_total * frm.doc.tutupan)

		//frm.doc.total_tax_in_gold = (frm.doc.ppn+frm.doc.pph) / frm.doc.tutupan;
		frm.doc.total_pajak=frm.doc.ppn+frm.doc.pph;
		frm.doc.sisa_pajak=frm.doc.total_pajak;
		frm.doc.total_setelah_pajak = frm.doc.total_sebelum_pajak + frm.doc.total_pajak
		refresh_field("pph");
		refresh_field("ppn");
		refresh_field("total_pajak");
		refresh_field("sisa_pajak");
		refresh_field("total_sebelum_pajak");
		refresh_field("total_setelah_pajak");
	// }
}

function hitung_rate(frm,cdt,cdn){
	var d = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, "amount", Math.floor((d.rate * d.qty) *10)/1000);
		frappe.model.set_value(cdt, cdn, "print_amount", Math.floor((d.print_rate * d.qty)*10)/1000);
		frappe.model.set_value(cdt, cdn, "jumlah", d.amount * cur_frm.doc.tutupan);
		var total = 0;
		var total_bruto = 0;
		$.each(frm.doc.items, function (i, g) {
			total = total + g.amount;
			total_bruto = total_bruto + g.qty;
		});
		frm.doc.total = total;
		frm.doc.total_bruto = total_bruto;
		if (!frm.doc.discount_amount) {
			frm.doc.discount_amount = 0;
		}
		frm.doc.grand_total = frm.doc.total - frm.doc.discount_amount;
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
		hitung_rate(frm,cdt,cdn)
	},
	rate: function (frm, cdt, cdn) {
		hitung_rate(frm,cdt,cdn)
	},
	jumlah: function (frm, cdt, cdn){
		hitung_rate(frm,cdt,cdn)
	}
});
