import uuid

import logging
from yookassa import Payment

log = logging.getLogger(__name__)


class PaymentOrder:
    @staticmethod
    def get_payment_url(order, return_link):
        payment = Payment.create({
            "amount": {
                "value": order.total_price,
                "currency": "RUB",
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_link,
            },
            "capture": True,
            "description": f"Заказ № {order.pk} от пользователя {order.user.username}"
        }, uuid.uuid4())
        if payment["status"] == "pending":
            payment_link = payment["confirmation"]["confirmation_url"]
            order.payment_id = payment["id"]
            order.save()
            return payment_link
        else:
            log.error(f"Ошибка при создании платежа. Для заказа {order.pk} у пользователя {order.user.username}")
            return ""

    @staticmethod
    def check_paid_order(pay_id):
        payment_status = Payment.find_one(pay_id)
        if payment_status["paid"]:
            return True
        else:
            return False
