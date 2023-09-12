  // Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

var list_kat;
async function getListAndSetQuery(frm) {
list_kat = [];
await frappe.db.get_list('Item Group', {
			filters: {
				parent_item_group: 'Products'
			}
		}).then(records => {
			for(var i = 0; i< records.length; i++){
				list_kat.push(records[i].name)
			}
			list_kat.sort()
		})
		frm.set_query("sub_kategori", "items",function () {
			return {
				"filters": [
					["Item Group", "parent_item_group", "in", list_kat],
				],
				"order_by":['name asc']
			};
		});
		frm.set_query("sub_kategori",function () {
			return {
				"filters": [
					["Item Group", "parent_item_group", "in", list_kat],
				],
				"order_by":['name asc']
			};
		});
	}

frappe.ui.form.on("Form Order", {
  setup: function (frm) {
    if(cur_frm.doc.docstatus === 0){
    frappe.db.get_value("Employee", { user_id: frappe.session.user }, "name").then(function (responseJSON) {
      cur_frm.set_value("pic", responseJSON.message.name);
      cur_frm.refresh_field("pic");
    });
  }
    $(":button[data-fieldname='reset']").css("background-color", "red");
    $(":button[data-fieldname='reset']").css("color", "white");
  },
  before_save: function (frm) {
    cur_frm.set_value("sku", "");
    cur_frm.set_value("qty_isi_pohon", "");
    cur_frm.set_value("qty", "");
    cur_frm.set_value("remark", "");
  },
  refresh: function (frm) {
    getListAndSetQuery(frm);
    if(cur_frm.doc.docstatus === 0){
      if(cur_frm.doc.no_fo == null || cur_frm.doc.no_fo == ""){
        // frappe.msgprint('test')
        frm.clear_table("items");
        frm.refresh_fields();
      }
    }
    // var me = this;
    // if (cur_frm.doc.items != null) {
    //   cur_frm.set_df_property("kadar", "read_only", 1);
    // } else {
    //   cur_frm.set_df_property("kadar", "read_only", 0);
    // }
    // frm.events.make_custom_buttons(frm);
    if (frm.doc.docstatus === 1) {
      frm.add_custom_button(__("Buat Baru"), () => {
        frappe.model.open_mapped_doc({
          method: "lestari.gold_selling.doctype.form_order.form_order.buat_baru",
          frm: cur_frm
        })
      });
    }
    $(":button[data-fieldname='reset']").css("background-color", "red");
    $(":button[data-fieldname='reset']").css("color", "white");
    frm.set_query("kategori", function () {
      return {
        filters: {
          parent_item_group: "Products",
        },
      };
    });
    frm.set_query("sku", function () {
      return {
        filters: {
          item_group: cur_frm.doc.sub_kategori,
          kadar: cur_frm.doc.kadar,
        },
      };
    });
  },
  type: function (frm){
    cur_frm.set_value("type",cur_frm.doc.type.toUpperCase())
    cur_frm.refresh_field("type")
  },
  make_custom_buttons: function (frm) {
    if (frm.doc.docstatus === 1) {
      frm.add_custom_button(__("Buat Baru"), () => {me.buat_baru()});
    }
  },
  reset: function (frm) {
    cur_frm.set_value("sku", "");
    cur_frm.set_value("qty", "");
    cur_frm.set_value("remark", "");
  },
  pilih: function (frm) {
    var addnew = frappe.model.add_child(cur_frm.doc, "Form Order Item", "items");
    addnew.model = frm.doc.sku;
    addnew.item_name = frm.doc.item_name;
    addnew.kadar = frm.doc.kadar;
    addnew.image = frm.doc.image;
    addnew.qty_isi_pohon = frm.doc.qty_isi_pohon;
    addnew.sub_kategori = frm.doc.sub_kategori;
    addnew.kategori = frm.doc.kategori;
    addnew.qty = frm.doc.qty;
    addnew.berat = frm.doc.berat;
    addnew.total_berat = frm.doc.berat * frm.doc.qty;
    addnew.remark = frm.doc.remark;
    hitung_items(frm)
    frm.refresh_field("items");
    // frm.trigger("items_add")
    // frm.script_manager.trigger(this.df.fieldname + "_add", d.doctype, d.name);
    cur_frm.set_value("sku", "");
    cur_frm.set_value("qty", "");
    cur_frm.set_value("berat", "");
    cur_frm.set_value("remark", "");
  },
  item_code: function (frm) {
    // frappe.msgprint(cur_frm.doc.image);
    var gambar = cur_frm.doc.image;
    $("#gambar-produk").attr("src", gambar);
  },
  //   item_name: function (frm) {
  //     frappe.msgprint(cur_frm.doc.image);
  //   },
  // kategori: function (frm) {
  //   frm.set_query("sub_kategori", function () {
  //     return {
  //       filters: {
  //         parent_item_group: cur_frm.doc.kategori,
  //       },
  //     };
  //   });
  // },
  
});

function hitung_items(frm){
  // console.log(frm)
  var total_berat = 0
  var total_qty = 0
  $.each(frm.doc.items, (i,e)=>{
    total_berat += e.total_berat
    total_qty += e.qty
  })
  frm.set_value("total_berat", total_berat);
  frm.set_value("total_qty", total_qty);
  frm.refresh_field('total_berat')
  frm.refresh_field('total_qty')
}

frappe.ui.form.on("Form Order Item", {
  items_remove: function (frm,cdt,cdn){
    hitung_items(frm)
  },
  view: function (frm, cdt, cdn) {
    var i = locals[cdt][cdn];
    let d = new frappe.ui.Dialog({
      title: "Gambar Product",
      size: "extra-large",
      fields: [
        {
          label: "Model",
          fieldname: "model",
          fieldtype: "Data",
          default: i.model,
          readonly: 1,
        },
        {
          label: "Gambar Product",
          fieldname: "gambar_product",
          fieldtype: "HTML",

          // default: '<img id="gambar-produk" src="/files/ATK.210.06K.Y.0.0.0.00.000.jpg" width="450px">'
        },
      ],
      primary_action_label: "Submit",
      primary_action(values) {
        console.log(values);
        d.hide();
      },
    });
    d.fields_dict.gambar_product.$wrapper.html('<img id="gambar-produk" src="' + i.image + '" width="450px">');
    d.show();
  }
});
