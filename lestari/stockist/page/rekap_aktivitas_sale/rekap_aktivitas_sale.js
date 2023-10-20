frappe.pages['rekap-aktivitas-sale'].on_page_load = function(wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Rekap Aktivitas Sales',
		single_column: true
	});

	wrapper.rekap_aktivitas_sales = new RekapAktivitasSales(wrapper);

}

RekapAktivitasSales = class RekapAktivitasSales {
	constructor(wrapper) {
		var me = this;
		// 0 setTimeout hack - this gives time for canvas to get width and height
		setTimeout(function() {
			me.setup(wrapper);
			// me.get_data();
		}, 0);
	}

	setup(wrapper) {
		var me = this;

		this.sales_field = wrapper.page.add_field({"fieldtype": "Link", "fieldname": "sales", "options": "Sales Partner",
			"label": __("Sales Partner"), "reqd": 1,
			change: function() {
				me.sales = this.value;
				// me.get_data();
			}
		}),

		this.pendamping_field = wrapper.page.add_field({"fieldtype": "Link", "fieldname": "pendamping", "options": "Sales Partner",
			"label": __("Pendamping"), "reqd": 0,
			change: function() {
				me.sales = this.value;
				// me.get_data();
			}
		}),

		this.bundle_field = wrapper.page.add_field({"fieldtype": "Link", "fieldname": "bundle", "options": "Sales Stock Bundle",
			"label": __("Bundle"), "reqd": 1,
			change: function() {
				me.sales = this.value;
				// me.get_data();
			}
		}),

		this.elements = {
			layout: $(wrapper).find(".layout-main"),
			from_date: wrapper.page.add_date(__("From Date")),
			to_date: wrapper.page.add_date(__("To Date")),
			// chart: wrapper.page.add_select(__("Chart"), [{value: 'sales_funnel', label:__("Sales Funnel")},
			// 	{value: 'sales_pipeline', label:__("Sales Pipeline")},
			// 	{value: 'opp_by_lead_source', label:__("Opportunities by lead source")}]),
			refresh_btn: wrapper.page.set_primary_action(__("Refresh"),
				function() { 
					// me.get_data(); 
				}, "fa fa-refresh"),
		};

		// this.elements.no_data = $('<div class="alert alert-warning">' + __("No Data") + '</div>')
		// 	.toggle(false)
		// 	.appendTo(this.elements.layout);

		// this.elements.funnel_wrapper = $('<div class="funnel-wrapper text-center"></div>')
		// 	.appendTo(this.elements.layout);

		// this.company = frappe.defaults.get_user_default('company');
		this.options = {
			from_date: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			to_date: frappe.datetime.get_today(),
			// chart: 'sales_funnel'
		};

		// set defaults and bind on change
		$.each(this.options, function(k, v) {
			if (['from_date', 'to_date'].includes(k)) {
				me.elements[k].val(frappe.datetime.str_to_user(v));
			} else {
				me.elements[k].val(v);
			}

			me.elements[k].on("change", function() {
				if (['from_date', 'to_date'].includes(k)) {
					me.options[k] = frappe.datetime.user_to_str($(this).val()) != 'Invalid date' ? frappe.datetime.user_to_str($(this).val()) : frappe.datetime.get_today();
				} else {
					// me.options.chart = $(this).val();
				}
				// me.get_data();
			});
		});

		// bind refresh
		this.elements.refresh_btn.on("click", function() {
			// me.get_data(this);
		});

		// bind resize
		$(window).resize(function() {
			// me.render();
		});
	} 
}
