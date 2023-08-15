frappe.pages['laravel-report'].on_page_load = function(wrapper) {
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
			<div id="dataGrid"></div>
		</div>`;
		$(frappe.render_template(body, this)).appendTo(this.page.main)
		var employees =  await this.employees()
		console.log(employees)		
		$("#dataGrid").dxDataGrid({
			dataSource: employees.data.worklog_percentages,
        	keyExpr: 'index',
			showBorders: true,
			allowColumnReordering: true,
			allowColumnResizing: true,
			groupPanel: {
				visible: true,
			},
			filterRow: { visible: true },
        	searchPanel: { visible: true }, 
			columnChooser: { enabled: true },
			export: {
				enabled: true
			},
			columns: [{
				dataField: 'index',
				width: 50,
				alignment: 'center',
				caption: 'No.',
			  }, 
			  {
				dataField: 'date',
				format: 'string',
				alignment: 'left',
				width: 110
			  },
			  {
				dataField: 'worklog_percent',
				alignment: 'right',
				format: {
					type: 'fixedPoint',
					precision: 2,
					currency: '',
				  },
			  },
			  ],
			// summary: {
			// 	groupItems: [{
			// 		column: 'no',
			// 		summaryType: 'count',
			// 		displayFormat: '{0} orders',
			// 	  }, {
			// 		column: 'Total',
			// 		summaryType: 'sum',
			// 		displayFormat: 'Total: {0}',
			// 		showInGroupFooter: false,
			// 		alignByColumn: true,
			// 		valueFormat: {
			// 			type: 'fixedPoint',
			// 			precision: 2,
			// 			thousandsSeparator: ',',
			// 			currencySymbol: '',
			// 			useGrouping: true,
			// 		},
			// 	  }],
			//   },
			onExporting(e) {
				const workbook = new ExcelJS.Workbook();
				const worksheet = workbook.addWorksheet('Employees');
		  
				DevExpress.excelExporter.exportDataGrid({
				  component: e.component,
				  worksheet,
				  autoFilterEnabled: true,
				}).then(() => {
				  workbook.xlsx.writeBuffer().then((buffer) => {
					saveAs(new Blob([buffer], { type: 'application/octet-stream' }), 'PurchaseOrder.xlsx');
				  });
				});
				e.cancel = true;
			  }
		});
	},
	employees: async function(){
		var obj;
		
		await fetch('http://192.168.3.100:8282/api/v1/employee-statistics-with-range?idEmployee=1793&operation=Poles%20Manual&dateStart=2023-07-01&dateEnd=2023-07-30')
		.then(res => res.json())
		.then(data => {obj = data})
		return obj
	},

})