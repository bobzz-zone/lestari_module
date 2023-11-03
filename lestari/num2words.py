import frappe
from num2words import num2words

@frappe.whitelist()
def get_num2words(number):
	return num2words(number, to='currency', lang='id').title()