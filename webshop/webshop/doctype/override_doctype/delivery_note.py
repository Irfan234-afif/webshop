import frappe
from frappe import _
from erpnext.stock.doctype.delivery_note.delivery_note import DeliveryNote, make_sales_invoice

class WebshopDeliveryNote(DeliveryNote):
	def make_return_invoice(self):
		try:
			return_invoice = make_sales_invoice(self.name)
			return_invoice.is_return = True
			return_invoice.update_billed_amount_in_sales_order = 1
			return_invoice.save()
			return_invoice.submit()

			credit_note_link = frappe.utils.get_link_to_form("Sales Invoice", return_invoice.name)

			frappe.msgprint(_("Credit Note {0} has been created automatically").format(credit_note_link))
		except Exception:
			frappe.throw(
				_(
					"Could not create Credit Note automatically, please uncheck 'Issue Credit Note' and submit again"
				)
			)
