// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Form Order", {
  setup: function (frm) {
    frappe.db.get_value("Employee", { user_id: frappe.session.user }, "name").then(function (responseJSON) {
      cur_frm.set_value("pic", responseJSON.message.name);
      cur_frm.refresh_field("pic");
    });
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
    // if (cur_frm.doc.items != null) {
    //   cur_frm.set_df_property("kadar", "read_only", 1);
    // } else {
    //   cur_frm.set_df_property("kadar", "read_only", 0);
    // }
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
    addnew.remark = frm.doc.remark;
    frm.refresh_field("items");
    cur_frm.set_value("sku", "");
    cur_frm.set_value("qty", "");
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
  kategori: function (frm) {
    frm.set_query("sub_kategori", function () {
      return {
        filters: {
          parent_item_group: cur_frm.doc.kategori,
        },
      };
    });
  },
});
frappe.ui.form.on("Form Order Item", {
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
  },
});
