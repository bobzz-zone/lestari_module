import datetime
import random
import time

import frappe
from frappe import _dict
from frappe.utils import getdate, flt, nowtime

from lestari.randomize import first_day_of_month, last_day_of_month, print_calendar, randomizer, start_generate

def get_first_last_day(year, month):
	month_name = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
	month_number = int(month_name.index(month) if month else 0)
	
	return first_day_of_month(datetime.date(year, month_number, 1)), last_day_of_month(datetime.date(year, month_number, 1))

def generate_bulan():
    st = time.time()
    first_day, last_day = get_first_last_day(int(2023), "May")
    # start_generate(int(2023), "May")
    start_generate_multi(first_day, last_day, bundle=None)
    
    en = time.time()
    print("Time taken = ", en-st)

@frappe.whitelist()
def start_generate_multi(first_day, last_day, bundle=None):
    
    from lestari.gold_selling.doctype.gold_invoice.gold_invoice import submit_gold_ledger

    def _emp(kadar):	
        emp = {}	
        if kadar == "06K":
            emp["pic"] = "HR-EMP-00489"
            emp["id_employee"] = 1240
        elif kadar == "08K":
            emp["pic"] = "HR-EMP-00485"
            emp["id_employee"] = 1147
        elif kadar == "16K":
            emp["pic"] = "HR-EMP-00486"
            emp["id_employee"] = 1194
        elif kadar in ["17K", "19K", "20K", "10K", "08KP"]:
            emp["pic"] = "HR-EMP-00487"
            emp["id_employee"] = 1225
        elif kadar in ["PCB", "17KP"]:
            emp["pic"] = "HR-EMP-00490"
            emp["id_employee"] = 1656

        return emp

    addons = ""
    if bundle:
        addons = " AND gi.bundle = '%s' " % bundle

    # get list gold invoice berdasarkan tanggal
    list_ginv = frappe.db.sql("""
        SELECT 
            gi.name, gi.sales_partner, gi.posting_date, gii.kadar, gii.qty, gi.bundle, gii.name as item_name, gii.category, gi.warehouse
        FROM `tabGold Invoice` gi
        JOIN `tabGold Invoice Item` gii ON gii.parent = gi.name
        WHERE posting_date between %s and %s
        {}
        AND gi.docstatus = 1
        
        ORDER BY gi.posting_date
    """.format(addons), [first_day, last_day])

    gold_invoice_sup, gold_inv_item, list_kadar, list_bundle_item = {}, [], set(), set()
    # key 0 = name, 1 = sales, 2 = posting_date, 3 = kadar, 4 = qty, 5 = bundle
    for row in list_ginv:
        # set gold invoice berdasarkan sales, kadar, bundle
        g_inv = gold_invoice_sup.setdefault((row[1], row[3], row[5]), {"total": []})
        # input total qty setiap tanggal
        if not g_inv.get(str(row[2])):
            g_inv[str(row[2])] = []
        g_inv[str(row[2])].append(row[4])
        
        # input keseluruhan qty sales, kadar, bundle
        g_inv["total"].append(row[4])

        # input keseluruhan gold invoice item
        gold_inv_item.append(_dict({
            "ginv": row[0],
            "category": row[7],
            "bundle": row[5],
            "kadar": row[3],
            "posting_date": row[2],
            "qty": row[4],
            "name": row[6],
            "warehouse": row[8],
        }))

        # input_kadar_bundle
        list_bundle_item.add((row[5], row[7]))
        # input keseluruhan tipe kadar
        list_kadar.add(row[3])

    # ambil key untuk dijadikan parameter
    key = list(gold_invoice_sup.keys())

    query = """ SELECT DISTINCT
            ubs.sales,
            dps.kadar,
            ubs.bundle
        FROM `tabUpdate Bundle Stock` ubs
        JOIN `tabDetail Penambahan Stock` dps ON dps.parent = ubs.name
        WHERE ubs.type = 'New Stock'
        AND (ubs.sales, dps.kadar, ubs.bundle) IN ({})
    """.format(','.join(['(%s, %s, %s)'] * len(key)))

    # Flatten the keys for the query parameters
    # Execute the query once
    data_penyerahan = frappe.db.sql(query, [item for sublist in key for item in sublist])
    penyerahan_sup = {(row[0], row[1], row[2]) for row in data_penyerahan}

    perhiasan_list = frappe.db.sql(""" 
        SELECT name, gold_selling_item, kadar
        FROM `tabItem` 
        WHERE item_group = "Perhiasan" and item_group_parent = "Pembayaran" and disabled != 1
        AND kadar IN %(kadar)s
        GROUP BY kadar
    """, {"kadar": list(list_kadar)})

    item_perhiasan = {}
    for row in perhiasan_list:
        item_perhiasan.setdefault(row[2], {"name": row[0], "gold_selling_item": row[1]})

    data_holiday = frappe.db.sql(""" SELECT holiday_date FROM `tabHoliday` """)
    # key 0 = sales, key 1 = kadar, key 2 = bundle
    for key_sup, posting_date in gold_invoice_sup.items():
        sales, kadar, i_bundle = key_sup
        for pd, qty in posting_date.items():
            if pd == "total":
                continue

            new_doc = frappe.new_doc("Update Bundle Stock")
            new_doc.bundle = i_bundle

            if (sales, kadar, i_bundle) in penyerahan_sup:
                new_doc.type = "Add Stock"
                new_doc.date = print_calendar(first_day, pd, data_holiday)
            else:
                new_doc.type = "New Stock"
                new_doc.date = frappe.db.get_value("Sales Stock Bundle", i_bundle, "date", cache=1)
                penyerahan_sup.add((sales, kadar, i_bundle))

            new_doc.s_warehouse = "Stockist - LMS"
            new_doc.purpose = "Sales"
            new_doc.sales = sales
            new_doc.warehouse = frappe.db.get_value("Sales Partner", new_doc.sales, "warehouse", cache=1)

            if emp := _emp(kadar):
                new_doc.update(emp)

            
            # for new_doc_row in new_doc.items:
            total_need= 0
            item = item_perhiasan.get(kadar)
            if not item:
                raise ValueError("List item tidak boleh kosong")
            
            total_qty = flt(sum(qty), 2)

            
            result = randomizer(new_doc.s_warehouse, kadar, total_qty, new_doc.type, kadar, i_bundle, new_doc.date)

            for baris_result in result:
                total_need += flt(baris_result[1])

                new_doc.append("per_sub_category",{
                    "item": baris_result[0] ,
                    "item_name": frappe.db.get_value("Item", baris_result[0], "item_name", cache=1),
                    "bruto": flt(baris_result[1]),
                    "kadar": kadar
                })
            
            new_doc.append("items",{
                "sub_category" : "Perhiasan",
                "kadar" : kadar,
                "qty_penambahan" : total_need,
                "item": item["name"] ,
                "gold_selling_item": item["gold_selling_item"]
            })
            
            new_doc.append("per_kadar",{
                "kadar" : kadar,
                "bruto" : total_need,
            })

            new_doc.total_bruto = total_need
            new_doc.save()

    # Prepare the SQL query for all keys
    query = """
        SELECT 
            ubs.sales, ubss.kadar, ubs.bundle, ubss.bruto, ubss.item
        FROM `tabUpdate Bundle Stock` ubs 
        JOIN `tabUpdate Bundle Stock Sub` ubss 
        ON ubss.parent = ubs.name 
        WHERE (ubss.kadar, ubs.bundle) IN %s
            AND ubss.bruto IS NOT NULL
    """

    # Execute the query once
    data_transfer_salesman = frappe.db.sql("""
        SELECT 
            ubs.sales, ubss.kadar, ubs.bundle, ubss.bruto, ubss.item
        FROM `tabUpdate Bundle Stock` ubs 
        JOIN `tabUpdate Bundle Stock Sub` ubss 
        ON ubss.parent = ubs.name 
        WHERE (ubss.kadar, ubs.bundle) IN %(kadar_bundle)s
            AND ubss.bruto IS NOT NULL
    """, { "kadar_bundle": [(k[1], k[2]) for k in key] })

    transfer_salesman_dict, transfer_stock = {}, {}
    # Convert the result to a dictionary for easy lookup
    for row in data_transfer_salesman:
        transfer_salesman_dict.setdefault((row[0], row[1], row[2]), []).append(row[3])
        transfer_stock.setdefault((row[1], row[2]), {}).setdefault(row[4], 0)

        transfer_stock[(row[1], row[2])][row[4]] =+ row[3]

    # key 0 = sales, key 1 = kadar, key 2 = bundle
    for key_peng, qty in gold_invoice_sup.items():
        sales, kadar, i_bundle = key_peng

        masuk = flt(sum(qty["total"]), 2)
        total_bruto = flt(sum(transfer_salesman_dict.get(key_peng, [0])), 2)
        if flt(total_bruto, 2) >= masuk:
            new_doc = frappe.new_doc("Update Bundle Stock")

            if emp := _emp(kadar):
                new_doc.update(emp)

            new_doc.date = getdate(last_day)
            new_doc.bundle = i_bundle
            new_doc.type = "Deduct Stock"

            new_doc.s_warehouse = "Stockist - LMS"
            new_doc.purpose = "Sales"
            new_doc.sales = sales
            new_doc.warehouse = frappe.db.get_value("Sales Partner", sales, "warehouse", cache=1)

            item = item_perhiasan.get(kadar)
            if not item:
                raise ValueError("List item tidak boleh kosong")
            
            maksimal_total = flt(total_bruto - masuk, 2)
            new_doc.append("items", {
                "sub_category" : "Perhiasan",
                "kadar" : kadar,
                "qty_penambahan" : maksimal_total,
                "item": item["name"],
                "gold_selling_item": item["gold_selling_item"]
            })

            new_doc.append("per_kadar", {
                "kadar" : kadar,
                "bruto" : maksimal_total,
            })
            
            # untuk margin 0.001-0.001
            maksimal_total = maksimal_total + round(random.uniform(0.001, 0.01), 2)
            item_pengembalian = transfer_stock.get((kadar, i_bundle)) or {}
            
            retur_result = generate_list_retur(item_pengembalian, maksimal_total)

            for per_index, per_value in retur_result.items():
                new_doc.append("per_sub_category",{
                    "item": per_index ,
                    "item_name": frappe.db.get_value("Item", per_index, "item_name", cache=1),
                    "bruto": flt(per_value, 2),
                    "kadar": kadar
                })

            new_doc.save()
    
    # pengganti submit_gold_ledger untuk eksekusi yang lebih cepat
    kss_list = frappe.db.sql("""
        SELECT 
            item, bundle, kategori, kadar, qty
        FROM `tabKartu Stock Sales`
        WHERE (bundle, item) IN %(kadar_bundle)s
    """, { "kadar_bundle": list(list_bundle_item) })

    kss_dict = {}
    for row in kss_list:
        kss_dict.setdefault((row[0], row[1]), row)

    for row in gold_inv_item:

        subkategori = frappe.db.get_value("Gold Selling Item", row.category, "item_group", cache=1)
        kategori = frappe.db.get_value("Item Group", subkategori, "parent_item_group", cache=1)

        gdle = frappe.new_doc("Gold Ledger Entry")

        gdle.item = row.category
        gdle.bundle = row.bundle
        gdle.kategori = kategori
        gdle.sub_kategori = subkategori
        gdle.kadar = row.kadar
        gdle.warehouse = row.warehouse
        gdle.posting_date = row.posting_date
        gdle.posting_time = nowtime()
        gdle.voucher_type = "Gold Invoice"
        gdle.voucher_no = row.ginv
        gdle.voucher_detail_no = row.name
        kss = kss_dict.get((row.bundle, row.category), []) or []
        
        for col in kss:
            gdle.proses = 'Penjualan'
            gdle.qty_in = 0
            gdle.qty_out = row.qty
            gdle.qty_balance = col.qty

        gdle.flags.ignore_permissions = True
        gdle.save()

def generate_list_retur(list_item, maksimal_total):
    if not list_item:
        return {}

    list_key = list(list_item.keys())
    random.shuffle(list_key)

    remaining_sum = maksimal_total
    result = {}
    for index, key in enumerate(list_key):
        if remaining_sum <= 0:
            break

        if index == len(list_key) - 1:
            value = min(list_item[key], remaining_sum) if list_item[key] != remaining_sum else list_item[key]

            if value > 0:
                value = flt(value, 2)
                result.setdefault(key, value)
                remaining_sum -= value
        else:
            # For other elements, ensure the sum with the last element does not exceed the max value
            max_possible = min(index, remaining_sum)
            value = round(random.uniform(0, max_possible), 2)
            if value > 0:
                result.setdefault(key, value)
                remaining_sum -= value

    return result