# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

import frappe
import datetime
from frappe.model.document import Document
from frappe.utils import cint, flt, now_datetime, now, getdate
# from lestari.randomize import first_day_of_month, last_day_of_month, start_generate
from lestari.randomize import first_day_of_month, last_day_of_month, start_generate
from lestari.gold_selling.doctype.gold_invoice.gold_invoice import submit_gold_ledger
from frappe.model.naming import getseries
from frappe.model.naming import make_autoname
from frappe.model.mapper import get_mapped_doc

class RekapAktivitasSales(Document):
    @frappe.whitelist()
    def autoname(self):
        date = getdate(self.date)
        tahun = date.strftime("%y")
        bulan = date.strftime("%m")
        hari = date.strftime("%d")
        # frappe.throw(str(self.naming_series))
        self.naming_series = self.naming_series.replace(".YY.", tahun).replace(".MM.", bulan).replace(".DD.", hari)
        self.name = self.naming_series.replace(".####", getseries(self.naming_series, 4))

    @frappe.whitelist()
    def get_details(self):
        list_rekap = frappe.db.sql(
            """
                SELECT *
                FROM `tabGold Ledger Entry`
                WHERE bundle = '{}'
                ORDER BY
                    CASE
                        WHEN proses = 'New Stock' THEN 1
                        WHEN proses = 'Add Stock' THEN 2
                        WHEN proses = 'Penjualan' THEN 3
                        WHEN proses = 'Penyetoran' THEN 4
                    END,
                posting_date ASC
            """.format(self.bundle, self.sales), as_dict=1)

        detail = {}
        if not list_rekap:
            frappe.throw("Data Kosong")

        def _kadar(kadar):
            return kadar.replace("0", "").lower()

        for row in list_rekap:
            detail.setdefault(row.name, {
                "id": row.name,
                "tgl_rekap": row.posting_date,
                "aktivitas": row.proses,
                "6k": 0,
                "8k": 0,
                "8kp": 0,
                "16k": 0,
                "17k": 0,
                "17kp": 0,
                "total": row.qty_in if row.proses in ["Penyerahan", "Penyetoran", "Penjualan"] else row.qty_out
            })

            bruto = row.qty_in if row.qty_in > 0 else row.qty_out
            detail[row.name][_kadar(row.kadar)] = bruto
                        
            self.append("detail", detail[row.name])

        total = {"total": 0}    
        for index, row in detail.items():
            for kadar in ["6k", "8k", "8kp", "16k", "17k", "17kp", "total"]:
                total.setdefault(kadar, 0)
                total[kadar] = flt(total[kadar] + (row[kadar] if row['aktivitas'] not in ["Penyetoran", "Penjualan"] else -row[kadar]), 2)
        
        self.append('detail', {
            "aktivitas": "Total",
            **total
        })

        self.total_barang_dibawa = total["total"]
    
    @frappe.whitelist()
    def hanya_randomize_update_bundle_stock(self):
        month_name = self.bulan
        year = self.tahun

        start_generate(self.tahun, self.bulan)
        frappe.msgprint("Generate Done")

    @frappe.whitelist()
    def hapus_transfer_salesman(self):
        first_day, last_day = get_first_last_day(int(self.tahun), self.bulan)

        frappe.db.sql(""" DELETE FROM `tabKartu Stock Sales` WHERE `posting_date` between %s and %s """, [first_day, last_day])
        frappe.db.sql(""" DELETE FROM `tabGold Ledger Entry` WHERE `posting_date` between %s and %s """, [first_day, last_day])
        # frappe.db.commit()

        # tidak menggunakan get list untuk mengurangi waktu eksekusi
        list_ts = frappe.db.sql("""
            SELECT 
                name, naming_series
            FROM `tabUpdate Bundle Stock`
            WHERE date between %s and %s
            ORDER BY name desc
        """, [first_day, last_day])
        
        # 0 = name, 1= naming_series (mengurangi waktu eksekusi)
        naming, name = {}, []
        for row in list_ts:
            name.append(row[0])
            if not row[1]:
                continue

            prefix, _ = row[1].rsplit(".", 1)
            count = cint(row[0].replace(prefix, ""))
            naming.setdefault(row[1], {"max": count, "min": count})
            if count > naming[row[1]]["max"]:
                naming[row[1]]["max"] = count
            elif count < naming[row[1]]["min"]:
                naming[row[1]]["min"] = count

        if name:
            frappe.db.sql(""" DELETE FROM `tabUpdate Bundle Stock` WHERE `name` in %(name)s """, {"name": name})
            frappe.db.sql(""" DELETE FROM `tabDetail Penambahan Stock` WHERE `parent` in %(parent)s """, {"parent": name})
            frappe.db.sql(""" DELETE FROM `tabUpdate Bundle Stock Kadar` WHERE `parent` in %(parent)s """, {"parent": name})
            frappe.db.sql(""" DELETE FROM `tabUpdate Bundle Stock Sub` WHERE `parent` in %(parent)s """, {"parent": name})
        
        for series, new_index in naming.items():
            current = frappe.db.sql("SELECT `current` FROM `tabSeries` WHERE `name`=%s FOR UPDATE", (series,))
            if current and current[0][0] <= new_index["max"]:
                frappe.db.sql("UPDATE `tabSeries` SET `current` = %s - 1 WHERE `name`=%s", (new_index["min"], series))

        frappe.db.commit()

        list_aktivitas = frappe.db.sql("""SELECT name from `tabAktivitas Sales` where MONTHNAME(posting_date) = "{}" """.format(self.bulan),as_list=1)
        for row in list_aktivitas:
            frappe.delete_doc('Aktivitas Sales', row[0])

        frappe.msgprint("Delete Done!!")

        # for row in list_ts:
        #   frappe.delete_doc('Update Bundle Stock', row)
        #   frappe.db.commit()

        # from lestari.randomize2 import start_generate_multi
        # start_generate_multi(first_day, last_day)

    @frappe.whitelist()
    def get_transfer_salesman(self):
        first_day, last_day = get_first_last_day(int(self.tahun), self.bulan)
        
        # from lestari.randomize2 import start_generate_multi

        start_generate(self.tahun, self.bulan)

        frappe.msgprint("Submitting Gold invoice")

        list_ginv = frappe.db.get_list(
            "Gold Invoice",
            filters=[
                ['posting_date', 'between', [first_day, last_day]]
            ]
        )

        for row in list_ginv:
            submit_gold_ledger(row.name)

        list_bundle = frappe.db.sql(
            """
            SELECT DISTINCT(bundle), sales_partner FROM `tabGold Invoice`
            WHERE DATE(posting_date) >= DATE("{}")
            AND DATE(posting_date) <= DATE("{}")
        
            """.format(first_day, last_day), as_dict=1, debug=1
        )
        frappe.msgprint(list_bundle)
        for row in list_bundle:
            doc = ""
            self.detail = []
            # new_doc = frappe.new_doc("Aktivitas Sales")
            self.sales = row.sales_partner
            self.bundle = row.bundle
            self.get_details()
            self.save()

            import time
            time.sleep(1)
            
            source_name = row.bundle
            
            doc = get_mapped_doc(
                "Rekap Aktivitas Sales",
                source_name,
                {
                    "Rekap Aktivitas Sales": {
                        "doctype": "Aktivitas Sales",
                    },
                    "Rekap Aktivitas Sales Details": {
                        "doctype": "Aktivitas Sales Details",
                    },
                },
            )

            doc.save()

            # frappe.msgprint(str(doc))

        frappe.msgprint("Generate Done")


    @frappe.whitelist()
    def get_transfer_salesman_bundle(self):
        list_kss = frappe.db.get_list("Kartu Stock Sales", filters={"bundle": self.bundle})
        for row in list_kss:
            frappe.delete_doc('Kartu Stock Sales', row.name)
            frappe.db.commit()
        list_gle = frappe.db.get_list("Gold Ledger Entry", filters={"bundle": self.bundle})
        for row in list_gle:
            frappe.delete_doc('Gold Ledger Entry', row.name)
            frappe.db.commit()
        list_ts = frappe.db.get_list("Update Bundle Stock", filters={"bundle": self.bundle})
        for row in list_ts:
            frappe.delete_doc('Update Bundle Stock', row.name)
            frappe.db.commit()
        
        start_generate(self.tahun, self.bulan, self.bundle)
        list_ginv = frappe.db.get_list("Gold Invoice", filters={"bundle": self.bundle})
        for row in list_ginv:
            submit_gold_ledger(row.name)

        frappe.msgprint(str(get_first_last_day(self.tahun, self.bulan)))
        # list_bundle = frappe.db.get_list("Sales Stock Bundle", filters={""})

        frappe.msgprint("Generate Done")
        # self.get_details()

def get_first_last_day(year, month):
    month_name = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    month_number = int(month_name.index(month) if month else 0)
    
    return first_day_of_month(datetime.date(int(year), month_number, 1)), last_day_of_month(datetime.date(int(year), month_number, 1))
