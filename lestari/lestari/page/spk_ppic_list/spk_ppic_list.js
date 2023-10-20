frappe.pages['spk-ppic-list'].on_page_load = function(wrapper) {
	new DevExtreme(wrapper)
}
DevExtreme = Class.extend({
	init: function(wrapper){
		var me = this
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'SPK PRODUKSI',
			single_column: true
		});
		this.list_spk = []
		this.posting_date = ""
		// this.page.add_inner_button('Update Posts', () => update_posts())
		// this.page.change_inner_button_type('Update Posts', null, 'primary');
		this.page.set_primary_action('Buat SPK PRODUKSI', () => this.submit(), { icon: 'add', size: 'sm'})
		this.page.set_secondary_action('Refresh', () => this.make(), { icon: 'refresh', size: 'sm'})
		this.page.add_inner_button('List SPK PRODUKSI', () => frappe.set_route(['List', 'SPK Produksi']))
		this.page.add_field({"fieldtype": "Date", "fieldname": "posting_date","default": "Today",
			"label": __("Posting Date"), "reqd": 1,
			change: function() {
				me.posting_date = this.value;
				// console.log(this.posting_date) /// ini kenapa ga ke baca yak waktu di submit padahal di console log disini keluar
				// console.log(this.list_spk)
				// me.get_data();
			}
		}),

		// this.page.set_secondary_action(
		// 	__('Buat SPK Produksi'),
		// 	() => this.show_user_search_dialog(),
		// 	{ icon: 'add', size: 'sm'}
		// );
		this.make()
	},
	// make page
	make: async function(){
		let me = this
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
		// console.log(employees)		
		// DevExpress.localization.locale('id');
		$("#dataGrid").dxDataGrid({
			dataSource: employees.message,
        	keyExpr: 'name',
			showBorders: true,
			
			allowColumnReordering: true,
			allowColumnResizing: true,
			columnAutoWidth: true,
			columnFixing: {
                enabled: true,
                 fixedPosition: "top"
            },
			scrolling: {
				columnRenderingMode: 'virtual',
				// mode: 'infinite'
			  },
			groupPanel: {
				visible: true,
			},
			 pager: {
                allowedPageSizes: [25, 50, 100],
                showPageSizeSelector: true,
                showNavigationButtons: true
            },
            paging: {
                pageSize: 25,
            },
			grouping:{
				autoExpandAll: false
			},
			selection: {
				mode: "multiple",
				allowSelectAll: true,
				selectAllMode: 'page' // or "multiple" | "none"
			}, 
			filterRow: { visible: true },
			headerFilter: {
				visible: true,
			  },
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
				allowHeaderFiltering: false,
			//   }],
			// ,{
			},{
				dataField: 'name',
				format: 'string',
				alignment: 'left',
				// width: 110,
				caption: 'No FM'			   
			  }
			  ,{
				dataField: 'posting_date',
				format: 'date',
				alignment: 'right',
				caption: 'Posting Date',
				sortOrder: 'desc',
				// width: 110,
				
			  },{
				dataField: 'urut_fm',
				format: 'string',
				alignment: 'left',
				// width: 110,
				caption: 'Urut FM',
				allowHeaderFiltering: false,			   
			  },			   
			  {
				dataField: 'sub_kategori',
				format: 'string',
				// width: 150,
				caption: 'Sub Kategori'
			  },
			  {
				dataField: 'model',
				format: 'string',
				// width: 150,
				caption: 'No Model'
			  },
			  {
				dataField: 'kadar',
				format: 'string',
				// width: 150,
				caption: 'Kadar'
			  },
			  {
				dataField: 'qty',
				format: 'decimal',
				caption: 'Qty',
				allowHeaderFiltering: false,
			  },
			  {
				dataField: 'berat',
				format: 'decimal',
				caption: 'Berat',
				allowHeaderFiltering: false,
			  },
			  ],
			  onSelectionChanged(e) {
				e.component.refresh(true);
				if(e.currentSelectedRowKeys[0] != null){	
					me.list_spk.push(e.currentSelectedRowKeys[0])
				}
				if(e.currentDeselectedRowKeys[0] != null){
					me.list_spk = me.list_spk.filter(data => data != e.currentDeselectedRowKeys[0])
				}
				// console.log(e)
				// console.log(me.list_spk)
			  },
			  summary: {
				totalItems: [{
				  name: 'SelectedRowsSummary',
				  showInColumn: 'qty',
				  displayFormat: 'Qty: {0}',
				  summaryType: 'custom',
				},
				],
				calculateCustomSummary(options) {
					
				  if (options.name === 'SelectedRowsSummary') {
					if (options.summaryProcess === 'start') {
					  options.totalValue = 0;
					}
					if (options.summaryProcess === 'calculate') {
					  if (options.component.isRowSelected(options.value.name)) {
						options.totalValue += options.value.qty;
					  }
					}
				  }
				},
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
			},
			// onSelectionChanged(selectedItems) {
            //     const data = selectedItems.selectedRowsData;
            //     if (data.length > 0) {
            //         // $('#selected-items-container').val(
            //         // data
            //         //     .map((value) => `${value.linkPopup}`)
            //         //     .join(', '),
            //         // );
			// 		console.log(data)
            //     } else {
            //         $('#selected-items-container').val('NULL');
                    
            //     }
       
            // },
		});
		
	},
	employees: function(){
		var data = frappe.call({
			method: 'lestari.lestari.page.spk_ppic_list.spk_ppic_list.contoh_report',
			args: {
				'doctype': 'Purchase Order',
			}
		});

		return data
	},
	submit: function(){
		var me = this
		// console.log("test"+me.posting_date) // disini keluar test doang masih kosong
		frappe.call({
			method: 'lestari.lestari.page.spk_ppic_list.spk_ppic_list.make_spk_ppic',
			args: {
				'data': this.list_spk,
				'posting_date': me.posting_date // disini kosong why???
			},
			callback: function(){
				me.make()
			}
		})
	}
})