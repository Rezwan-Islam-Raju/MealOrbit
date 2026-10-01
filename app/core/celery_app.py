from celery import Celery

from app.utils.email import send_email


celery_app = Celery(
    "food_delivery",
    broker="amqp://guest:guest@localhost:5672//",
    backend="rpc://",
)


celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Dhaka",
    enable_utc=False
)

#--------- General Email Notification --------

@celery_app.task
def send_notification_email(
    email: str,
    title: str,
    message: str
):
    send_email(
        to_email=email,
        subject=title,
        body=message
    )



#--------- ------ Order Confirmation Email -------------

@celery_app.task(
    name="send_order_confirmation_email"
)
def send_order_confirmation_email(
    customer_email: str,
    order_id: int,
    order_items: list[dict],
):
    items_text = "\n".join(
        f"• {item['food_name']} × {item['quantity']}"
        for item in order_items
    )

    subject = f"Order #{order_id} Confirmed"

    message = f"""
🎉 Order Confirmed!

Your order #{order_id} has been confirmed successfully.

Order Details:
{items_text}

💳 Please complete your payment to start preparing your order.

Once your payment is successful, the restaurant will begin preparing your order.

Thank you for ordering with us! ❤️

We hope you enjoy your meal.

Best regards,
Food Delivery Team
"""

    send_email(
        to_email=customer_email,
        subject=subject,
        body=message
    )

    return {
        "order_id": order_id,
        "status": "success"
    }



#------------ ------ Order Status Notification -------------

@celery_app.task(
    name="send_order_status_notification"
)
def send_order_status_notification(
    user_id: int,
    order_id: int,
    new_status: str,
):
    notifications = {

        # Preparing

        "PREPARING": {
            "title": "Order Preparing",
            "message": (
                f"Your order #{order_id} is now being "
                "prepared by the restaurant."
            ),
        },

        # Ready

        "READY": {
            "title": "Order Ready",
            "message": (
                f"Your order #{order_id} is ready for pickup. "
                "Thank you for ordering with us!"
            ),
        },

        # Rider Assigned

        "RIDER_ASSIGNED": {
            "title": "Rider Assigned",
            "message": (
                f"A rider has been assigned to your "
                f"order #{order_id}. "
                "Your food will be delivered soon."
            ),
        },

        # Cancelled

        "CANCELLED": {
            "title": "Order Cancelled",
            "message": (
                f"Your order #{order_id} has been cancelled. "
                "If you have already completed the payment, "
                "please check your payment or refund status."
            ),
        },
    }

    notification = notifications.get(new_status)

    if not notification:
        return {
            "success": False,
            "message": (
                f"No notification configured "
                f"for status {new_status}"
            ),
        }

    notification_data = {
        "user_id": user_id,
        "order_id": order_id,
        "title": notification["title"],
        "message": notification["message"],
        "notification_type": "ORDER",
    }

    print(
        f"ORDER NOTIFICATION: {notification_data}"
    )

    return {
        "success": True,
        "notification": notification_data
    }

