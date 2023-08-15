frappe.pages['dev-extreme-report'].on_page_load = function(wrapper) {
	new DevExtreme(wrapper)
}
DevExtreme = Class.extend({
	init: function(wrapper){
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'DevExtreme',
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
		// var formattedNumber = DevExpress.localization.formatNumber(employees.message., {
		// 	style: "currency",
		// 	currency: "",
		// 	useGrouping: true
		//   });
		console.log(employees)		
		// DevExpress.localization.locale('id');
		$("#dataGrid").dxDataGrid({
			dataSource: employees.message,
        	keyExpr: 'name',
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
				dataField: 'no',
				width: 50,
				alignment: 'center',
				caption: 'No.',
			  }, 
			  {
				dataField: 'name',
				format: 'string',
				caption: 'Nomor PO'
			  },
			  {
				dataField: 'Transaction_Date',
				format: 'string',
				alignment: 'left',
				width: 110
			  },
			  {
				dataField: 'Schedule_Date',
				format: 'string',
				alignment: 'left',
				width: 110
			  },
			  {
				dataField: 'Status',
				format: 'string',
				alignment: 'left',
				width: 100
			  },
			  {
				dataField: 'Supplier',
				format: 'string',
			  },
			  {
				dataField: 'Mata_Uang',
				format: 'string',
				width: 70,
				alignment: 'center',
			  },
			  {
				dataField: 'Total',
				alignment: 'right',
				format: {
					type: 'fixedPoint',
					precision: 2,
					currency: '',
				  },
			  },
			  ],
			summary: {
				groupItems: [{
					column: 'no',
					summaryType: 'count',
					displayFormat: '{0} orders',
				  }, {
					column: 'Total',
					summaryType: 'sum',
					displayFormat: 'Total: {0}',
					showInGroupFooter: false,
					alignByColumn: true,
					valueFormat: {
						type: 'fixedPoint',
						precision: 2,
						thousandsSeparator: ',',
						currencySymbol: '',
						useGrouping: true,
					},
				  }],
			  },
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
	employees: function(){
		var data = frappe.call({
			method: 'lestari.lestari.page.dev_extreme_report.dev_extreme_report.contoh_report',
			args: {
				'doctype': 'Purchase Order',
			}
		});

		return data
	},

})