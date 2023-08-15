// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on("Work Order Lilin", {
  refresh(frm) {
    // your code here
    frm.set_query("pohon_id", function () {
      return {
        filters: {
          warehouse: "Lilin - L",
          docstatus: 1,
        },
      };
    }),
      frm.set_query("nomor_base_karet", function () {
        // if (!cur_frm.doc.ukuran_base_karet) {
        // frappe.throw("Silakan Pilih Ukuran Base Karet Terlebih dahulu!");
        // } else {
        return {
          // filters: {
          //   item_code: cur_frm.doc.ukuran_base_karet,
          // },
          filters: [["item_code", "IN", ["MT-Base Karet Besar", "MT-Base Karet Sedang", "MT-Base Karet Kecil"]]],
        };
        // }
      }),
      frm.set_query("mul_karet_id", "tabel_pohon", function (doc, cdn, cdt) {
        var d = locals[cdn][cdt];
        return {
          filters: {
            item_code: d.mul_karet,
          },
        };
      });
  },
  pohon_id: function (frm) {
    frm.call("create_wo_lilin", {});
  },
  set_sprue: function (frm) {
    var item_code = frappe.get_doc("Data Set Sprue", cur_frm.ukuran_base_karet);
    console.log(item_code);
    frm.set_query("nomor_base_karet", function () {
      return {
        filters: {
          item_code: cur_frm.doc.ukuran_base_karet,
        },
      };
    });
  },
});
