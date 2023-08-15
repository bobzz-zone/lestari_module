frappe.pages['tf-salesman-dvx-repo'].on_page_load = function(wrapper) {
	new DevExtreme(wrapper)
}
DevExtreme = Class.extend({
	init: function(wrapper){
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'Transfer Salesman',
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
			columnAutoWidth: true,
			scrolling: {
				columnRenderingMode: 'virtual',
			  },
			groupPanel: {
				visible: true,
			},
			paging: {
				pageSize: 25,
			},
			pager: {
			visible: true,
			allowedPageSizes: [25, 50, 100, 'all'],
			showPageSizeSelector: true,
			showInfo: true,
			showNavigationButtons: true,
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
			  },{
				dataField: 'name',
				format: 'string',
				alignment: 'left',
				width: 110,
				caption: 'No Doc'			   
			  },{
				dataField: 'posting_date',
				format: 'string',
				alignment: 'left',
				width: 110,
				caption: 'Posting Date'
			  },			   
			  {
				dataField: 'bundle',
				format: 'string',
				width: 150,
				caption: 'Bundle'
			  },
			  {
				dataField: 'type',
				format: 'string',
				width: 150,
				caption: 'Type'
			  },
			  {
				dataField: 'nama_stokist',
				format: 'string',
				width: 150,
				caption: 'Stokist'
			  },
			  {
				dataField: 'sales',
				format: 'string',
				width: 100,
				caption: 'Sales'
			  },
			  {
				dataField: 'warehouse',
				format: 'string',
				width: 100,
				caption: 'Warehouse'
			  },
			  {
				dataField: 'kategori',
				format: 'string',
				width: 100,
				caption: 'Kategori'
			  },
			  {
				dataField: 'sub_kategori',
				format: 'string',
				width: 100,
				caption: 'Sub Kategori'
			  },
			  {
				dataField: 'kadar',
				format: 'string',
				width: 100,
				caption: 'Kadar'
			  },
			  {
				dataField: 'qty',
				format: 'decimal',
				caption: 'Per Qty'
			  },
			  ],
			summary: {
				groupItems: [{
					column: 'no',
					summaryType: 'count',
					displayFormat: '{0} orders',
				  }, {
					column: 'qty',
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
					saveAs(new Blob([buffer], { type: 'application/octet-stream' }), 'TransferSalesman.xlsx');
				  });
				});
				e.cancel = true;
			  }
		});
	},
	employees: function(){
		var data = frappe.call({
			method: 'lestari.lestari.page.tf_salesman_dvx_repo.tf_salesman_dvx_repo.contoh_report',
			args: {
				'doctype': 'Purchase Order',
			}
		});

		return data
	},

})