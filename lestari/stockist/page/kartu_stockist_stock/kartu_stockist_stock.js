frappe.pages['kartu-stockist-stock'].on_page_load = function(wrapper) {
	var tema = frappe.boot.user.desk_theme
	if(tema == "Dark"){
		frappe.require('/assets/lestari/css/dx.dark.css',function() {
			new DevExtreme(wrapper)
		})
	}else{
		frappe.require('/assets/lestari/css/dx.light.css',function() {
			new DevExtreme(wrapper)
		})
	}
	DevExpress.viz.refreshTheme();
frappe.breadcrumbs.add("Stockist");
}
DevExtreme = Class.extend({
	init: function(wrapper){
		var me = this
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'Kartu Stock Stockist',
			single_column: true
		});
		this.page.set_secondary_action('Refresh', () => me.make(), { icon: 'refresh', size: 'sm'})
		this.posting_date = ""
		// this.sales = ""
		this.bundle = ""
		this.kadar = ""
		this.page.add_field({"fieldtype": "DateRange", "fieldname": "posting_date","default": ['2023-10-31', frappe.datetime.now_date()],
			"label": __("Posting Date"), "reqd": 1,
			change: function() {
				me.posting_date = this.value;
				me.make()
			}
		}),
		// this.page.add_field({"fieldtype": "Link", "fieldname": "sales","options": "Sales Partner",
		// 	"label": __("Sales"), "reqd": 0,
		// 	change: function() {
		// 		me.sales = this.value;
		// 		me.make()
		// 	}
		// }),
		this.page.add_field({"fieldtype": "Link", "fieldname": "bundle","options": "Sales Stock Bundle",
			"label": __("Bundle"), "reqd": 0,
			change: function() {
				me.bundle = this.value;
				me.make()
			}
		}),
		this.page.add_field({"fieldtype": "Link", "fieldname": "kadar","options": "Data Logam",
			"label": __("Kadar"), "reqd": 0,
			change: function() {
				me.kadar = this.value;
				me.make()
			}
		}),
		this.make()
		// frappe.msgprint('Data Terload')
	},
	// make page
	make: async function(){
		let me = this
		console.log(this.page.wrapper.attr('id'))
		// DevExpress.localization.locale(navigator.language);
		let body = `<div class="dx-viewport">
			<div id="dataGrid_`+this.page.wrapper.attr('id')+`"></div>
		</div>`;
		$(frappe.render_template(body, this)).appendTo(this.page.main)
		var infoproses = await this.infoproses()
		$("#dataGrid_"+this.page.wrapper.attr('id')).dxDataGrid({
			dataSource: infoproses.message,
			width: '100%',
        	keyExpr: 'voucher',
			// height: 650,
			// width: '100%',
			columnAutoWidth: true,
			allowColumnReordering: false,
			// showBorders: true,
			// hoverStateEnabled:true,
			// preloadEnabled:true,
			// renderAsync:true,
			// filterBuilder: true,
			// summary: {
			// 	groupItems: [{
			// 		summaryType: "count"
			// 	}]
			// },
			// columnFixing: {
			// 	enabled: true,
			// 	fixedPosition: "top"
			// },
			// scrolling: {
			// 	mode: 'virtual',
			// 	rowRenderingMode: 'virtual',
			// },
			// paging: {
			// 	enabled: false
			// },
			// filterRow: {
			// 	visible: true
			// },
			// headerFilter: {
			// 	visible: true
			// },
			// filterRow: {
			// 	visible: true
			// },
			// grouping: {  
			// 	autoExpandAll: false  
			// },  
			// groupPanel: {
			// 	visible: true
			// },
			// searchPanel: {
			// 	visible: true
			// },
			// focusedRowEnabled: false,
			// export: {
			// 	enabled: true
			// },
			showBorders: true,
			rowAlternationEnabled: true,
			allowColumnReordering: true,
			allowColumnResizing: true,
			columnAutoWidth: true,
			scrolling: {
				columnRenderingMode: 'virtual',
			  },
			groupPanel: {
				visible: true,
			},
			grouping:{
				autoExpandAll: false,
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
			filterRow: { visible: true, applyFilter: 'auto'},
			filterPanel: { visible: true },
        	searchPanel: { visible: true }, 
			columnChooser: { enabled: true },
			headerFilter: {
				visible: true,
			  },
			export: {
				enabled: true
			},
			// columns:[
			// {
			// 	dataField: 'no',
			// 	width: 50,
			// 	alignment: 'center',
			// 	caption: 'No.'
			// },
			// {
		// 		dataField: 'customer',
		// 		width: 120,
		// 		alignment: 'center',
		// 		caption: 'Customer',
		// 		groupIndex: 0
		// 	},
		// {
		// 		dataField: 'subcustomer',
		// 		width: 120,
		// 		alignment: 'center',
		// 		caption: 'SubCustomer',
				
		// 	},
		// {
		// 		dataField: 'no_nota',
		// 		width: 100,
		// 		alignment: 'center',
		// 		caption: 'No Nota',
		// 	},
			// {
			// 	dataField: 'posting_date',
			// 	width: 100,
			// 	alignment: 'center',
			// 	sort: 'ASC',
			// 	caption: 'Tanggal Posting',
			// },
			// {
			// 	dataField: 'proses',
			// 	width: 120,
			// 	alignment: 'center',
			// 	caption: 'Proses',
			// },
			// {
			// 	dataField: 'voucher_no',
			// 	width: 150,
			// 	alignment: 'center',
			// 	caption: 'Voucher No',
			// },
			// {
			// 	dataField: 'kadar',
			// 	width: 150,
			// 	alignment: 'center',
			// 	caption: 'Kadar',
			// 	groupIndex: 0
			// },
			// {
			// 	dataField: 'qty_in',
			// 	width: 150,
			// 	alignment: 'center',
			// 	caption: 'Masuk',
			// },
			// {
			// 	dataField: 'qty_out',
			// 	width: 150,
			// 	alignment: 'center',
			// 	caption: 'Keluar',
			// },
			// {
			// 	dataField: 'qty_balance',
			// 	width: 150,
			// 	alignment: 'center',
			// 	caption: 'Sisa',
			// },
		// {
		// 		dataField: 'berat_kotor',
		// 		width: 150,
		// 		dataType: 'decimal',
		// 		alignment: 'right',
		// 		caption: 'Berah Kotor',
		// 	},{
		// 		dataField: 'berat_bersih',
		// 		width: 150,
		// 		dataType: 'decimal',
		// 		alignment: 'right',
		// 		caption: 'Berat Bersih',
		// 	},{
		// 		dataField: 'satuan',
		// 		width: 80,
		// 		dataType: 'decimal',
		// 		alignment: 'right',
		// 		caption: 'Satuan',
		// 	},{
		// 		dataField: 'tutupan',
		// 		alignment: 'right',
		// 		width: 150,
		// 		format: {
		// 			type: 'fixedPoint',
		// 			precision: 2,
		// 			currency: '',
		// 		  },
		// 		caption: 'Tutupan'
		// 	},{
		// 		dataField: 'tax_status',
		// 		width: 100,
		// 		alignment: 'center',
		// 		caption: 'Tax',
		// 	},{
		// 		dataField: 'ppn',
		// 		alignment: 'right',
		// 		width: 150,
		// 		format: {
		// 			type: 'fixedPoint',
		// 			precision: 2,
		// 			currency: '',
		// 		  },
		// 		caption: 'PPN'
		// 	},{
		// 		dataField: 'pph',
		// 		alignment: 'right',
		// 		width: 150,
		// 		format: {
		// 			type: 'fixedPoint',
		// 			precision: 2,
		// 			currency: '',
		// 		  },
		// 		caption: 'PPH'
		// 	},{
		// 		dataField: 'user',
		// 		width: 150,
		// 		alignment: 'center',
		// 		caption: 'User',
		// 	}	
		// ],
		// summary:{
		// 	totalItems: [
		// 		{
		// 			column: 'berat_kotor',
		// 			summaryType: 'sum',
		// 			displayFormat: '{0}',
		// 			showInGroupFooter: false,
		// 			alignByColumn: true,
		// 			valueFormat: {
		// 				type: 'fixedPoint',
		// 				precision: 2,
		// 				thousandsSeparator: ',',
		// 				currencySymbol: '',
		// 				useGrouping: true,
		// 			},
		// 	},{
		// 		column: 'berat_bersih',
		// 		summaryType: 'sum',
		// 		displayFormat: '{0}',
		// 		showInGroupFooter: false,
		// 		alignByColumn: true,
		// 		valueFormat: {
		// 			type: 'fixedPoint',
		// 			precision: 2,
		// 			thousandsSeparator: ',',
		// 			currencySymbol: '',
		// 			useGrouping: true,
		// 		},
		// },
		// 	],
			// groupItems: [
			// 	{
			// 		column: 'no',
			// 		summaryType: 'count',
			// 		displayFormat: '{0} Nota',
			// 	},
			// 	{
			// 		column: 'berat_kotor',
			// 		summaryType: 'sum',
			// 		displayFormat: '{0}',
			// 		showInGroupFooter: true,
			// 		alignByColumn: true,
			// 		valueFormat: {
			// 			type: 'fixedPoint',
			// 			precision: 2,
			// 			thousandsSeparator: ',',
			// 			currencySymbol: '',
			// 			useGrouping: true,
			// 		},
			// 	},
			// 	{
			// 		column: 'berat_kotor',
			// 		summaryType: 'sum',
			// 		displayFormat: '{0}',
			// 		showInGroupFooter: false,
			// 		alignByColumn: true,
			// 		valueFormat: {
			// 			type: 'fixedPoint',
			// 			precision: 2,
			// 			thousandsSeparator: ',',
			// 			currencySymbol: '',
			// 			useGrouping: true,
			// 		},
			// 	},
			// 	{
			// 		column: 'berat_bersih',
			// 		summaryType: 'sum',
			// 		displayFormat: '{0}',
			// 		showInGroupFooter: false,
			// 		alignByColumn: true,
			// 		valueFormat: {
			// 			type: 'fixedPoint',
			// 			precision: 2,
			// 			thousandsSeparator: ',',
			// 			currencySymbol: '',
			// 			useGrouping: true,
			// 		},
			// 	},
			// 	{
			// 		column: 'berat_bersih',
			// 		summaryType: 'sum',
			// 		displayFormat: '{0}',
			// 		showInGroupFooter: true,
			// 		alignByColumn: true,
			// 		valueFormat: {
			// 			type: 'fixedPoint',
			// 			precision: 2,
			// 			thousandsSeparator: ',',
			// 			currencySymbol: '',
			// 			useGrouping: true,
			// 		},
			// 	}
			// ]
		// },
			onExporting(e) {
				const workbook = new ExcelJS.Workbook();
				const worksheet = workbook.addWorksheet('infoproses');
		  
				DevExpress.excelExporter.exportDataGrid({
				  component: e.component,
				  worksheet,
				  autoFilterEnabled: true,
				}).then(() => {
				  workbook.xlsx.writeBuffer().then((buffer) => {
					saveAs(new Blob([buffer], { type: 'application/octet-stream' }), 'Pembayaran.xlsx');
				  });
				});
				e.cancel = true;
			  }
		});
	},
	infoproses: function(){
		var me = this
		var data = frappe.call({
			method: 'lestari.stockist.page.kartu_stockist_stock.kartu_stockist_stock.contoh_report',
			args: {
				'doctype': 'Transfer Barang Jadi',
				'posting_date': me.posting_date,
				// 'sales': me.sales,
				'bundle': me.bundle,
				'kadar': me.kadar,
			}
		});

		return data
	},

})
 