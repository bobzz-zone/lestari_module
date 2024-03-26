frappe.pages['kartu-piutang-custom'].on_page_load = function(wrapper) {
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
	frappe.breadcrumbs.add("Gold Selling");
}
DevExtreme = Class.extend({
	init: function(wrapper){
		var me = this
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'Kartu Piutang Customer',
			single_column: true
		});
		this.page.set_secondary_action('Refresh', () => me.make(), { icon: 'refresh', size: 'sm'})
		this.posting_date = ""
		this.page.add_field({"fieldtype": "DateRange", "fieldname": "posting_date","default": ['2023-10-31', frappe.datetime.now_date()],
			"label": __("Posting Date"), "reqd": 1,
			change: function() {
				me.posting_date = this.value;
				me.make()
			}
		}),
		this.make()
	},
	// make page
	make: async function(){
		let me = this
		console.log(this.page.wrapper.attr('id'))
		// DevExpress.localization.locale(navigator.language);
		let body = `<div class="dx-viewport">
			<div id="dataGrid_`+this.page.wrapper.attr('id')+`"></div>
		</div>`;
		const formatDate = new Intl.DateTimeFormat(['ban', 'id']).format;
		$(frappe.render_template(body, this)).appendTo(this.page.main)
		var piutang =  await this.piutang()
		$("#dataGrid_"+this.page.wrapper.attr('id')).dxDataGrid({
			dataSource: piutang.message,
        	keyExpr: 'voucher_no',
			// dataRowTemplate(container, item) {
			// 	const { data } = item;
			// 	let url = window.location.origin+'/app';
			// 	var doctype = data.voucher_type.replace(/\s+/g, '-').toLowerCase();;
			// 	const markup = '<tr class=\'main-row\'>'
			// 		+ `<td>${data.no}</td>`
			// 		+ `<td>${data.customer}</td>`
			// 		+ `<td><button type="button" class="btn btn-primary">
			// 		<a href='${url}/${doctype}/${data.voucher_no}' target="_blank" >`
			// 		+ `${data.voucher_no}</a></button></td>` 	
			// 		+ `<td>${data.voucher_type}</td>`
			// 		+ `<td>${data.bundle}</td>`
			// 		+ `<td>${data.posting_date}</td>`
			// 		+ `<td>${data.tutupan}</td>`
			// 		+ `<td>${data.outstanding}</td>`
			// 		+ `<td>${data.cpr}</td>`
			// 		+ `<td>${data.deposit_gold}</td>`
			// 		+ `<td>${data.deposit_idr}</td>`
			// 		+ `<td>${data.summarize}</td>`
			// 	+ '</tr>';
			// 	container.append(markup);
			//   },
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
			columns: [{
				dataField: 'no',
				width: 50,
				alignment: 'center',
				caption: 'No.',
			  },
			  {
				dataField: 'voucher_no',
				format: 'string',
				width: 150,
				caption: 'Voucher No',
				cellTemplate(container, options) {
					// console.log(options)
					const { data } = options;
					let url = window.location.origin+'/app';
					var doctype = data.voucher_type.replace(/\s+/g, '-').toLowerCase();
					$('<a href='+url+'/'+doctype+'/'+options.value+' class="btn btn-primary btn-block '+doctype+'" target="_blank">'+options.value+'</a>')
					//   .append($('<a>', { href: , text: options.value, target:'_blank' }))
					  .appendTo(container);
				  },
			  },
			  {
				dataField: 'voucher_type',
				format: 'string',
				width: 150,
				caption: 'Voucher Type'
			  },
			  {
				  dataField: 'customer',
				  format: 'string',
				  width: 150,
				  caption: 'Customer',
				  groupIndex: 0
				},
				{
					dataField: 'bundle',
					format: 'string',
					width: 150,
					caption: 'Bundle',
					
				  },
			  {
				dataField: 'posting_date',
				format: 'date',
				caption: 'Posting Date',
			  },
			  {
				dataField: 'tutupan',
				format: 'decimal',
				caption: 'Tutupan'
			  },
			  {
				dataField: 'outstanding',
				alignment: 'right',
				format: {
					type: 'fixedPoint',
					precision: 3,
					currency: '',
				  },
				caption: 'Outstanding'
			  },
			  {
				dataField: 'cpr',
				alignment: 'right',
				format: {
					type: 'fixedPoint',
					precision: 3,
					currency: '',
				  },
				caption: 'Outstanding CPR'
			  },
			  {
				dataField: 'deposit_gold',
				alignment: 'right',
				format: {
					type: 'fixedPoint',
					precision: 3,
					currency: '',
				  },
				caption: 'Deposit Gold'
			  },
			  {
				dataField: 'deposit_idr',
				alignment: 'right',
				format: {
					type: 'fixedPoint',
					precision: 3,
					currency: '',
				  },
				  caption: 'Deposit IDR'
			  },
			  {
				dataField: 'summarize',
				alignment: 'right',
				format: {
					type: 'fixedPoint',
					precision: 3,
					currency: '',
				  },
				caption: 'Summarize'
			  },
			  ],
			  sortByGroupSummaryInfo: [{
				summaryItem: 'count',
			  }],
			summary: {
				totalItems: [
				{
						column: 'outstanding',
						summaryType: 'sum',
						displayFormat: '{0}',
						showInGroupFooter: false,
						alignByColumn: true,
						valueFormat: {
							type: 'fixedPoint',
							precision: 3,
							thousandsSeparator: ',',
							currencySymbol: '',
							useGrouping: true,
						},
				},
				{
						column: 'cpr',
						summaryType: 'sum',
						displayFormat: '{0}',
						showInGroupFooter: false,
						alignByColumn: true,
						valueFormat: {
							type: 'fixedPoint',
							precision: 3,
							thousandsSeparator: ',',
							currencySymbol: '',
							useGrouping: true,
						},
				},
				{
					column: 'deposit_gold',
					summaryType: 'sum',
					displayFormat: '{0}',
					showInGroupFooter: false,
					alignByColumn: true,
					valueFormat: {
						type: 'fixedPoint',
						precision: 3,
						thousandsSeparator: ',',
						currencySymbol: '',
						useGrouping: true,
					},
				  },
				  {
					column: 'deposit_idr',
					summaryType: 'sum',
					displayFormat: '{0}',
					showInGroupFooter: false,
					alignByColumn: true,
					valueFormat: {
						type: 'fixedPoint',
						precision: 3,
						thousandsSeparator: ',',
						currencySymbol: '',
						useGrouping: true,
					},
				  },
				  {
					column: 'summarize',
					summaryType: 'sum',
					displayFormat: '{0}',
					showInGroupFooter: false,
					alignByColumn: true,
					valueFormat: {
						type: 'fixedPoint',
						precision: 3,
						thousandsSeparator: ',',
						currencySymbol: '',
						useGrouping: true,
					},
				  },
			],
				groupItems: [
				  {
					column: 'outstanding',
					summaryType: 'sum',
					displayFormat: '{0}',
					showInGroupFooter: false,
					alignByColumn: true,
					valueFormat: {
						type: 'fixedPoint',
						precision: 3,
						thousandsSeparator: ',',
						currencySymbol: '',
						useGrouping: true,
					},
				  },
				  {
					column: 'cpr',
					summaryType: 'sum',
					displayFormat: '{0}',
					showInGroupFooter: false,
					alignByColumn: true,
					valueFormat: {
						type: 'fixedPoint',
						precision: 3,
						thousandsSeparator: ',',
						currencySymbol: '',
						useGrouping: true,
					},
				  },
				  {
					column: 'deposit_gold',
					summaryType: 'sum',
					displayFormat: '{0}',
					showInGroupFooter: false,
					alignByColumn: true,
					valueFormat: {
						type: 'fixedPoint',
						precision: 3,
						thousandsSeparator: ',',
						currencySymbol: '',
						useGrouping: true,
					},
				  },
				  {
					column: 'deposit_idr',
					summaryType: 'sum',
					displayFormat: '{0}',
					showInGroupFooter: false,
					alignByColumn: true,
					valueFormat: {
						type: 'fixedPoint',
						precision: 3,
						thousandsSeparator: ',',
						currencySymbol: '',
						useGrouping: true,
					},
				  },
				  {
					column: 'summarize',
					summaryType: 'sum',
					displayFormat: '{0}',
					showInGroupFooter: false,
					alignByColumn: true,
					valueFormat: {
						type: 'fixedPoint',
						precision: 3,
						thousandsSeparator: ',',
						currencySymbol: '',
						useGrouping: true,
					},
				  },
				],
			  },
			onExporting(e) {
				const workbook = new ExcelJS.Workbook();
				const worksheet = workbook.addWorksheet('piutang');
		  
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
	piutang: function(){
		var me = this
		var data = frappe.call({
			method: 'lestari.lestari.page.kartu_piutang_custom.kartu_piutang_custom.contoh_report',
			args: {
				'posting_date': me.posting_date,
			}
		});

		return data
	},

})