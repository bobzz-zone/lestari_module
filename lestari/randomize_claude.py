import frappe
import random
import pandas as pd
import datetime
from frappe.utils import getdate, now_datetime
from datetime import datetime, timedelta, date
from faker import Faker
import time

# Fungsi Utama
def start_generate(year, month, bundle=None):
    if is_generate_locked():
        frappe.throw("Generate process is locked. Please try again later.")
    
    set_generate_lock(True)
    try:
        if not wait_for_reposting():
            frappe.throw("Reposting process is still running. Please try again later.")

        first_day, last_day = get_month_range(year, month)
        addons = f" AND gi.bundle = '{bundle}'" if bundle else ""

        gold_invoices = get_gold_invoice_list(first_day, last_day, addons)
        holidays = get_holidays()
        penyerahan_data = get_penyerahan_data(first_day, last_day)

        for invoice in gold_invoices:
            process_single_invoice(invoice, holidays, penyerahan_data, first_day)

        process_pengembalian(first_day, last_day, addons, holidays)
        
    finally:
        set_generate_lock(False)

def process_single_invoice(invoice, holidays, penyerahan_data, first_day):
    new_doc = create_update_bundle_stock_doc(invoice, holidays, penyerahan_data, first_day)
    process_item_details(new_doc, invoice)
    new_doc.save()
    update_stock_ledger(new_doc)
    frappe.db.commit()


# Fungsi-fungsi yang Terhubung Langsung ke start_generate
def get_month_number(month_name):
    month_dict = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12
    }
    return month_dict.get(month_name, 0)

def get_gold_invoice_list(first_day, last_day, addons):
    return frappe.db.sql(f""" 
        SELECT 
        gi.name,
        gi.sales_partner as sales_partner, 
        IF(MONTH(DATE_ADD(gi.posting_date, INTERVAL - WEEKDAY(gi.posting_date) DAY)) != MONTH(gi.posting_date), gi.`posting_date`,DATE_ADD(gi.posting_date, INTERVAL - WEEKDAY(gi.posting_date) DAY)) AS senin, 
        gii.kadar, 
        SUM(gii.qty) as qty, 
        gi.bundle,
        gi.posting_date

        FROM 
        `tabGold Invoice` gi
        JOIN `tabGold Invoice Item` gii ON gii.parent = gi.name
        WHERE DATE(gi.posting_date) >= DATE("{first_day}")
        AND DATE(gi.posting_date) <= DATE("{last_day}")
        
        {addons}

        AND gi.docstatus = 1

        GROUP BY gi.sales_partner, senin, gii.kadar, gi.bundle
        ORDER BY gi.sales_partner, gi.posting_date, gi.bundle, gii.kadar 
        
        """, as_dict=1, debug=True)

def get_penyerahan_data(first_day, last_day):
    return frappe.db.sql(f""" SELECT 
        ubs.name, ubs.`sales`,dps.`kadar`,ubs.`bundle`
        FROM `tabUpdate Bundle Stock` ubs JOIN
        `tabDetail Penambahan Stock` dps ON dps.parent = ubs.name
        WHERE ubs.type = "New Stock"
        AND DATE(ubs.date) >= DATE("{first_day}")
        AND DATE(ubs.date) <= DATE("{last_day}")
    """, debug=True)

def create_penyerahan_array(data_penyerahan):
    return [f"{row[1]}|{row[2]}|{row[3]}" for row in data_penyerahan]

def process_gold_invoice(lis_gold_invoice, data_holiday, penyerahan_array, first_day, last_day):
    for row in lis_gold_invoice:
        new_doc = create_update_bundle_stock_doc(row, data_holiday, penyerahan_array, first_day)
        process_item_details(new_doc, row)
        new_doc.save()
        update_stock_ledger(new_doc)
        frappe.db.commit()

def create_update_bundle_stock_doc(row, data_holiday, penyerahan_array, first_day):
    new_doc = frappe.new_doc("Update Bundle Stock")
    new_doc.bundle = row.bundle
    new_doc.type = "Add Stock" if f"{row.sales_partner}|{row.kadar}|{row.bundle}" in penyerahan_array else "New Stock"
    new_doc.date = print_calendar(first_day, row.posting_date, data_holiday, row.senin) if new_doc.type == "Add Stock" else frappe.db.get_value("Sales Stock Bundle", row.bundle, "date", cache=1)
    new_doc.s_warehouse = "Stockist - LMS"
    new_doc.purpose = "Sales"
    new_doc.sales = row.sales_partner
    new_doc.warehouse = frappe.db.get_value("Sales Partner", new_doc.sales, "warehouse", cache=1)
    set_pic_and_employee(new_doc, row.kadar)
    return new_doc

def set_pic_and_employee(new_doc, kadar):
    pic_employee_map = {
        "06K": ("HR-EMP-00489", 1240),
        "08K": ("HR-EMP-00485", 1147),
        "16K": ("HR-EMP-00486", 1194),
        "17K": ("HR-EMP-00487", 1225),
        "19K": ("HR-EMP-00487", 1225),
        "20K": ("HR-EMP-00487", 1225),
        "10K": ("HR-EMP-00487", 1225),
        "08KP": ("HR-EMP-00487", 1225),
        "PCB": ("HR-EMP-00490", 1656),
        "17KP": ("HR-EMP-00490", 1656)
    }
    new_doc.pic, new_doc.id_employee = pic_employee_map.get(kadar, (None, None))

def process_item_details(new_doc, row):
    result = randomizer(new_doc.s_warehouse, row.kadar, row.qty, new_doc.type, row.kadar, row.bundle, new_doc.date)
    total_need = 0
    for baris_result in result:
        total_need += frappe.utils.flt(baris_result[1])
        new_doc.append("per_sub_category", {
            "item": baris_result[0],
            "item_name": frappe.db.get_value("Item", baris_result[0], "item_name", cache=1),
            "bruto": frappe.utils.flt(baris_result[1]),
            "kadar": row.kadar
        })
    add_items_and_kadar(new_doc, row.kadar, total_need)

def add_items_and_kadar(new_doc, kadar, total_need):
    item = frappe.get_cached_doc("Item", {"kadar": kadar, "item_group": "Perhiasan", "item_group_parent": "Pembayaran"})
    new_doc.append("items", {
        "sub_category": "Perhiasan",
        "kadar": kadar,
        "qty_penambahan": total_need,
        "item": item.name,
        "gold_selling_item": item.gold_selling_item
    })
    new_doc.append("per_kadar", {
        "kadar": kadar,
        "bruto": total_need,
    })
    new_doc.total_bruto = total_need

def process_pengembalian(first_day, last_day, addons, data_holiday):
    list_pengembalian = get_pengembalian_list(first_day, last_day, addons)
    data_transfer_stock = get_transfer_stock_data(first_day, last_day)
    pengembalian_dict = create_pengembalian_dict(first_day, last_day)

    for row in list_pengembalian:
        keluar = pengembalian_dict.get((row.bundle, row.sales_partner, row.kadar), 0)
        masuk = row.qty
        if frappe.utils.flt(keluar) >= frappe.utils.flt(masuk):
            create_pengembalian_doc(row, keluar, masuk, data_holiday, last_day, data_transfer_stock)

# Fungsi-fungsi Pembantu
def first_day_of_month(any_day):
    return any_day.replace(day=1)

def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)

def print_calendar(str_start_date, str_end_date, data_holiday, senin):
    final_date = ""
    try:
        check_holiday = data_holiday.index(str(senin))

        fake = Faker()

        start_date = datetime.strptime(str(str_start_date), '%Y-%m-%d')
        end_date = datetime.strptime(str(str_end_date), '%Y-%m-%d') - timedelta(days=1)

        check = 0 

        while check == 0:
            if final_date == "":
                final_date = get_monday_of_date(str_end_date)
            
            try:
                check_holiday = data_holiday.index(str(final_date))
                final_date = fake.date_between(start_date=start_date, end_date=end_date)
            except:
                check = 1
                
    except:
        final_date = senin

    return str(final_date)

def randomizer(input_warehouse, input_kadar, kebutuhan, type, kadar, bundle, tanggal):
    list_item = get_available_items(warehouse, kadar, tanggal)
    
    if not list_item:
        frappe.throw(f"Tidak ada item dengan kadar {kadar} tersedia di gudang {warehouse}.")

    total_available = sum(item.qty_after_transaction for item in list_item)
    if total_available < kebutuhan:
        frappe.throw(f"Stok tidak cukup untuk kadar {kadar}. Tersedia: {total_available}, Dibutuhkan: {kebutuhan}")

    kebutuhan_min = kebutuhan * 1.10
    kebutuhan_max = min(kebutuhan * 1.20, total_available)

    return generate_random_list(list_item, kebutuhan_min, kebutuhan_max)

def generate_random_list(items, min_need, max_need):
    result = []
    total = 0
    items = sorted(items, key=lambda x: x.qty_after_transaction, reverse=True)

    while total < min_need and items:
        item = items.pop(0)
        qty = min(item.qty_after_transaction, max_need - total)
        if qty > 0:
            result.append([item.item_code, qty])
            total += qty

        if total >= max_need:
            break

    if total < min_need:
        frappe.throw(f"Tidak dapat memenuhi kebutuhan minimum. Total terpilih: {total}, Minimum dibutuhkan: {min_need}")

    return result


def generate_list(list_item, kebutuhan_min, kebutuhan_max, type, kadar, bundle, tanggal):
    if not list_item:
        raise ValueError("List item tidak boleh kosong")
    
    temp_list = list(list_item)
    result_list = []
    counter = 0

    while True:
        counter += 1
        random.shuffle(temp_list)
        result_list = []
        kebutuhan = 0
        for item in temp_list:
            if item['qty_after_transaction'] <= 0:
                continue
            qty_random = round(random.uniform(0, min(item['qty_after_transaction'], kebutuhan_min)), 2)
            result_list.append([item['item_code'], qty_random])
            kebutuhan += qty_random

            if kebutuhan_min <= kebutuhan <= kebutuhan_max:
                print(f"Looping selesai setelah {counter} kali iterasi.")
                return result_list

        if counter > 1000:
            raise Exception("Terlalu banyak iterasi, periksa parameter input")

def update_stock_ledger(doc):
    for item in doc.items:
        sle = frappe.get_doc({
            "doctype": "Stock Ledger Entry",
            "item_code": item.item,
            "warehouse": doc.s_warehouse,
            "actual_qty": -item.qty_penambahan,
            "posting_date": doc.date,
            "posting_time": now_datetime().strftime('%H:%M:%S'),
            "valuation_rate": 0,  # Sesuaikan jika diperlukan
            "company": frappe.get_cached_value('Warehouse', doc.s_warehouse, 'company'),
            "voucher_type": doc.doctype,
            "voucher_no": doc.name,
            "voucher_detail_no": item.name
        })
        sle.insert()
    
    frappe.db.commit()

def get_available_items(warehouse, kadar, tanggal):
    return frappe.get_all(
        "Stock Ledger Entry",
        filters={
            "warehouse": warehouse,
            "posting_date": ("<=", tanggal),
            "item_code": ("like", f"%{kadar}%")
        },
        fields=["item_code", "qty_after_transaction"],
        order_by="creation desc"
    )

def is_generate_locked():
    return frappe.cache().get_value("generate_lock")

def set_generate_lock(lock=True):
    frappe.cache().set_value("generate_lock", lock)

def wait_for_reposting():
    max_retries = 12  # 1 hour max wait time
    for _ in range(max_retries):
        if not check_reposting_status():
            return True
        time.sleep(300)  # Wait 5 minutes before checking again
    return False

def check_reposting_status():
    return frappe.db.exists("Repost Item Valuation", {"status": "Queued"})

# Fungsi-fungsi lain yang diperlukan (get_pengembalian_list, get_transfer_stock_data, create_pengembalian_dict, create_pengembalian_doc)



def get_pengembalian_list(first_day, last_day, addons):
    return frappe.db.sql(f""" 
        SELECT gi.name, gi.sales_partner AS sales_partner, gi.posting_date, gii.kadar, SUM(gii.qty) AS qty, gi.bundle FROM 
        `tabGold Invoice` gi
        JOIN `tabGold Invoice Item` gii ON gii.parent = gi.name

        WHERE DATE(gi.posting_date) >= DATE("{first_day}")
        AND DATE(gi.posting_date) <= DATE("{last_day}")

        AND gi.docstatus = 1

        {addons}

        GROUP BY gi.sales_partner, gii.kadar, gi.bundle
        ORDER BY gi.sales_partner, gi.posting_date 
    """, as_dict=1, debug=1)

def get_transfer_stock_data(first_day, last_day):
    return frappe.db.sql(f""" 
        SELECT ubss.item, sum(ubss.bruto) as bruto, ubs.`bundle`, ubs.`sales`, ubss.kadar, ubss.item
        FROM 
         `tabUpdate Bundle Stock` ubs 
        JOIN `tabUpdate Bundle Stock Sub` ubss ON ubss.parent = ubs.name 

        WHERE 
        DATE(ubs.date) >= DATE("{first_day}")
        AND DATE(ubs.date) <= DATE("{last_day}")
        AND ubss.bruto IS NOT NULL
        GROUP BY ubss.item, ubs.bundle, ubs.kadar
    """, as_dict=1, debug=1)

def create_pengembalian_dict(first_day, last_day):
    data_pengembalian = frappe.db.sql(f""" 
        SELECT ubs.`bundle`, ubs.`sales`, ubss.kadar, SUM(ubss.bruto)
        FROM 
         `tabUpdate Bundle Stock` ubs 
        JOIN `tabUpdate Bundle Stock Sub` ubss ON ubss.parent = ubs.name 

        WHERE 
        DATE(ubs.date) >= DATE("{first_day}")
        AND DATE(ubs.date) <= DATE("{last_day}")
        AND ubss.bruto IS NOT NULL
        GROUP BY ubs.bundle, ubss.kadar, ubs.`sales`;
    """)

    pengembalian_dict = {}
    for row in data_pengembalian:
        pengembalian_dict.setdefault((row[0], row[1], row[2]), 0)
        pengembalian_dict[(row[0], row[1], row[2])] += row[3]
    
    return pengembalian_dict

def create_pengembalian_doc(row, keluar, masuk, data_holiday, last_day, data_transfer_stock):
    new_doc = frappe.new_doc("Update Bundle Stock")
    set_pic_and_employee(new_doc, row.kadar)

    new_doc.date = getdate(last_day)
    new_doc.bundle = row.bundle
    new_doc.type = "Deduct Stock"
    
    new_doc.s_warehouse = "Stockist - LMS"
    new_doc.purpose = "Sales"
    new_doc.sales = row.sales_partner
    new_doc.warehouse = frappe.db.get_value("Sales Partner", new_doc.sales, "warehouse", cache=1)

    item = frappe.get_cached_doc("Item", {"kadar": row.kadar, "item_group": "Perhiasan", "item_group_parent": "Pembayaran"})

    maksimal_total = frappe.utils.flt(keluar) - frappe.utils.flt(masuk)

    new_doc.append("items", {
        "sub_category": "Perhiasan",
        "kadar": row.kadar,
        "qty_penambahan": maksimal_total,
        "item": item.name,
        "gold_selling_item": item.gold_selling_item
    })

    new_doc.append("per_kadar", {
        "kadar": row.kadar,
        "bruto": maksimal_total,
    })

    item_pengembalian = [
        {row_sub_category.item: row_sub_category.bruto}
        for row_sub_category in data_transfer_stock
        if row.kadar == row_sub_category.kadar and new_doc.bundle == row_sub_category.bundle
    ]

    maksimal_total += round(random.uniform(0.001, 0.01), 2)
    retur_result = generate_list_retur(item_pengembalian, maksimal_total)

    for per_item in retur_result:
        item, qty = list(per_item.items())[0]
        new_doc.append("per_sub_category", {
            "item": item,
            "item_name": frappe.db.get_value("Item", item, "item_name"),
            "bruto": frappe.utils.flt(qty),
            "kadar": row.kadar
        })

    new_doc.save()
    # Uncomment the line below if you want to create GDLE
    # create_gdle(new_doc)