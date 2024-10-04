# Copyright (c) 2022, DAS and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now_datetime , now, getdate
from frappe.model.document import Document
from erpnext.accounts.utils import get_account_currency, get_fiscal_years, validate_fiscal_year
from datetime import datetime # from python std library
from frappe.utils import flt
from frappe.model.naming import getseries
from frappe.model.naming import make_autoname

@frappe.whitelist()
def autoname(self,method):
    date = getdate(self.posting_date)
    tahun = date.strftime("%y")
    bulan = date.strftime("%m")
    hari = date.strftime("%d")
    # frappe.throw(str(self.naming_series))
    self.naming_series = self.naming_series.replace(".YY.", tahun).replace(".MM.", bulan).replace(".DD.", hari)
    self.name = self.naming_series.replace(".###", getseries(self.naming_series,3))