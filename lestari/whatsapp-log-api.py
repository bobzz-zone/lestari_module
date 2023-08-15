# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import json

import frappe
import frappe.utils
from werkzeug.wrappers import Response

@frappe.whitelist(allow_guest=True)
def whatssapp_log():
    req = frappe.request
    token = 'cek'
    if(req.method == 'GET'):
        mode = str(frappe.request.args['hub.mode'])
        if (req.args["hub.mode"] == "subscribe" and req.args["hub.verify_token"] == token):
            return Response(req.args["hub.challenge"])
    if(req.method == 'POST'):
        tmp = json.loads(frappe.request.data)
        doc_t = frappe.new_doc('Whatsapp Log')
        doc_t.log = """ {} """.format(tmp)
        doc_t.save(ignore_permissions=True)