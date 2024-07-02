frappe.provide("lestari.ui.form");

lestari.ui.form.MultiSelectDialog = frappe.ui.form.MultiSelectDialog
$.extend(lestari.ui.form.MultiSelectDialog.prototype, {
    async perform_search(args) {
		const res = await frappe.call({
			type: "GET",
			method: 'frappe.desk.search.search_widget',
			no_spinner: true,
			args: args,
		});
		const more = res.values.length && res.values.length > this.page_length ? 1 : 0;

		return [res, more];
	},

    async get_child_result() {
		let filters = [["parentfield", "=", this.child_fieldname]];

		await this.add_parent_filters(filters);
		this.add_custom_child_filters(filters);

		return frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: this.child_doctype,
				filters: filters,
				fields: ['name', 'parent', ...this.child_columns],
				parent: this.doctype,
				limit_page_length: this.child_page_length + 5,
				order_by: 'parent'
			}
		});
	}
})