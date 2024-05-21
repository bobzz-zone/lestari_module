# Copyright (c) 2021, Patrick Stuhlmüller and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.utils import now,today,add_days,flt
from datetime import datetime
from decimal import Decimal, getcontext 


@frappe.whitelist()
def contoh_report(posting_date = None, bundle = None, kadar = None):
    invoice = []
    if posting_date:
        json_data = json.loads(posting_date)
    else:
        input_dt = datetime.today()
        res = input_dt.replace(day=1)
        json_data = ['2023-01-01', today()]

    condition = ""
    # if sales:
    #     condition = """AND sales = '{}'""".format(sales)
    if bundle:
        condition = """AND bundle = '{}'""".format(bundle)
    if kadar:
        condition = """AND kadar = '{}'""".format(kadar)
        
    list_doc = frappe.db.sql("""
        SELECT 
        NAME, 
        posting_date,
        proses,
        voucher_no,
        kadar,
        SUM(qty_in) AS masuk,
        SUM(qty_out) AS keluar

        FROM `tabGold Ledger Entry`
        WHERE
        posting_date BETWEEN "{0}" AND "{1}"
        {2}
        GROUP BY kadar, proses, bundle, posting_date 
        ORDER BY kadar ASC, posting_date ASC
    """.format(json_data[0],json_data[1],condition),as_dict = 1)
    no = 0
    qty_balance = 0.000
    # kadar = row.kadar
    for row in list_doc:
        getcontext().prec = 3
        if row.masuk > 0.000:
            # qty_balance = Decimal(str(qty_balance)) + Decimal(str(row.masuk))
            qty_balance = flt(qty_balance,3) + flt(row.masuk,3)
        if row.keluar > 0.000:
            # qty_balance = Decimal(str(qty_balance)) - Decimal(str(row.keluar))
            qty_balance = flt(qty_balance,3) - flt(row.keluar,3)
        # frappe.msgprint(str(row.masuk))
        # frappe.msgprint(str(qty_balance))
        no+=1
        baris_baris = {
            'no' : no,
            'posting_date' : row.posting_date,
            'proses' : row.proses,
            'voucher_no' : row.voucher_no,
            'kadar': row.kadar,
            'qty_in': row.masuk,
            'qty_out' : row.keluar,
            'qty_balance' : flt(qty_balance,3),
        }
        invoice.append(baris_baris)
        # frappe.msgprint(str(baris_baris))
    return invoice   
    # return list_doc   