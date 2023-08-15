# -*- coding: utf-8 -*-
# Copyright (c) 2021, PibiCo and contributors
# For license information, please see license.txt
import frappe
import base64
import io
import qrcode

@frappe.whitelist()
def get_qrcode(your_data):
    stream = io.BytesIO()
    img = qrcode.make(your_data)
    img.save(stream, 'PNG')
    data = base64.b64encode(stream.getvalue())
    return ('data:image/png;base64,{}').format(data.decode('UTF-8'))
    
    # print(img_tag)