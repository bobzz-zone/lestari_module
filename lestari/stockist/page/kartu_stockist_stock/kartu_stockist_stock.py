# Copyright (c) 2021, Patrick Stuhlmüller and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.utils import now,today,add_days,flt
from datetime import datetime, timedelta, date
from decimal import Decimal, getcontext 

@frappe.whitelist()
def debug_check_balance():
    qty_balance = check_balance("2023-04-17","GPAC2-06KY")
    print(qty_balance)

@frappe.whitelist()
def check_balance(posting_date, item):
    tgl = datetime.strptime(str(posting_date), '%Y-%m-%d')
    print(tgl)
    qty_balance = frappe.db.sql("""
        SELECT
            qty_after_transaction
        FROM 
            `tabStock Ledger Entry`
        WHERE
            posting_date = "{0}"
        AND
            item_code = "{1}"
    """.format(tgl,item),as_dict=1)

    return (qty_balance[0].qty_after_transaction)

@frappe.whitelist()
def contoh_report(posting_date = None, produk = None, kadar = None):
    pergerakan_stock = []
    if posting_date:
        json_data = json.loads(posting_date)
    else:
        input_dt = datetime.today()
        res = input_dt.replace(day=1)
        json_data = ['2023-01-01', today()]

    condition = ""
    condition1 = ""
    # if sales:
    #     condition = """AND sales = '{}'""".format(sales)
    if produk:
        condition += """AND b.sub_kategori = '{}'""".format(produk)
        condition1 += """AND b.item LIKE '%{}%'""".format(produk+"-"+kadar)
    if kadar:
        condition += """AND b.kadar = '{}'""".format(kadar)
        condition1 += """AND b.kadar = '{}'""".format(kadar)
    if produk == "" or kadar == "":
        frappe.msgprint("Isikan Produk dan Kadar")
        return

    list_doc = frappe.db.sql("""
        SELECT
            a.date AS tanggal,
            a.name AS voucher,
            "Transfer FG" AS proses,
            b.kadar,
            CONCAT (
                b.sub_kategori,
                "-",
                b.kadar,
                c.alloy
            ) AS produk,
            b.qty_penambahan AS berat,
            e.`qty_after_transaction` AS balance
            FROM
            `tabTransfer Stockist` a
            JOIN `tabTransfer Stockist Item` b
                ON b.parent = a.name
            JOIN `tabData Logam` c
                ON c.name = b.kadar
            JOIN `tabStock Entry` d
                ON d.voucher_no = a.name
            LEFT JOIN `tabStock Ledger Entry` e
                ON e.`voucher_no` = d.name
            WHERE a.date BETWEEN "{0}" AND "{1}"
            {2}
            UNION
            SELECT
            a.date AS tanggal,
            a.name AS voucher,
            "Transfer Salesman" AS proses,
            b.kadar,
            b.item,
            b.bruto AS berat,
            "0" AS balance
            FROM
            `tabUpdate Bundle Stock` a
            JOIN `tabUpdate Bundle Stock Sub` b
                ON b.parent = a.name
            WHERE a.date BETWEEN "{0}" AND "{1}"
            {3}
            ORDER BY tanggal ASC,
            kadar DESC
    """.format(json_data[0],json_data[1],condition,condition1),as_dict = 1, debug = 1)
    # frappe.msgprint(str(list_doc))
    no = 0
    # qty_balance = 0.000
    # # kadar = row.kadar
    qty_balance = 0
    for row in list_doc:
        masuk = 0
        keluar = 0
        if row.proses == "Transfer FG":
            masuk = flt(row.berat)
            if no == 0:
                qty_balance = flt(row.balance)
            else:
                qty_balance += flt(row.berat)
        if row.proses == "Transfer Salesman":
            # qty_balance = check_balance(row.tanggal, row.produk)
            type_transfer = frappe.db.get_value("Update Bundle Stock", row.voucher, "type")
            if type_transfer == "New Stock" or type_transfer == "Add Stock":
                keluar = flt(row.berat)
                qty_balance = flt(qty_balance) - flt(row.berat)
            else:
                masuk = flt(row.berat)
                qty_balance = flt(qty_balance) + flt(row.berat)
        no+=1
        baris_baris = {
            'no' : no,
            'posting_date' : row.tanggal,
            'proses' : row.proses,
            'voucher' : row.voucher,
            'kadar': row.kadar,
            'produk': row.produk,
            'masuk': masuk,
            'keluar' : keluar,
            'saldo' : flt(qty_balance,3),
        }
        pergerakan_stock.append(baris_baris)
        # frappe.msgprint(str(baris_baris))
    return pergerakan_stock   
    # return list_doc   