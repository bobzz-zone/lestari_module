frappe.listview_settings["SPK Produksi"] = {
    onload: function (listview) {
        listview.page.add_inner_button('List SPK PPIC', () => frappe.set_route(['spk-ppic-list']))
        $(":button[data-label='List%20SPK%20PPIC']").css("background-color", "red");
        $(":button[data-label='List%20SPK%20PPIC']").css("color", "white");
    }
};