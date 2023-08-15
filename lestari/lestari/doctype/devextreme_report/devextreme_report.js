// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt
frappe.provide("frappe.views");
frappe.ui.form.on('DevExtreme Report', {
  onload: function (frm) {
    frm.tab_report = new frappe.views.TabReport({ frm: frm });
    frm.tab_report.show();
  },

  refresh: function (frm) {
    frm.tab_report.refresh();
  },
});

frappe.views.TabReport = class TabReport {
  constructor(opts) {
    Object.assign(this, opts);
  }

  show() {
    frappe.run_serially([() => this.init()]);
  }

  init() {
    if (this.init_promise) return this.init_promise;

    let tasks = [this.setup_defaults].map((fn) => fn.bind(this));

    this.init_promise = frappe.run_serially(tasks);
    return this.init_promise;
  }

  setup_defaults() {
    // set full-width
    this.frm.$wrapper.find(".container.page-body").addClass("col-md-12");

    // create container for tabulator table
    $("<div id='tab-report' class='table-bordered'></div>").appendTo(
      this.frm.fields_dict["report_html"].$wrapper
    );

    this.report_name = this.frm.doc.report_name;
    this.report_settings = {};
  }

  refresh() {
    return new Promise((resolve) => {
      this.last_ajax = frappe.call({
        method: "frappe.desk.query_report.run",
        type: "GET",
        args: {
          report_name: this.report_name,
        },
        callback: resolve,
        always: () => this.frm.page.btn_secondary.prop("disabled", false),
      });
    }).then((r) => {
      let data = r.message;
      this.execution_time = data.execution_time || 0.1;
      if (data.result && data.result.length) {
        this.prepare_report_data(data);
        this.render_datatable();
      } else {
        this.data = { result: [], columns: [] };
      }
    });
  }

  prepare_report_data(data) {
    this.data = data;

    // prepare columns
    this.data.columns.forEach((t) => {
      t.title = t.label;
      t.field = t.fieldname;
    });
  }

  render_datatable() {
    if (this.tabulator) {
      $("#tab-report").tabulator("destroy");
    }
    let opts = this.report_settings.opts || {};
    Object.assign(opts, { height: `${this.frm.doc.height}px` });
    this.tabulator = new Tabulator("#tab-report", opts);
    this.tabulator.setColumns(this.data.columns);
    this.tabulator.setData(this.data.result);
  }
};
