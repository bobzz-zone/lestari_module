// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

var isButtonClicked = false;
var isButtonClicked1 = false;
function run_writeoff_sisa(frm){
	if(frm.doc.unallocated_payment>0){
		frm.doc.write_off=frm.doc.write_off+frm.doc.unallocated_payment;
		frm.doc.unallocated_payment=0;
		refresh_field("write_off");
		refresh_field("unallocated_payment");
		frm.doc.total_sisa_invoice=0;
		refresh_field("total_sisa_invoice");
	}
	if(frm.doc.unallocated_idr_payment>0){
		frm.doc.write_off_idr=frm.doc.write_off_idr+frm.doc.unallocated_idr_payment;
		frm.doc.unallocated_idr_payment=0;
		refresh_field("write_off_idr");
		refresh_field("unallocated_idr_payment");
	}
	if (frm.doc.total_sisa_invoice>0){
		if(frm.doc.total_sisa_invoice>0.1){
			frappe.msgprint("Penghapusan Sisa Invoice Melebihi 0.1 Gram Emas di lakukan apabila document ini di submit")
		}
		frm.doc.write_off=frm.doc.write_off-frm.doc.total_sisa_invoice;
		refresh_field("write_off");
		//frm.doc.total_sisa_invoice=0
	}
	$.each(frm.doc.invoice_table,  function(i,  g) {
		frappe.model.set_value(g.doctype, g.name, "allocated", g.outstanding);
	});
	frm.doc.write_off_total=(frm.doc.write_off*frm.doc.tutupan)+frm.doc.write_off_idr;
	refresh_field("write_off_total");
	refresh_total_and_charges(frm);
}
//tax allocated itu di pisah tp kalo un allocated based on mata uang...
function calculate_table_invoice(frm,cdt,cdn){
	var total=0;
	var total_pajak=0;
	$.each(frm.doc.invoice_table,  function(i,  g) {
		total=total+g.outstanding;
		total_pajak=g.outstanding_tax;
	});
	$.each(frm.doc.customer_return,  function(i,  g) {
		total=total+g.outstanding;
	});
	frm.doc.total_pajak=total_pajak;
	frm.doc.total_invoice=total;
	refresh_field("total_pajak");
	refresh_field("total_invoice");
	//frappe.model.set_value(cdt, cdn,"allocated",0);
	frm.doc.discount_amount=(frm.doc.bruto_discount/100*frm.doc.discount).toFixed(3);
	refresh_field("discount_amount");
}
function calculate_table_invoice_alo(frm,cdt,cdn){
	var allocated=0;
	var tax_allocated=0;
	$.each(frm.doc.invoice_table,  function(i,  g) {
		allocated=allocated+g.allocated;
		tax_allocated=g.tax_allocated;
	});
	$.each(frm.doc.customer_return,  function(i,  g) {
		allocated=allocated+g.allocated;
	});
	frm.doc.allocated_idr_payment=tax_allocated;
	frm.doc.allocated_payment=allocated ;
	refresh_field("allocated_payment");
	/*refresh_field("unallocated_idr_payment");
	refresh_field("unallocated_payment");*/
	refresh_field("allocated_idr_payment");
	//refresh_field("discount_amount");
	//frappe.msgprint("invoice table reloaded");
}
function refresh_total_and_charges(frm){
	frm.doc.total_extra_charges=Math.floor((frm.doc.bonus - frm.doc.discount_amount)*1000)/1000;
	refresh_field("total_extra_charges");
	if (frm.doc.allocated_payment>0){
		if (frm.doc.allocated_payment>frm.doc.total_extra_charges){
			frm.doc.total_sisa_invoice=frm.doc.total_invoice - frm.doc.allocated_payment;
		}else{
			frm.doc.total_sisa_invoice=frm.doc.total_invoice + frm.doc.total_extra_charges - frm.doc.allocated_payment;
		}
	}else{
		frm.doc.total_sisa_invoice=frm.doc.total_invoice + frm.doc.total_extra_charges;
	}
	frm.doc.total_sisa_invoice = frm.doc.total_sisa_invoice+frm.doc.write_off;
	if (frm.doc.total_sisa_invoice <0 ){
		frm.doc.total_sisa_invoice=0;
	}
	refresh_field("total_sisa_invoice");
}


function reset_allocated(frm){
	$.each(frm.doc.invoice_table,  function(i,  g) {
		g.allocated=0;
		g.tax_allocated=0;
		frappe.model.set_value(g.doctype, g.name, "allocated", 0);
		frappe.model.set_value(g.doctype, g.name, "tax_allocated", 0);
	});
	frm.doc.allocated_payment=0;
	frm.doc.allocated_idr_payment=0;
	frm.doc.unallocated_idr_payment=frm.doc.total_idr_payment ;
	frm.doc.unallocated_payment=frm.doc.total_gold_payment ;
	//frm.doc.unallocated_write_off=0;
	frm.doc.write_off=0;
	frm.doc.write_off_idr=0;
	frm.doc.write_off_total=0;
	frm.doc.jadi_deposit=0;
	refresh_field("allocated_idr_payment");
	refresh_field("allocated_payment");
	refresh_field("unallocated_idr_payment");
	refresh_field("unallocated_payment");
	//refresh_field("unallocated_write_off");
	refresh_field("write_off");
	refresh_field("write_off_idr");
	refresh_field("write_off_total");
	refresh_field("jadi_deposit");
	//frappe.msgprint("Reset Called");
	refresh_total_and_charges(frm);
	console.log("Karena ad aperubahan nilai, maka data alokasi dan write off telah ter reset!!");
}
function calculate_table_idr(frm,cdt,cdn){
	var total=0;
	$.each(frm.doc.idr_payment,  function(i,  g) {
		total=total+g.amount;
	});
	frm.doc.total_idr_payment=total;
	frm.doc.total_idr_gold=total/frm.doc.tutupan;
	refresh_field("total_idr_payment");
	refresh_field("total_idr_gold");
	//calculate total payment
	frm.doc.total_payment=frm.doc.total_gold_payment+frm.doc.total_idr_gold;
	frm.doc.unallocated_idr_payment=frm.doc.total_idr_payment ;
	frm.doc.unallocated_payment=frm.doc.total_gold_payment+frm.doc.total_idr_gold-frm.doc.allocated_payment;
	//frappe.msgprint("Callculate IDR");
	refresh_field("total_payment");
	refresh_field("unallocated_payment");
	refresh_field("unallocated_idr_payment");
	if(frm.doc.allocated_payment!=0){
		reset_allocated(frm);
	}else if(frm.doc.allocated_idr_payment!=0){
		reset_allocated(frm);
	}
}

function calculate_table_stock(frm,cdt,cdn){
	var d=locals[cdt][cdn];
	// frappe.model.set_value(cdt, cdn,"amount",d.rate*d.qty/100);
	var total=0;
	$.each(frm.doc.stock_payment,  function(i,  g) {
		total=total+g.amount;
	});
	frm.doc.total_gold_payment=total;
	refresh_field("total_gold_payment");
	//calculate total payment
	frm.doc.total_payment=frm.doc.total_gold_payment+frm.doc.total_idr_gold;
	refresh_field("total_payment");
	reset_allocated(frm);
	/*frm.doc.unallocated_idr_payment=frm.doc.total_idr_payment+frm.doc.total_idr_advance;
	frm.doc.unallocated_payment=frm.doc.total_gold_payment+frm.doc.total_gold;
	//frappe.msgprint("Callculate Stock");
	refresh_field("unallocated_payment");
	refresh_field("unallocated_idr_payment");*/
}

frappe.ui.form.on('Gold Payment', {
	validate:function(frm){
		//validate allocated amount
		
		$.each(frm.doc.invoice_table,  function(i,  g) {
			frappe.db.get_value("Gold Invoice", g.gold_invoice, ["bundle"]).then((responseJSON)=>{cur_frm.set_value("sales_bundle",responseJSON.message.bundle)})
			if (g.allocated>g.outstanding){
				frappe.msgprint("Nota "+g.gold_invoice+" nilai alokasi salah");
				return false;
			}
		});
		
		
	},
	discount:function(frm){
		if (frm.doc.discount<0){
			return
		}
		frm.doc.discount_amount=frm.doc.bruto_discount*frm.doc.discount/100;
		refresh_field("discount_amount");
		refresh_total_and_charges(frm);
	},
	bruto_discount:function(frm){
		if (frm.doc.discount<0){
			return
		}
		/*var disc=0
		$.each(frm.doc.invoice_table,  function(i,  g) {
			if (g.allocated>0){
				disc=disc+(g.total_bruto/100*frm.doc.discount);
			}
		});*/
		frm.doc.discount_amount=frm.doc.bruto_discount*frm.doc.discount/100;
		refresh_field("discount_amount");
		refresh_total_and_charges(frm);
	},
	write_off:function(frm){
		refresh_total_and_charges(frm);
	},
	bonus:function(frm){
		refresh_total_and_charges(frm);
	},
	reset_alokasi:function(frm){
		reset_allocated(frm);
	},
	writeoff_sisa:function(frm){
		//need to change
		run_writeoff_sisa(frm);
	},
	jadikan_deposit:function(frm){
		//need to check
		frm.doc.jadi_deposit=frm.doc.unallocated_payment + (frm.doc.unallocated_idr_payment/frm.doc.tutupan);
		frm.doc.unallocated_payment=0;
		frm.doc.unallocated_idr_payment=0;
		frappe.msgprint("Total Deposit "+frm.doc.jadi_deposit);
		refresh_field("unallocated_payment");
		refresh_field("unallocated_idr_payment");
		refresh_field("jadi_deposit");
		//frm.dirty();
	},
	auto_distribute:function(frm){
		if (frm.doc.invoice_table==[] && frm.doc.customer_return==[]){
			frappe.throw("Tidak ada Invoice yang terpilih");
		}else{
			reset_allocated(frm);
			//payment rupiah selali di alokasikan ke pajak dulu apabila ada pajak
			if (frm.doc.total_pajak>0){
				var idr_need_to=frm.doc.unallocated_idr_payment;
				var total_allocated=0;
				$.each(frm.doc.invoice_table,  function(i,  g) {
					if (idr_need_to > g.outstanding_tax){
						g.tax_allocated=g.outstanding_tax;
					}else{
						g.tax_allocated=idr_need_to;
					}
					total_allocated = total_allocated + g.tax_allocated;
					idr_need_to=idr_need_to-g.tax_allocated;
				});
				frm.doc.unallocated_idr_payment=idr_need_to;
				frm.doc.allocated_idr_payment = total_allocated;
				refresh_field("allocated_idr_payment");
			}
			var idr_to_gold=0;
			if (frm.doc.unallocated_idr_payment>0){
				idr_to_gold = (frm.doc.unallocated_idr_payment/frm.doc.tutupan);
				idr_to_gold=parseFloat(idr_to_gold).toFixed(3);
			}
			// var saldo_gold=frm.doc.unallocated_payment-frm.doc.total_extra_charges;
			var saldo_gold=frm.doc.unallocated_payment;
			var need_to= parseFloat(saldo_gold) + parseFloat(idr_to_gold);
			//frappe.msgprint("Need to "+need_to +" dari IDR "+idr_to_gold+" dari GOLD "+saldo_gold);
			// console.log(need_to)
			// var sisa_invoice = parseFloat(cur_frm.doc.total_invoice) - parseFloat(need_to) + frm.doc.total_extra_charges ;
			var sisa_invoice = parseFloat(cur_frm.doc.total_invoice) - parseFloat(need_to);
			if (sisa_invoice <0){
				sisa_invoice=0
			}
			cur_frm.set_value("total_sisa_invoice",sisa_invoice);
			refresh_field("total_sisa_invoice");
			need_to = parseFloat(need_to).toFixed(3);
			var total_alo=0;
			// console.log(need_to)
			if(need_to<=0){
				refresh_total_and_charges(frm);
				refresh_field("unallocated_idr_payment");
				//frappe.msgprint("Tidak ada pembayaran yang dapat di alokasikan");
				return;
			}
			$.each(frm.doc.customer_return,  function(i,  g) {
				var alo=0;
				if (need_to>(g.outstanding-g.allocated)){
					alo=g.outstanding-g.allocated;
					//cur_frm.doc.total_sisa_invoice = alo
				}else{
					alo=need_to;
				}
				total_alo=total_alo+alo;
				need_to=need_to-alo;
				frappe.model.set_value(g.doctype, g.name, "allocated", alo);
			});

			if (need_to>0) {
				$.each(frm.doc.invoice_table,  function(i,  g) {
					var alo=0;
					if (need_to>(g.outstanding-g.allocated)){
						alo=g.outstanding-g.allocated;
					}else{
						alo=need_to;
					}
					need_to=need_to-alo;
					total_alo=total_alo+alo;
					frappe.model.set_value(g.doctype, g.name, "allocated", g.allocated+alo);
				});
			}
			/*if (need_to<0){
				frappe.msgprint(" Test "+need_to);
				cur_frm.set_value("total_sisa_invoice",need_to*-1);
				need_to=0;*/
			//}else{
				
			//}	
			//refresh_field("total_sisa_invoice");
			if (idr_to_gold>0){
				var sisa_idr=parseFloat((idr_to_gold-(total_alo-saldo_gold))*frm.doc.tutupan).toFixed(0);
				frm.doc.unallocated_idr_payment=sisa_idr;
				cur_frm.set_value("unallocated_idr_payment",sisa_idr);
			}
			if (saldo_gold <= total_alo){
				frm.doc.unallocated_payment=0;
				cur_frm.set_value("unallocated_payment",0);
			}else{
				var unaloc=parseFloat(saldo_gold- total_alo).toFixed(3) ;
				console.log(unaloc)
				// if (isNan(unaloc)){
				// 	unaloc=0;
				// }
				frm.doc.unallocated_payment=unaloc;
				cur_frm.set_value("unallocated_payment",unaloc);
			}
			//frappe.msgprint("Unallocated "+cur_frm.doc.unallocated_payment);
			cur_frm.set_value("allocated_payment",parseFloat(total_alo).toFixed(3));
			refresh_field("unallocated_idr_payment");
			refresh_field("unallocated_payment");
			refresh_field("allocated_payment");
			
			
			var sisa_pay=(frm.doc.unallocated_idr_payment/frm.doc.tutupan) + frm.doc.unallocated_payment;
			if(sisa_pay<=1/100 && sisa_pay>0){
				frappe.msgprint("Write off sisa Sedikit "+(frm.doc.unallocated_idr_payment/frm.doc.tutupan) + frm.doc.unallocated_payment);
				run_writeoff_sisa(frm);
			}if(frm.doc.total_sisa_invoice<=0.01){
				frappe.msgprint("Write off sisa Invoice Senilai "+frm.doc.total_sisa_invoice);
				run_writeoff_sisa(frm);
			}else{
				refresh_total_and_charges(frm);	
			}
			frappe.msgprint("Pembayaran Telah di Alokasikan");
			// frappe.msgprint("Pembayaran Telah di Alokasikan");
		}

	},
	tutupan:function(frm){
		cur_frm.get_field("tutupan").set_focus()
		frm.doc.total_idr_gold=frm.doc.total_idr_payment/frm.doc.tutupan;
		refresh_field("total_idr_payment");
		refresh_field("total_idr_gold");
		//calculate total payment
		frm.doc.total_payment=frm.doc.total_gold_payment+frm.doc.total_idr_gold;
		refresh_field("total_payment");
		reset_allocated(frm);
	},
	get_gold_invoice:function(frm){
		// var button = cur_frm.get_field('get_gold_invoice').$input;
		// button.prop('disabled', true);
		// isButtonClicked = true;
		frappe.call({
			method: "get_gold_invoice",
			doc: frm.doc,
			callback: function (r){
				frm.refresh();
				calculate_table_invoice(cur_frm);
				reset_allocated(cur_frm);
				
			}
		});
		
	},
	refresh: function(frm) {
		// Get the input field element
        // var inputField = cur_frm.get_field('tutupan').$input;

        // // Attach keydown event listener
        // inputField.keydown(function(event) {
        //     // Check if the Enter key is pressed
        //     if (event.which === 13) {
        //         // Prevent the default Enter key action
        //         event.preventDefault();
        //         return false;
        //     }
        // });
		frm.set_query("item","stock_payment", function(doc, cdt, cdn) {
			return {
				"filters": {
					"available_for_stock_payment":1
				}
			};

		});
		frm.set_query("gold_invoice","invoice_table", function(doc, cdt, cdn) {
			return {
				"filters": {
					"docstatus":1,
					"invoice_status":"Unpaid",
					"customer":doc.customer
				}
			};

		});
		frm.set_query("sales_bundle", function(){
			return {
				"filters": [
				["Sales Stock Bundle", "aktif", "=", "1"],
				]
			}
		});

		if(!frm.doc.tutupan){
			frappe.call({
				method: "lestari.gold_selling.doctype.gold_rates.gold_rates.get_latest_rates",
				args:{type:frm.doc.type_emas},
				callback: function (r){
					frm.doc.tutupan=r.message.nilai;
					refresh_field("tutupan");

				}
			});
		}
		if(frm.doc.docstatus > 0) {
			cur_frm.add_custom_button(__('Accounting Ledger'), function() {
				frappe.route_options = {
					voucher_no: frm.doc.name,
					from_date: frm.doc.posting_date,
					to_date: moment(frm.doc.modified).format('YYYY-MM-DD'),
					company: frm.doc.company,
					group_by: "Group by Voucher (Consolidated)",
					show_cancelled_entries: frm.doc.docstatus === 2
				};
				frappe.set_route("query-report", "General Ledger");
			}, __("View"));
			cur_frm.add_custom_button(__("Stock Ledger"), function() {
				frappe.route_options = {
					voucher_no: me.frm.doc.name,
					from_date: me.frm.doc.posting_date,
					to_date: moment(me.frm.doc.modified).format('YYYY-MM-DD'),
					company: me.frm.doc.company,
					show_cancelled_entries: me.frm.doc.docstatus === 2
				};
				frappe.set_route("query-report", "Stock Ledger");
			}, __("View"));
		}
	},
	/*type_payment:function(frm){
		frm.doc.idr_payment=[];
		frm.doc.stock_payment=[];
		refresh_field("stock_payment");
		refresh_field("idr_payment")
	},*/
	type_emas:function(frm){
		frm.doc.stock_payment=[];
		refresh_field("stock_payment");
		frappe.call({
                                method: "lestari.gold_selling.doctype.gold_rates.gold_rates.get_latest_rates",
                                args:{type:frm.doc.type_emas},
                                callback: function (r){
                                        frm.doc.tutupan=r.message.nilai;
                                        refresh_field("tutupan")

                                }
                        });
	}

});

frappe.ui.form.on('Gold Payment Invoice', {
	gold_invoice:function(frm,cdt,cdn) {
		calculate_table_invoice(frm,cdt,cdn);
	},
	allocated:function(frm,cdt,cdn) {
		calculate_table_invoice_alo(frm,cdt,cdn);
		
	},
	invoice_table_remove: function(frm,cdt,cdn){
		calculate_table_invoice(frm,cdt,cdn);
		reset_allocated(frm);
	}
});

frappe.ui.form.on('IDR Payment', {
	amount:function(frm,cdt,cdn) {
		calculate_table_idr(frm,cdt,cdn)
	},
	idr_payment_remove:function(frm,cdt,cdn){
		calculate_table_idr(frm,cdt,cdn)
	}
});

frappe.ui.form.on('Stock Payment', {
	item:function(frm,cdt,cdn) {
		// your code here
		var d=locals[cdt][cdn];
		if(!d.item){return;}
		frappe.call({
			method: "lestari.gold_selling.doctype.gold_invoice.gold_invoice.get_gold_purchase_rate",
			args:{"item":d.item,"customer":frm.doc.customer,"customer_group":frm.doc.customer_group},
			callback: function (r){
				frappe.model.set_value(cdt, cdn,"rate",r.message.nilai);
				frappe.model.set_value(cdt, cdn,"amount",parseFloat(r.message.nilai)*d.qty/100);
				var total=0;
				$.each(frm.doc.stock_payment,  function(i,  g) {
					total=total+g.amount;
				});
				frm.doc.total_gold_payment=total;
				refresh_field("total_gold_payment");
				//calculate total payment
				frm.doc.total_payment=frm.doc.total_gold_payment+frm.doc.total_idr_gold;
				refresh_field("total_payment");
				frm.doc.unallocated_payment=frm.doc.total_gold_payment-frm.doc.allocated_payment;
				refresh_field("unallocated_payment");
			}
		});
	},
	qty:function(frm,cdt,cdn) {
		var d=locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn,"amount",d.rate*d.qty/100);
		calculate_table_stock(frm,cdt,cdn)
	},
	rate:function(frm,cdt,cdn) {
		var d=locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn,"amount",d.rate*d.qty/100);
		calculate_table_stock(frm,cdt,cdn)
	},
	stock_payment_remove:function(frm,cdt,cdn){
		calculate_table_stock(frm,cdt,cdn)
	}
	
});

