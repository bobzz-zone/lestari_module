// Copyright (c) 2023, DAS and contributors
// For license information, please see license.txt

var port,
  textEncoder,
  writableStreamClosed,
  writer,
  dataToSend,
  historyIndex = -1,
  timbangan,
  type_timbangan = "AND",
  connected = 0;
const lineHistory = [];
const baud = 9800;

async function connectSerial() {
  try {
	connected = 1;
	cur_frm.set_value("status_timbangan","Connected")
	cur_frm.refresh_field("status_timbangan");
    await port.open({ baudRate: 9600 });
    listenToPort();

    textEncoder = new TextEncoderStream();
    writableStreamClosed = textEncoder.readable.pipeTo(port.writable);

    writer = textEncoder.writable.getWriter();
	if(timbangan == null){
		timbangan = 1;
	}
	if(cur_frm.doc.berat==null && timbangan == 1){
	setInterval(function() {
		sendSerialLine()
	  }, 2500);
	}
  } catch {
  }
}
async function listenToPort() {
  const textDecoder = new TextDecoderStream();
  const readableStreamClosed = port.readable.pipeTo(textDecoder.writable);
  const reader = textDecoder.readable.getReader();
  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }
    appendToTerminal(value);
  }
}
async function sendSerialLine() {
  if(type_timbangan == "AND"){
  dataToSend = "S";
  }else{
  dataToSend = "O9";
  }
  lineHistory.unshift(dataToSend);
  historyIndex = -1; // No history entry selected
  dataToSend = dataToSend + "\r\n";
  await writer.write(dataToSend);
}

async function appendToTerminal(newStuff) {
  if (newStuff == "E01" || newStuff == "E" || newStuff == "01" && type_timbangan == "AND"){
	timbangan = 0;
	type_timbangan = "SHINKO";
  }
  // mettler
  newStuff = newStuff.replace("S S       ", "");
  newStuff = newStuff.replace("S       ", "");
  newStuff = newStuff.replace(" g", "");
  newStuff = newStuff.replace(" ", "");

  // // and 
  newStuff = newStuff.replace("ST,+0000", "");
  newStuff = newStuff.replace("ST,+000", "");
  newStuff = newStuff.replace("ST,+00", "");
  newStuff = newStuff.replace("ST,+0", "");
  newStuff = newStuff.replace("T,+0000", "");
  newStuff = newStuff.replace("T,+000", "");
  newStuff = newStuff.replace("T,+00", "");
  newStuff = newStuff.replace("T,+0", "");

  // shinko
  newStuff = newStuff.replace("+00000", "");
  newStuff = newStuff.replace("+0000", "");
  newStuff = newStuff.replace("+000", "");
  newStuff = newStuff.replace("+00", "");
  newStuff = newStuff.replace("+0", "");
  newStuff = newStuff.replace("+", "");

  // vibra
  newStuff = newStuff.replace("0000", "");
  newStuff = newStuff.replace("000", "");
  newStuff = newStuff.replace("00", "");
  if (newStuff.charAt(0) === '.') { // periksa apakah karakter pertama adalah titik
	  newStuff = newStuff.replace(/^\./, '0.'); // ganti karakter pertama dari titik menjadi 0.
  }
  if (newStuff.endsWith('.')) { // periksa apakah karakter terakhir adalah titik
	  newStuff += '00'; // tambahkan string "00" di belakangnya
  }
  if( connected == 1){
	let result = newStuff.includes("G S");
	if (result) {
		newStuff = newStuff.replace("G S", "");
	}
	cur_frm.set_value("berat", newStuff);
	cur_frm.refresh_field("berat");
	$(".berat_real").text(cur_frm.doc.berat);
  }
}

function hitung(){
	var totalberat = 0,
	totalqty = 0,
  	totaltransfer = 0;
	$.each(cur_frm.doc.items, function(i,e){
		// console.log(e.qty_penambahan)
		if(e.qty_penambahan != null){
		totalberat = parseFloat(totalberat) + parseFloat(e.qty_penambahan)
		totalqty = parseFloat(totalqty) + parseFloat(e.jumlah)
		// console.log(totalberat)
		}
	})
	cur_frm.set_value("total_bruto", totalberat)
	cur_frm.set_value("total_qty", totalqty)
	cur_frm.refresh_field("total_bruto")
	cur_frm.refresh_field("total_qty")

	cur_frm.clear_table("per_kadar")
		cur_frm.refresh_field('per_kadar');
		var totals = {},
		jumlahs = {};
			cur_frm.doc.items.forEach(function(row) {
				var kadar = row.kadar;
				var berat = parseFloat(row.qty_penambahan);
				var jumlah = parseFloat(row.jumlah);
				var berat_transfer = parseFloat(row.berat_transfer);
				if (!totals[kadar]) {
					totals[kadar] = 0;
					jumlahs[kadar] = 0;
				}
				totals[kadar] += berat;
				jumlahs[kadar] += jumlah;
			});
			for (var kadar in totals) {
				var total_berat = totals[kadar];
				var total_qty = jumlahs[kadar];
				var child = cur_frm.add_child('per_kadar');
				child.kadar = kadar;
				child.bruto = total_berat;
				child.total_qty = total_qty;
				// console.log(total_berat);
			}
			cur_frm.refresh_field('per_kadar');
}
// function addColumns(frm, fields, table) {
//     let grid = frm.get_field(table).grid;
    
//     for (let field of fields) {
// 		console.log(grid.fields_map[field])
//         grid.fields_map[field].hidden = 0;
//     }
    
//     grid.visible_columns = undefined;
//     grid.setup_visible_columns();
    
//     grid.header_row.wrapper.add();
//     delete grid.header_row;
//     grid.make_head();
    
//     for (let row of grid.grid_rows) {
//         if (row.open_form_button) {
//             row.open_form_button.parent().add();
//             delete row.open_form_button;
//         }
        
//         for (let field in row.columns) {
//             if (row.columns[field] !== undefined) {
//                 row.columns[field].add();
//             }
//         }
//         delete row.columns;
//         row.columns = [];
//         row.render_row();
//     }
    
// }
function showColumns(frm, fields, table) {
	let grid = frm.get_field(table).grid;
  
	// Menampilkan kolom yang tersembunyi
	for (let field of fields) {
	  grid.fields_map[field].hidden = 0;
	}
  
	// Mengatur ulang kolom yang terlihat
	grid.visible_columns = undefined;
	grid.setup_visible_columns();
  
	// Menghapus header row dan membuat ulang
	grid.header_row.wrapper.remove();
	delete grid.header_row;
	grid.make_head();
  
	// Mengembalikan kolom-kolom yang dihapus pada setiap baris
	for (let row of grid.grid_rows) {
	  // Menghapus tombol open form
	  if (row.open_form_button) {
		row.open_form_button.parent().remove();
		delete row.open_form_button;
	  }
  
	  // Mengembalikan kolom-kolom yang dihapus
	  for (let field in row.columns) {
		if (row.columns[field] === undefined) {
		  row.columns[field] = frappe.ui.form.make_control({
			df: grid.get_field(field),
			parent: row.wrapper.find(`[data-fieldname="${field}"]`),
			render_input: true,
		  });
		}
	  }
  
	  // Mengembalikan array kolom dan merender ulang baris
	  row.columns = row.make_columns();
	  row.render_row();
	}
  }
  

function removeColumns(frm, fields, table) {
    let grid = frm.get_field(table).grid;
    
    for (let field of fields) {
		// console.log(grid.fields_map[field])
        grid.fields_map[field].hidden = 1;
    }
    
    grid.visible_columns = undefined;
    grid.setup_visible_columns();
    
    grid.header_row.wrapper.remove();
    delete grid.header_row;
    grid.make_head();
    
    for (let row of grid.grid_rows) {
        if (row.open_form_button) {
            row.open_form_button.parent().remove();
            delete row.open_form_button;
        }
        
        for (let field in row.columns) {
            if (row.columns[field] !== undefined) {
                row.columns[field].remove();
            }
        }
        delete row.columns;
        row.columns = [];
        row.render_row();
    }
    
}

var list_kat;
async function getListAndSetQuery(frm) {
list_kat = [];
await frappe.db.get_list('Item Group', {
			filters: {
				parent_item_group: 'Products'
			}
		}).then(records => {
			for(var i = 0; i< records.length; i++){
				list_kat.push(records[i].name)
			}
			list_kat.sort()
		})
		if(cur_frm.doc.transfer == "Transfer Stockist ke Barang Lama" || cur_frm.doc.transfer == "Transfer Stockist ke PCB"){
			list_kat.push('Pembayaran')
			list_kat.sort()
			console.log(list_kat)
		}
		frm.set_query("sub_kategori", "items",function () {
			return {
				"filters": [
					["Item Group", "parent_item_group", "in", list_kat],
					["Item Group", "name", "!=", "Rongsok"],
				],
				"order_by":['name asc']
			};
		});
	}

frappe.ui.form.on('Transfer Stockist', {
	before_load:function(frm){
		// removeColumns(frm, 'note', 'Transfer Stockist Item')
	},
	onload:function(frm){
		frm.trigger('get_connect')

	},
	validate: function(frm){
		frm.events.get_disconnect(frm)
	},
	refresh: function(frm) {
		frm.add_custom_button(__("Connect"), () => frm.events.get_connect(frm));
		if (cur_frm.is_new()){
			frappe.db.get_value("Employee", { "user_id": frappe.session.user }, ["name","id_employee"]).then(function (responseJSON) {
				cur_frm.set_value("pic", responseJSON.message.name);
				cur_frm.set_value("id_employee", responseJSON.message.id_employee);
				cur_frm.get_field("transfer").set_focus()
				cur_frm.refresh_field("pic");
				cur_frm.refresh_field("id_employee");
			//   console.log(responseJSON)
			});
			if(cur_frm.doc.id_penerima){
			frappe.db.get_value("Employee", { "id_employee": cur_frm.doc.id_penerima }, ["name","employee_name"]).then(function (responseJSON) {
				cur_frm.set_value("employee_penerima", responseJSON.message.name);
				cur_frm.refresh_field("employee_penerima");
				})
			}
		}		
	getListAndSetQuery(frm);
	},
	id_employee: function(frm){
		frappe.db.get_value("Employee", { "id_employee": cur_frm.doc.id_employee }, ["name","employee_name"]).then(function (responseJSON) {
			cur_frm.set_value("nama_stokist", responseJSON.message.employee_name);
			cur_frm.set_value("pic", responseJSON.message.name);
			cur_frm.get_field("transfer").set_focus()
			cur_frm.refresh_field("nama_stokist");
			cur_frm.refresh_field("pic");
		})
	},
	id_penerima: function(frm){
		frappe.db.get_value("Employee", { "id_employee": cur_frm.doc.id_penerima }, ["name","employee_name"]).then(function (responseJSON) {
			// cur_frm.set_value("nama_penerima", responseJSON.message.employee_name);
			cur_frm.set_value("employee_penerima", responseJSON.message.name);
			// cur_frm.refresh_field("nama_penerima");
			cur_frm.refresh_field("employee_penerima");
		})
	},
	get_disconnect: function(frm){
		connected = 0;
		cur_frm.set_value("status_timbangan","Not Connect")
	},
	get_connect: function(frm){
		// frappe.msgprint("Connect");
		window.checkPort = async function (fromWorker) {
			if ("serial" in navigator) {
			  var ports = await navigator.serial.getPorts();
			  if (ports.length == 0 || fromWorker) {
				// console.log("Not Connected");
				cur_frm.set_value("status_timbangan","Not Connect")
				cur_frm.refresh_field("status_timbangan");
				frappe.confirm(
				  "Browser Belum Memiliki Ijin Akses Serial!, Ijinkan ?",
				  async function () {
					// Prompt user to select any serial port.
					port = await navigator.serial.requestPort();
					connectSerial();
				  },
				  function () {}
				);
			  } else {
				port = ports[0];
				connectSerial();
				// console.log("Connected");
				cur_frm.set_value("status_timbangan","Connected")
				cur_frm.refresh_field("status_timbangan");
				// Prompt user to select any serial port.
			  }
			} else {
			  frappe.msgprint("Your browser does not support serial device connection. Please switch to a supported browser to connect to your weigh device");
			}
		  }
		  window.checkPort(false);
	},
	transfer: function(frm){
		if(frm.doc.transfer != 'Transfer Stockist ke Produksi'){
			var fields = ['jumlah']
			var table = 'items'
			var fields1 = ['total_qty']
			var table1 = 'per_kadar'
			removeColumns(frm, fields, table)
			removeColumns(frm, fields1, table1)
		}else{
			var fields = ['jumlah']
			var table = 'items'
			var fields1 = ['total_qty']
			var table1 = 'per_kadar'
			showColumns(frm, fields, table)
			showColumns(frm, fields1, table1)
		}
		
	}
});


frappe.ui.form.on('Transfer Stockist Item', {
	items_add: function (frm, cdt, cdn){
		var d = locals[cdt][cdn];
		
        var idx = d.idx;
        var prev_kadar = 0;
		$.each(frm.doc.items, function(i,g){
			if(g.kadar != null){
				prev_kadar = g.kadar;
			}else{
				g.kadar = prev_kadar
			}
			cur_frm.refresh_field("item")
		})
		d.kadar = prev_kadar
        cur_frm.refresh_field('items');
		// hitung()
		if(cur_frm.doc.transfer == "Transfer Stockist ke Produksi"){
				d.set_df_property("jumlah","hidden",1)
		}
		if(cur_frm.doc.status_timbangan == "Connected"){
		// 	d.set_df_property("qty_penambahan","read_only",1)
		}else{
		// 	d.set_df_property("qty_penambahan","read_only",0)
		// var df = frappe.meta.get_docfield("Attribute Shopee","qty_penambahan", cur_frm.doc.items[d.idx]['parent']);
		// df.read_only = 1;
		// cur_frm.refresh_fields('items');
		}
	},
	items_remove: function(frm,cdt,cdn){
		hitung()
	},
	sub_kategori: function (doc,cdt, cdn){
		var d = locals[cdt][cdn];
		if(d.kadar != null){
		frappe.call({
			method: 'lestari.stockist.doctype.update_bundle_stock.update_bundle_stock.get_sub_item',
			args: {
				'kadar': d.kadar,
				'sub_kategori': d.sub_kategori
			},
			callback: function(r) {
				if (!r.exc) {
					d.item = r.message[0][0]
					d.gold_selling_item = r.message[0][1]
					cur_frm.refresh_field("items")
				}
			}
		});
		}
	}, 
	kadar: function (doc,cdt, cdn){
		var d = locals[cdt][cdn];
		frappe.model.set_value(cdt, cdn, 'qty_penambahan', "read_only", true);
		if(d.sub_kategori != null){
		frappe.call({
			method: 'lestari.stockist.doctype.update_bundle_stock.update_bundle_stock.get_sub_item',
			args: {
				'kadar': d.kadar,
				'sub_kategori': d.sub_kategori
			},
			callback: function(r) {
				if (!r.exc) {
					d.item = r.message[0][0]
					d.gold_selling_item = r.message[0][1]
					cur_frm.refresh_field("items")
					
				}
			}
		});
		}
	}, 
	qty_penambahan: function(frm,cdt,cdn){
		hitung();
	},
	
	jumlah: function(frm,cdt,cdn){
		hitung();
	},
	
	timbang: async function(frm,cdt,cdn){
		frappe.model.set_value(cdt, cdn, 'qty_penambahan', cur_frm.doc.berat);
		cur_frm.refresh_field("items")
	}
});
