// Copyright (c) 2022, DAS and contributors
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
	  // var warna;
	  // frappe.call({
		  // 	method: 'frappe.client.get',
		  // 	args: {
			  // 	  doctype: 'User',
			  // 	  filters: { name: frappe.session.user },
			  // 	  fields: ['desk_theme'],
			  // 	},
			  // 	callback: function(response) {
				  // 	  var user = response.message;
				  // 	  var isDarkMode = user.desk_theme === 'Light';
				  
				  // 	  if (isDarkMode) {
					  // 		console.log("Mode Gelap aktif");
					  // 		warna = "#f9fafa"
					  // 	  } else {
						  // 		console.log("Mode Terang aktif");
						  // 		warna = "#1f272e"
						  // 	  }
						  // 	}
						  //   });	  
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
  	totaltransfer = 0;
	$.each(cur_frm.doc.items, function(i,e){
		if(e.qty_penambahan != null){
		totalberat = parseFloat(totalberat) + parseFloat(e.qty_penambahan)
		}
	})
	cur_frm.set_value("total_bruto", totalberat)
	cur_frm.refresh_field("total_bruto")

	cur_frm.clear_table("per_kadar")
		cur_frm.refresh_field('per_kadar');
		var totals = {};
			cur_frm.doc.items.forEach(function(row) {
				var kadar = row.kadar;
				var berat = parseFloat(row.qty_penambahan);
				var berat_transfer = parseFloat(row.berat_transfer);
				if (!totals[kadar]) {
					totals[kadar] = 0;
				}
				totals[kadar] += berat;
			});
			for (var kadar in totals) {
				var total_berat = totals[kadar];
				var child = cur_frm.add_child('per_kadar');
				child.kadar = kadar;
				child.bruto = total_berat;
			}
			cur_frm.refresh_field('per_kadar');
}
var list_kat = [];
frappe.ui.form.on('Update Bundle Stock', {
	onload:function(frm){
		frm.trigger('get_connect')
	},
	validate: function(frm){
		frm.events.get_disconnect(frm)
	},
	refresh: function(frm) {	
		cur_frm.dashboard.refresh();
		const hasil_timbang = `
			<div class="hasiltimbangan" style="font-weight:bold;margin:0px 13px 0px 2px;
				color:#f9fafa;font-size:18px;display:inline-block;vertical-align:text-bottom;>
				<span class="label_berat">Berat</span>
				<span class="colon">:</span>
				<span class="berat_real">0</span>
			</div>`;
	
		cur_frm.toolbar.page.add_inner_message(hasil_timbang);
		cur_frm.get_field("bundle").set_focus()
		frm.add_custom_button(__("Connect"), () => frm.events.get_connect(frm));
		// frm.add_custom_button(__("Buat Baru"), () => frm.events.get_connect(frm));
		if (cur_frm.is_new()){
			frappe.db.get_value("Employee", { "user_id": frappe.session.user }, ["name","id_employee"]).then(function (responseJSON) {
				cur_frm.set_value("pic", responseJSON.message.name);
				cur_frm.set_value("id_employee", responseJSON.message.id_employee);
				cur_frm.get_field("bundle").set_focus()
				cur_frm.refresh_field("pic");
				cur_frm.refresh_field("id_employee");
			});
		}		
		frm.set_query("pic", function(){
			return {
				"filters": [
					["Employee", "department", "=", "Stockist - LMS"],
				]
			}
		});
		frm.set_query("sub_kategori", "items", function () {
			return {
				"filters": [
					["Item Group", "name", "=", "Perhiasan"],
				]
			};
		  });
		frm.set_query("bundle", function(){
			return {
				"filters": [
					["Sales Stock Bundle", "aktif", "=", 1],
					["Sales Stock Bundle", "docstatus", "=", 1],
				]
			}
		});
		
	},
	total_perkadar:function(frm){
		hitung()
	},
	get_disconnect: function(frm){
		connected = 0;
		cur_frm.set_value("status_timbangan","Not Connect")
	},
	get_connect: function(frm){
		window.checkPort = async function (fromWorker) {
			if ("serial" in navigator) {
			  var ports = await navigator.serial.getPorts();
			  if (ports.length == 0 || fromWorker) {
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
				cur_frm.set_value("status_timbangan","Connected")
				cur_frm.refresh_field("status_timbangan");
				// Prompt user to select any serial port.
			  }
			} else {
			//   frappe.msgprint("Your browser does not support serial device connection. Please switch to a supported browser to connect to your weigh device");
			  console.log("Your browser does not support serial device connection. Please switch to a supported browser to connect to your weigh device");
			}
		  }
		  window.checkPort(false);
	},
	id_employee: function(frm){
		frappe.db.get_value("Employee", { "id_employee": cur_frm.doc.id_employee }, ["name","employee_name"]).then(function (responseJSON) {
			cur_frm.set_value("nama_stokist", responseJSON.message.employee_name);
			cur_frm.set_value("pic", responseJSON.message.name);
			cur_frm.get_field("bundle").set_focus()
			cur_frm.refresh_field("nama_stokist");
			cur_frm.refresh_field("pic");
	})
	},
	bundle: async function(frm){
		// await frappe.db.count('Update Bundle Stock', { bundle: cur_frm.doc.bundle, docstatus:['!=',2] })
		// 	.then(count => {
		// 		if(count > 0){
		// 			// console.log(count)
		// 			frm.set_df_property('type','options',['Add Stock','Deduct Stock'])
		// 			frm.refresh()
		// 		}else{
		// 			// console.log('as')
		// 			cur_frm.set_df_property('type','options',['New Stock'])
		// 			cur_frm.set_value('type','New Stock')
		// 			cur_frm.set_df_property('type','read_only',1)
		// 			cur_frm.refresh_field('type')
		// 		}
		// 	})
	},
	type: function(frm){
		// cur_frm.fields_dic['items'].grid.get_field("sub_kategori").set_focus()
	}
});

frappe.ui.form.on('Detail Penambahan Stock', {
	items_add: function (frm, cdt, cdn){
		var d = locals[cdt][cdn];
        var prev_kadar, prev_sub_kategori,prev_kategori,prev_kadar,prev_item,prev_gold_selling_item;
		$.each(frm.doc.items, function(i,g){
			if(g.kadar != null){
				prev_kadar = g.kadar;
				prev_sub_kategori = g.sub_kategori;
				prev_kategori = g.kategori;
				prev_item = g.item;
				prev_gold_selling_item = g.gold_selling_item;
			}else{
				g.kadar = prev_kadar
				g.sub_kategori = prev_sub_kategori
				g.kategori = prev_kategori
				g.item = prev_item
				g.gold_selling_item = prev_gold_selling_item
			}
			cur_frm.refresh_field("item")
		})
		d.kadar = prev_kadar
        cur_frm.refresh_field('items');
		hitung()		
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
					cur_frm.doc.id_row = d.idx
					cur_frm.doc.field_row = "qty_penambahan"
					cur_frm.refresh_field("id_row")
					cur_frm.refresh_field("field_row")
					cur_frm.refresh_field("items")
					
				}
			}
		});
		}
	}, 
	qty_penambahan: function(frm,cdt,cdn){
		hitung();
	},
	timbang: async function(frm,cdt,cdn){
		frappe.model.set_value(cdt, cdn, 'qty_penambahan', cur_frm.doc.berat);
		cur_frm.refresh_field("items")
	}
});
