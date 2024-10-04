import frappe
from frappe.utils import getdate
from frappe import db, msgprint, throw
from datetime import datetime, timedelta, date
import pandas as pd
import random
from faker import Faker

# Date utility functions
def get_monday_of_date(date_str):
    """Get the Monday of the week for the given date."""
    tgl = datetime.strptime(date_str, '%Y-%m-%d')
    offset = (tgl.weekday() - 0) % 7
    monday = tgl - timedelta(days=offset)
    return monday.strftime('%Y-%m-%d')

def last_day_of_month(any_day):
    """Get the last day of the month for the given date."""
    next_month = any_day.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)

def first_day_of_month(any_day):
    """Get the first day of the month for the given date."""
    return any_day.replace(day=1)

# Holiday and Calendar functions
def fetch_holidays():
    """Fetch holiday dates from the database."""
    return db.sql("SELECT holiday_date FROM `tabHoliday`", as_dict=True)

def print_calendar(str_start_date, str_end_date, data_holiday, senin):
    """Generate a date for a specific event while considering holidays."""
    final_date = ""
    start_date = datetime.strptime(str_start_date, '%Y-%m-%d')
    end_date = datetime.strptime(str_end_date, '%Y-%m-%d') - timedelta(days=1)

    while True:
        if not final_date:
            final_date = get_monday_of_date(str_end_date)

        if final_date not in [str(holiday.holiday_date) for holiday in data_holiday]:
            return str(final_date)
        
        final_date = fake.date_between(start_date=start_date, end_date=end_date)

# Debugging functions
@frappe.whitelist()
def debug_print_calendar():
    """Debug function to print calendar."""
    data_holiday = fetch_holidays()
    print_calendar("2024-01-01", "2024-01-18", data_holiday)

# Main generation function
@frappe.whitelist()
def start_generate(year, month, bundle=None):
    """Initiate the generation of invoices for a specified month and year."""
    msgprint("-- Initiate Generate --")
    
    # Ensure year and month_number are integers
    year = int(year)  # Convert year to integer
    month_number = month_to_number(month)  # This should return an integer

    # Check if month_number is valid
    if month_number == 0:
        throw("Invalid month name provided.")

    first_day = first_day_of_month(datetime(year, month_number, 1))
    last_day = last_day_of_month(datetime(year, month_number, 1))

    addons = f" AND gi.bundle = '{bundle}'" if bundle else ""

    gold_invoices = fetch_gold_invoices(first_day, last_day, addons)
    data_holiday = fetch_holidays()
    
    # Process gold invoices
    process_gold_invoices(gold_invoices, first_day, last_day, data_holiday)

def month_to_number(month_name):
    """Convert month name to month number."""
    months = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12
    }
    return months.get(month_name, 0)  # Return 0 if month_name is invalid

def fetch_gold_invoices(first_day, last_day, addons):
    """Fetch gold invoices from the database."""
    query = f"""
        SELECT gi.name, gi.sales_partner, gi.posting_date, gii.kadar, SUM(gii.qty) as qty, gi.bundle
        FROM `tabGold Invoice` gi
        JOIN `tabGold Invoice Item` gii ON gii.parent = gi.name
        WHERE DATE(gi.posting_date) BETWEEN DATE('{first_day}') AND DATE('{last_day}')
        AND gi.docstatus = 1
        {addons}
        GROUP BY gi.sales_partner, gii.kadar, gi.bundle
        ORDER BY gi.sales_partner, gi.posting_date
    """
    return db.sql(query, as_dict=True)

def process_gold_invoices(invoices, first_day, last_day, data_holiday):
    """Process each gold invoice and create stock updates."""
    for row in invoices:
        new_doc = create_update_bundle_stock(row)
        
        # Additional processing
        # ...

def create_update_bundle_stock(row, is_deduct=False):
    """Create a new Update Bundle Stock document."""
    # Create a new document of type Update Bundle Stock
    new_doc = frappe.new_doc("Update Bundle Stock")
    
    # Set basic fields
    new_doc.bundle = row.bundle
    new_doc.s_warehouse = "Stockist - LMS"
    new_doc.purpose = "Sales"
    new_doc.sales = row.sales_partner
    new_doc.warehouse = frappe.db.get_value("Sales Partner", new_doc.sales, "warehouse", cache=1)

    # Set the appropriate employee information based on the 'kadar'
    new_doc.update(get_employee_info(row.kadar))

    # Retrieve the item associated with the 'kadar'
    item = get_item_by_kadar(row.kadar)
    if item:
        new_doc.append("items", {
            "sub_category": "Perhiasan",
            "kadar": row.kadar,
            "qty_penambahan": row.qty,
            "item": item.name,
            "gold_selling_item": item.gold_selling_item
        })
    else:
        throw(f"Item not found for kadar {row.kadar}")

    # Set the 'type' field based on whether it's a deduction or addition
    new_doc.type = "Deduct" if is_deduct else "Add Stock"

    # Save the document and commit the changes
    new_doc.save()
    frappe.db.commit()

    return new_doc

def determine_type(row):
    """Determine the type based on your business logic."""
    # Implement your logic to set the type here. For example:
    if row.qty > 0:
        return "New Stock"
    else:
        return "Add Stock"

def get_employee_info(kadar):
    """Return employee information based on the item 'kadar'."""
    employee_mapping = {
        "06K": {"pic": "HR-EMP-00489", "id_employee": 1240},
        "08K": {"pic": "HR-EMP-00485", "id_employee": 1147},
        "16K": {"pic": "HR-EMP-00486", "id_employee": 1194},
        "17K": {"pic": "HR-EMP-00487", "id_employee": 1225},
        "19K": {"pic": "HR-EMP-00487", "id_employee": 1225},
        "20K": {"pic": "HR-EMP-00487", "id_employee": 1225},
        "10K": {"pic": "HR-EMP-00487", "id_employee": 1225},
        "08KP": {"pic": "HR-EMP-00487", "id_employee": 1225},
        "PCB": {"pic": "HR-EMP-00490", "id_employee": 1656},
        "17KP": {"pic": "HR-EMP-00490", "id_employee": 1656},
    }
    return employee_mapping.get(kadar, {})

def get_item_by_kadar(kadar):
    """Fetch the item based on the 'kadar'."""
    return frappe.get_cached_doc("Item", {"kadar": kadar, "item_group": "Perhiasan", "item_group_parent": "Pembayaran"})

# Randomization and return handling functions
def randomizer(input_warehouse, input_kadar, kebutuhan, type, kadar, bundle, tanggal):
    """Randomly select items from inventory based on criteria."""
    list_item = fetch_available_items(input_warehouse, input_kadar, tanggal)
    total_item = sum(frappe.utils.flt(row[1]) for row in list_item)

    kebutuhan_min = kebutuhan * 1.10
    kebutuhan_max = min(kebutuhan * 1.20, total_item)

    if total_item < kebutuhan:
        throw(f"Insufficient items with kadar {kadar} in warehouse. Available: {total_item}")

    return generate_random_selection(list_item, kebutuhan_min, kebutuhan_max)

def fetch_available_items(warehouse, kadar, tanggal):
    """Fetch available items from the stock ledger."""
    query = f"""
        SELECT tb.item_code, tb.qty_after_transaction
        FROM `tabStock Ledger Entry` tb
        JOIN `tabItem` ti ON ti.name = tb.item_code
        WHERE tb.qty_after_transaction > 0
        AND tb.warehouse = '{warehouse}'
        AND ti.barang_yang_dibawa_sales = 1
        AND ti.kadar = '{kadar}'
        AND tb.posting_date < '{tanggal}'
    """
    return db.sql(query)

def generate_random_selection(list_item, kebutuhan_min, kebutuhan_max):
    """Generate a random selection of items within the specified range."""
    result_list = []
    total_selected = 0

    random.shuffle(list_item)
    for item_code, actual_qty in list_item:
        if total_selected >= kebutuhan_max:
            break
        
        qty_to_select = round(random.uniform(0, min(actual_qty, kebutuhan_max - total_selected)), 2)
        if qty_to_select > 0:
            result_list.append([item_code, qty_to_select])
            total_selected += qty_to_select

    if total_selected < kebutuhan_min:
        throw("Unable to meet minimum quantity requirements.")

    return result_list