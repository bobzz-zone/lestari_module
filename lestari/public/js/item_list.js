frappe.listview_settings["Item"] = {
  onload: function (listview) {
    console.log(listview);
    listview.page.add_action_item(__("Buat Form Order"), function (list) {
      //   let d = new frappe.ui.Dialog({
      //     title: 'Gambar Product',
      //     size:'extra-large',
      //     fields: [
      //         {
      //             label: 'Model',
      //             fieldname: 'model',
      //             fieldtype: 'Data',
      //             default: i.model,
      //             readonly: 1
      //         },
      //         {
      //             label: 'Gambar Product',
      //             fieldname: 'gambar_product',
      //             fieldtype: 'HTML',

      //             // default: '<img id="gambar-produk" src="/files/ATK.210.06K.Y.0.0.0.00.000.jpg" width="450px">'
      //         }
      //     ],
      //     primary_action_label: 'Submit',
      //     primary_action(values) {
      //         console.log(values);
      //         d.hide();
      //     }
      // });
      // d.fields_dict.gambar_product.$wrapper.html('<img id="gambar-produk" src="'+i.image+'" width="450px">');
      // d.show();
      // }
      frappe.call({
        method: "lestari.testapi.item_form_order",
        args: {
          item: listview.get_checked_items(true),
        },
        callback: function (r) {
          if (!r.exc) {
            console.log(r);
            var doclist = frappe.model.sync(r.message);
            doctype = doclist[0].doctype.replace(" ", "-").toLowerCase();
            path = window.location.hostname;
            window.open("../../" + doctype + "/" + doclist[0].name, "_blank");
          }
        },
      });
    });
  },
  //   add_fields: ["item_name", "stock_uom", "item_group", "image", "variant_of", "has_variants", "end_of_life", "disabled"],
  //   filters: [["disabled", "=", "0"]],
  //   get_indicator: function (doc) {
  //     if (doc.disabled) {
  //       return [__("Disabled"), "grey", "disabled,=,Yes"];
  //     } else if (doc.end_of_life && doc.end_of_life < frappe.datetime.get_today()) {
  //       return [__("Expired"), "grey", "end_of_life,<,Today"];
  //     } else if (doc.has_variants) {
  //       return [__("Template"), "orange", "has_variants,=,Yes"];
  //     } else if (doc.variant_of) {
  //       return [__("Variant"), "green", "variant_of,=," + doc.variant_of];
  //     }
  //   },
  //   reports: [
  //     {
  //       name: "Stock Summary",
  //       report_type: "Page",
  //       route: "stock-balance",
  //     },
  //     {
  //       name: "Stock Ledger",
  //       report_type: "Script Report",
  //     },
  //     {
  //       name: "Stock Balance",
  //       report_type: "Script Report",
  //     },
  //     {
  //       name: "Stock Projected Qty",
  //       report_type: "Script Report",
  //     },
  //   ],
};

// frappe.help.youtube_id["Item"] = "qXaEwld4_Ps";
