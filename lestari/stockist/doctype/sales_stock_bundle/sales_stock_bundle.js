// Copyright (c) 2022, DAS and contributors
// For license information, please see license.txt

function formatDate(d)
{
    //get the month
    var month = d.getMonth();
    //get the day
    //convert day to string
    var day = d.getDate().toString().padStart(2, '0');
    //get the year
    var year = d.getFullYear();
    
    //pull the last two digits of the year
    year = year.toString().substr(-2);
    
    //increment month by 1 since it is 0 indexed
    //converts month to a string
    month = (month + 1).toString().padStart(2, '0');

    //return the string "MMddyy"
    return year + month + day;
}

function updnobundle(){
	var nobunble;
	var tgl;
	tgl = new Date(cur_frm.doc.date);
	if(cur_frm.doc.sales != null){
	nobunble = cur_frm.doc.abbr + formatDate(tgl);
	cur_frm.set_value("no_bundle",nobunble);
	cur_frm.refresh_field("no_bundle");
	}else{
		frappe.throw("Sales Tidak Boleh Kosong!!");
	}
}

frappe.ui.form.on('Sales Stock Bundle', {
	// refresh: function(frm) {
	
	// },
	sales: function(frm){
		updnobundle();
	},
	date: function(frm){
		updnobundle();
	},
	purpose: function(frm){
		if(cur_frm.doc.purpose == "Event"){
			cur_frm.set_value("sales","")
			cur_frm.refresh_field();
		}
	}
});
