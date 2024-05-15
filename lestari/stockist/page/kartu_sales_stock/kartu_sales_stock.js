frappe.pages['kartu-sales-stock'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Kartu Stock Sales',
		single_column: true
	});
}