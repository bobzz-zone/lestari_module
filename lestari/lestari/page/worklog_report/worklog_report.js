frappe.pages['worklog-report'].on_page_load = function(wrapper) {
	new DevExtreme(wrapper)
}
DevExtreme = Class.extend({
	init: function(wrapper){
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'WorkLog',
			single_column: true
		});
		this.make()
	},
	// make page
	make: async function(){
		let me = $(this);
		DevExpress.localization.locale(navigator.language);
		let body = `<div class="dx-viewport">
			<div id="pivotgrid"></div>
		</div>`;
		$(frappe.render_template(body, this)).appendTo(this.page.main)
		var employees =  await this.employees()
		console.log(employees.data.worklog_percentages)		
		$('#pivotgrid').dxPivotGrid({
			allowSortingBySummary: true,
			allowFiltering: true,
			showBorders: true,
			showColumnGrandTotals: false,
			showRowGrandTotals: false,
			showRowTotals: false,
			showColumnTotals: false,
			fieldChooser: {
			  enabled: true,
			  height: 400,
			},
			dataSource: {
			  fields: [{
				caption: 'Employee Name',
				width: 120,
				dataField: 'employee_name',
				area: 'row',
				sortBySummaryField: 'Percent',
			  },{
				caption: 'SPKO',
				dataField: 'spko_utuh',
				width: 150,
				area: 'row',
			  },{
				caption: 'Kategori',
				dataField: 'kategori',
				width: 150,
				area: 'row',
			  },{
				caption: 'Sub Kategori',
				dataField: 'sub_kategori',
				width: 150,
				area: 'row',
			  }, {
				dataField: 'date',
				dataType: 'date',
				area: 'column',
			  }, {
				groupName: 'date',
				groupInterval: 'day',
				visible: true,
			  }, {
				caption: 'Percent',
				dataField: 'percent',
				dataType: 'number',
				summaryType: 'sum',
				area: 'data',
			  }],
			  store: employees.data,
			},
		  })
	},
	employees: async function(){
		var obj;
		
		await fetch('http://192.168.3.100:8282/api/v1/employee-statistics-with-range-devextreme?operation=Poles Manual&dateStart=2023-05-01&dateEnd=2023-07-30')
		.then(res => res.json())
		.then(data => {obj = data})
		return obj
	},

})