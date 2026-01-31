import frappe
from frappe import _
from frappe.utils import get_url, nowdate

from erpnext.accounts.doctype.payment_request.payment_request import (
    PaymentRequest as OriginalPaymentRequest,
)


class PaymentRequest(OriginalPaymentRequest):
    """
    Extended Payment Request for Webshop manual payment approval workflow

    Workflow:
    - docstatus = 0 (Draft): Pending approval, customer can upload payment proof
    - docstatus = 1 (Submitted): Approved, marks payment as paid automatically
    - docstatus = 2 (Cancelled): Rejected, includes rejection reason in remarks
    """

    def validate(self):
        """Extended validation for webshop payment approval workflow"""
        super().validate()

        # Additional validation for webshop manual payments
        if self.is_webshop_manual_payment():
            self.validate_payment_proof_on_submit()

    def before_submit(self):
        """Capture admin approval metadata and set mode_of_payment before submission"""
        super().before_submit()

        if self.is_webshop_manual_payment():
            # Capture who approved and when
            self.admin_approval_by = frappe.session.user
            self.admin_approval_time = frappe.utils.now()
            
            # Get and set mode_of_payment from Webshop Payment Method
            # This must be done BEFORE submit to avoid UpdateAfterSubmitError
            if self.payment_method_type and not self.mode_of_payment:
                mode_of_payment = frappe.get_cached_value(
                    "Webshop Payment Method",
                    self.payment_method_type,
                    "mode_of_payment"
                )
                if mode_of_payment:
                    self.mode_of_payment = mode_of_payment

    def on_submit(self):
        """
        Override on_submit to mark payment as paid for approved manual payments

        For webshop manual payments (Transfer Manual with need_admin_approval),
        submission (docstatus=1) represents approval and triggers payment completion.
        """
        # Call parent's on_submit for standard Payment Request logic
        super().on_submit()

        # Additional logic for webshop manual payment approval
        if self.is_webshop_manual_payment():
            try:
                # Mark payment as paid - creates Payment Entry automatically
                # Payment Entry will use the mode_of_payment we set in before_submit
                self.set_as_paid()
                frappe.msgprint(
                    _("Payment marked as paid successfully"),
                    indicator="green",
                    alert=True
                )
            except Exception as e:
                frappe.log_error(
                    message=frappe.get_traceback(),
                    title=f"Failed to mark payment as paid for Payment Request {self.name}"
                )
                frappe.throw(_("Failed to mark payment as paid: {0}").format(str(e)))

    def on_cancel(self):
        """Capture admin info on rejection (cancellation)"""
        # Capture who rejected and when
        if not self.admin_approval_by:
            frappe.db.set_value(
                self.doctype,
                self.name,
                "admin_approval_by",
                frappe.session.user,
                update_modified=False
            )

        if not self.admin_approval_time:
            frappe.db.set_value(
                self.doctype,
                self.name,
                "admin_approval_time",
                frappe.utils.now(),
                update_modified=False
            )

        # Call parent's on_cancel
        super().on_cancel()

    def is_webshop_manual_payment(self):
        """
        Check if this is a webshop manual payment that needs admin approval

        Returns True if:
        - Payment Request has payment_method_type custom field set (NEW - supports all doctypes)
        - OR Reference doctype is Sales Order with order_type = "Shopping Cart"
        """
        # Check if this Payment Request has payment_method_type field (NEW)
        # This supports Sales Invoice, Sales Order, and any other reference doctype
        if hasattr(self, 'payment_method_type') and self.payment_method_type:
            needs_approval = frappe.get_cached_value(
                "Webshop Payment Method",
                self.payment_method_type,
                "need_admin_approval"
            )
            return bool(needs_approval)
        
        # Fallback to existing Sales Order logic for backward compatibility
        if self.reference_doctype != "Sales Order":
            return False

        # Check if Sales Order is from webshop
        sales_order = frappe.get_cached_value(
            "Sales Order",
            self.reference_name,
            ["order_type", "payment_method_type"],
            as_dict=1
        )

        if not sales_order or sales_order.get("order_type") != "Shopping Cart":
            return False

        # Check if payment method needs admin approval
        payment_method_type = sales_order.get("payment_method_type")
        if not payment_method_type:
            return False

        needs_approval = frappe.get_cached_value(
            "Webshop Payment Method",
            payment_method_type,
            "need_admin_approval"
        )

        return bool(needs_approval)

    def validate_payment_proof_on_submit(self):
        """Validate that payment proof is uploaded before approval"""
        if not self.payment_proof and self.docstatus == 1:
            frappe.msgprint(
                _("Payment proof is not uploaded. Please ensure customer has provided payment evidence."),
                indicator="orange",
                alert=True
            )

    def on_payment_authorized(self, status=None):
        if not status:
            return

        if status not in ("Authorized", "Completed"):
            return

        if not hasattr(frappe.local, "session"):
            return

        if frappe.local.session.user == "Guest":
            return

        cart_settings = frappe.get_doc("Webshop Settings")

        if not cart_settings.enabled:
            return

        success_url = cart_settings.payment_success_url
        redirect_to = get_url("/orders/{0}".format(self.reference_name))

        if success_url:
            redirect_to = (
                {
                    "Orders": "/orders",
                    "Invoices": "/invoices",
                    "My Account": "/me",
                }
            ).get(success_url, "/me")

        self.set_as_paid()

        return redirect_to

    @staticmethod
    def get_gateway_details(args):
        if args.order_type != "Shopping Cart":
            return super().get_gateway_details(args)

        cart_settings = frappe.get_doc("Webshop Settings")
        gateway_account = cart_settings.payment_gateway_account
        return super().get_payment_gateway_account(gateway_account)

    def get_payment_url(self):
        """
        Override to handle virtual account payment flow
        """
        # Check if this is a virtual account payment
        if hasattr(self, 'payment_gateway') and self.payment_gateway:
            from payments.utils import get_payment_gateway_controller
            controller = get_payment_gateway_controller(self.payment_gateway)

            # Prepare payment data
            payment_data = {
                "amount": self.grand_total,
                "title": self.subject or f"Payment for {self.reference_name}",
                "description": self.subject or f"Payment for {self.reference_name}",
                "reference_doctype": self.reference_doctype,
                "reference_docname": self.reference_name,
                "payer_email": self.email_to or frappe.session.user,
                "payer_name": self.party_name,
                "order_id": self.name,
                "currency": self.currency,
                "payment_gateway": self.payment_gateway,
                "payment_request_doc": self,  # Pass the document instance for direct modification
            }

            # Call the controller's get_payment_url method
            return controller.get_payment_url(**payment_data)

        # Fall back to original implementation
        return super().get_payment_url()
