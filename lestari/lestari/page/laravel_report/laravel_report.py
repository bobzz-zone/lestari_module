# Copyright (c) 2021, Patrick Stuhlmüller and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import requests
import json

# url = "http://lestarigold.co.id:8282"
# endpoint = "/api/v1/employee-statistics-with-range"

@frappe.whitelist()
def contoh_report():
    url = "http://192.168.3.100:8282/api/v1/employee-statistics-with-range?idEmployee=1793&operation=Poles%20Manual&dateStart=2023-07-01&dateEnd=2023-07-30"
    request = requests.get(url)
    # response = request.json
    print(request.status_code)
    return request