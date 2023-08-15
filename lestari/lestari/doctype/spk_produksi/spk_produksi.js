// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

frappe.ui.form.on("SPK Produksi", {
  refresh: function (frm) {
    // }
    // area: function (frm) {
    //   frm.clear_custom_buttons();
    frm.events.make_custom_buttons(frm);
  },
  make_custom_buttons: function (frm) {
    if (frm.doc.docstatus === 0) {
      // frm.add_custom_button(__("Sales Order"), () => frm.events.get_items_from_sales_order(frm), __("Get Items From"));
      frm.add_custom_button(__("Form Order"), () => frm.events.get_items_from_form_order(frm), __("Get Items From"));
    }
  },
  get_items_from_sales_order: function (frm) {
    erpnext.utils.map_current_doc({
      method: "lestari.lestari.doctype.spk_produksi.spk_produksi.make_material_request",
      source_doctype: "Sales Order",
      target: frm,
      setters: {
        customer: frm.doc.customer || undefined,
        delivery_date: undefined,
        currency: frm.doc.currency || undefined,
        order_type: frm.doc.order_type || undefined,
      },
      size: "extra-large",
      add_filters_group: 1,
      get_query_filters: {
        docstatus: 1,
        status: ["not in", ["Closed", "On Hold"]],
        per_delivered: ["<", 99.99],
        company: frm.doc.company,
      },
      allow_child_item_selection: true,
      child_fieldname: "items",
      child_columns: ["parent", "item_code", "qty", "qty_isi_pohon", "jumlah_pohon", "target_berat"],
    });
  },
  get_items_from_form_order: function (frm) {
    erpnext.utils.map_current_doc({
      // new frappe.ui.form.MultiSelectDialog({
      method: "lestari.lestari.doctype.spk_produksi.spk_produksi.get_items_from_form_order",
      source_doctype: "Form Order",
      // doctype: "Transfer Material",
      target: frm,
      setters: {
        type: undefined,
        kadar: undefined,
        kategori: undefined,
        sub_kategori: undefined,
      },
      add_filters_group: 1,
      size: "extra-large",
      get_query_filters: {
        docstatus: 1,
        // status: ["not in", ["Cancel"]],
        // company: frm.doc.company,
      },
      allow_child_item_selection: true,
      child_fieldname: "items_valid",
      child_columns: ["model", "item_name", "kadar", "kategori", "sub_kategori", "kategori_pohon", "qty_isi_pohon", "no_pohon", "qty"],
    });
    // const allowed_request_types = ["STA", "STO", "STP", "Customer"];
    // const depends_on_condition = "eval:doc.type==='Customer'";
    // const d = new frappe.ui.form.MultiSelectDialog({
    //   method: "lestari.lestari.doctype.spk_produksi.spk_produksi.get_items_from_form_order",
    //   source_doctype: "Form Order",
    //   target: frm,
    //   // date_field: "due_date",
    //   setters: [
    //     {
    //       fieldtype: "Select",
    //       label: __("Purpose"),
    //       options: allowed_request_types.join("\n"),
    //       fieldname: "type",
    //       default: "STA",
    //       mandatory: 1,
    //       change() {
    //         if (this.value === "Customer") {
    //           d.dialog.get_field("customer").set_focus();
    //         }
    //       },
    //     },
    //     {
    //       fieldtype: "Link",
    //       label: __("Customer"),
    //       options: "Customer",
    //       fieldname: "customer",
    //       depends_on: depends_on_condition,
    //       mandatory_depends_on: depends_on_condition,
    //     },
    //   ],
    //   get_query_filters: {
    //     docstatus: 1,
    //     type: ["in", allowed_request_types],
    //     // status: ["not in", ["Draft", "Submitted"]],
    //   },
    // });
    // const d = new frappe.ui.form.MultiSelectDialog({
    //   doctype: "Form Order",
    //   target: frm,
    //   method: "lestari.lestari.doctype.spk_produksi.spk_produksi.get_items_from_form_order",
    //   // source_doctype: "Form Order",
    //   setters: {
    //     // schedule_date: null,
    //     status: null,
    //   },
    //   add_filters_group: 1,
    //   size: "extra-large",
    //   // date_field: "transaction_date",
    //   allow_child_item_selection: 1,
    //   child_fieldname: "items", // child table fieldname, whose records will be shown &amp; can be filtered
    //   child_columns: ["model", "qty"], // child item columns to be displayed
    //   get_query() {
    //     return {
    //       filters: { docstatus: ["!=", 2] },
    //     };
    //   },
    //   action(selections, args) {
    //     console.log(args.filtered_children); // list of selected item names
    //   },
    // });
    // erpnext.utils.map_current_doc({
    //   method: "lestari.lestari.doctype.spk_produksi.spk_produksi.get_items_from_form_order",
    //   doctype: "Form Order",
    //   target: frm,
    //   setters: {
    //     type: frm.doc.type || undefined,
    //     customer: frm.doc.customer || undefined,
    //     // delivery_date: undefined,
    //     // currency: frm.doc.currency || undefined,
    //     // order_type: frm.doc.order_type || undefined,
    //   },
    //   size: "extra-large",
    //   add_filters_group: 1,
    //   get_query_filters: {
    //     docstatus: 1,
    //     // status: ["not in", ["Closed", "On Hold"]],
    //     // per_delivered: ["<", 99.99],
    //     company: frm.doc.company,
    //   },
    //   allow_child_item_selection: true,
    //   child_fieldname: "items",
    //   child_columns: ["parent", "model", "qty", "qty_isi_pohon"],
    // });
    // return d;
  },
  //   get_items_from_material_request: function (frm) {
  //     erpnext.utils.map_current_doc({
  //       method: "lestari.lestari.doctype.spk_produksi.spk_produksi.get_material_request",
  //       source_doctype: "Material Request",
  //       target: frm,
  //       setters: {
  //         transaction_date: undefined,
  //         schedule_date: undefined,
  //         status: undefined,
  //       },
  //       get_query_filters: {
  //         docstatus: 1,
  //         status: ["!=", "Stopped"],
  //         per_ordered: ["<", 100],
  //         company: me.frm.doc.company,
  //       },
  //     });
  //   },
});
