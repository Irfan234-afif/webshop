# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# License: MIT. See LICENSE

import frappe


def get_context(context):
    """
    Get context for Midtrans checkout page
    """
    context.no_cache = 1

    # Get token from query string
    token = frappe.form_dict.get("token")

    if not token:
        frappe.throw("Invalid payment request")

    context.token = token

    # Get payment details
    try:
        from webshop.webshop.doctype.midtrans_settings.midtrans_settings import get_checkout_details
        context.payment_details = get_checkout_details(token)
    except Exception as e:
        frappe.log_error(frappe.get_traceback())
        frappe.throw("Unable to load payment details")

    return context
