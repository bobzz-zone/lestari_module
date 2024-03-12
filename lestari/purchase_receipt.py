# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt, getdate, nowdate
from frappe.model.naming import getseries
from frappe.model.naming import make_autoname
import erpnext
from datetime import datetime

@frappe.whitelist()
def autoname_prec(self,method): 
    if not self.tujuan:
        return
    kode = "01" if self.tujuan in ['Logam','Batu'] else "02"
    tahun = str(self.posting_date).split("-")[0]
    bulan_angka = str(self.posting_date).split("-")[1]
    naming_series = "YYYY./.KODE./.MM./.#####."
    naming_series = naming_series.replace("YYYY.", tahun).replace(".KODE.", kode).replace(".MM.", bulan_angka)
    text_angka = getseries(naming_series, 5)
    self.name = naming_series.replace(".#####.",text_angka)