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
    pergerakan_stock = []
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
            a.posting_date AS tanggal,
            a.name AS voucher,
            "Transfer FG" AS proses,
            b.kadar,
            CONCAT (
                b.sub_kategori,
                "-",
                b.kadar,
                c.alloy
            ) AS produk,
            b.berat as berat
        FROM
            `tabTransfer Barang Jadi` a
        JOIN 
            `tabTransfer Barang Jadi Item` b
        ON b.parent = a.name
        JOIN 
            `tabData Logam` c
        ON c.name = b.kadar
        WHERE a.posting_date BETWEEN "{0}" AND "{1}"
        UNION
        SELECT
            a.date AS tanggal,
            a.name AS voucher,
            "Transfer Salesman" AS proses,
            b.kadar,
            b.item,
            b.bruto as berat
        FROM
            `tabUpdate Bundle Stock` a
        JOIN 
            `tabUpdate Bundle Stock Sub` b
        ON b.parent = a.name
        WHERE a.date BETWEEN "{0}" AND "{1}"
        ORDER BY 
            tanggal ASC, kadar DESC
    """.format(json_data[0],json_data[1]),as_dict = 1)
    # frappe.msgprint(str(list_doc))
    no = 0
    # qty_balance = 0.000
    # # kadar = row.kadar
    for row in list_doc:
        masuk = 0
        keluar = 0
        if row.proses == "Transfer FG":
            masuk = row.berat
        if row.proses == "Transfer Salesman":
            type_transfer = frappe.db.get_value("Update Bundle Stock", row.voucher, "type")
            if type_transfer == "New Stock" or type_transfer == "Add Stock":
                keluar = row.berat
            else:
                masuk = row.berat 
        no+=1
        baris_baris = {
            'no' : no,
            'posting_date' : row.tanggal,
            'proses' : row.proses,
            'voucher' : row.voucher,
            'kadar': row.kadar,
            'produk': row.produk,
            'masuk': masuk,
            'keluar' : keluar
            # 'saldo' : flt(qty_balance,3),
        }
        pergerakan_stock.append(baris_baris)
        # frappe.msgprint(str(baris_baris))
    return pergerakan_stock   
    # return list_doc   