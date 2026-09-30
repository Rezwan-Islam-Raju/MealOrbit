from decimal import Decimal

import httpx
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.pubsub import publish_message
from app.models.user_model import User
from app.models.order_model import Order, OrderStatus
from app.models.payment_model import Payment

from config.config import (
    SSLCOMMERZ_PAYMENT_URL,
    SSLCOMMERZ_IPN_URL,
    SSLCOMMERZ_CANCEL_URL,
    SSLCOMMERZ_FAIL_URL,
    SSLCOMMERZ_SUCCESS_URL,
    SSLCOMMERZ_STORE_ID,
    SSLCOMMERZ_STORE_PASSWORD,
    SSLCOMMERZ_VALIDATION_URL,
    generate_transaction_id,
)



# CREATE PAYMENT


async def create_payment_service(
    db: AsyncSession,
    user_id: int,
    order_id: int,
    payment_method: str,
):


    #  Normalize payment method


    payment_method = payment_method.strip().lower()

    if payment_method != "sslcommerz":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment method must be sslcommerz",
        )


    # Find user's order


    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.user_id == user_id,
        )
    )

    order = result.scalar_one_or_none()

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )


    #  Validate order status


    if order.status not in (
        OrderStatus.PENDING,
        OrderStatus.CONFIRMED,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Payment cannot be created for order "
                f"with status '{order.status.value}'"
            ),
        )


    #  Get user


    result = await db.execute(
        select(User).where(
            User.id == user_id
        )
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


    #  Check existing payment


    result = await db.execute(
        select(Payment).where(
            Payment.order_id == order.id,
            Payment.status.in_(
                [
                    "pending",
                    "processing",
                    "paid",
                ]
            ),
        )
    )

    existing_payment = result.scalar_one_or_none()

    if existing_payment is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment already exists for this order",
        )


    #  Generate transaction ID


    transaction_id = generate_transaction_id()


    #  Create pending payment

    payment = Payment(
        order_id=order.id,
        amount=order.total_amount,
        payment_method="sslcommerz",
        transaction_id=transaction_id,
        status="pending",
    )

    db.add(payment)

    try:

        await db.commit()
        await db.refresh(payment)

    except Exception:

        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment",
        )


    #  Customer information


    full_name = (
        f"{user.first_name} {user.last_name}"
        .strip()
    )

    if not full_name:
        full_name = "Customer"

    email = user.email

    phone = getattr(user, "phone", None)

    if not phone:
        phone = "01700000000"


    # 9. Payment amount


    amount = Decimal(
        str(order.total_amount)
    )


    #  SSLCOMMERZ payload


    payload = {
        "store_id": SSLCOMMERZ_STORE_ID,
        "store_passwd": SSLCOMMERZ_STORE_PASSWORD,

        "total_amount": f"{amount:.2f}",
        "currency": "BDT",

        "tran_id": transaction_id,

        "success_url": SSLCOMMERZ_SUCCESS_URL,
        "fail_url": SSLCOMMERZ_FAIL_URL,
        "cancel_url": SSLCOMMERZ_CANCEL_URL,
        "ipn_url": SSLCOMMERZ_IPN_URL,

        "cus_name": full_name,
        "cus_email": email,
        "cus_phone": phone,

        "cus_add1": "Dhaka",
        "cus_city": "Dhaka",
        "cus_country": "Bangladesh",

        "shipping_method": "NO",

        "product_name": "Ecommerce Order",
        "product_category": "General",
        "product_profile": "general",
    }


    #  Call SSLCOMMERZ


    try:

        async with httpx.AsyncClient() as client:

            response = await client.post(
                SSLCOMMERZ_PAYMENT_URL,
                data=payload,
                timeout=30,
            )

            response.raise_for_status()

            response_data = response.json()

    except (
        httpx.HTTPStatusError,
        httpx.RequestError,
        ValueError,
    ):

        payment.status = "failed"

        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="SSLCOMMERZ API Error",
        )


    #  Check SSLCOMMERZ response


    if response_data.get("status") != "SUCCESS":

        payment.status = "failed"

        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                response_data.get("failedreason")
                or
                "SSLCOMMERZ payment "
                "initialization failed"
            ),
        )


    #  Get payment URL


    payment_url = response_data.get(
        "GatewayPageURL"
    )

    if not payment_url:

        payment.status = "failed"

        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "SSLCOMMERZ did not return "
                "payment URL"
            ),
        )


    #  Return payment information


    return {
        "payment_id": payment.id,
        "order_id": payment.order_id,
        "amount": float(payment.amount),
        "transaction_id": payment.transaction_id,
        "payment_url": payment_url,
        "status": payment.status,
    }



# PAYMENT SUCCESS CALLBACK

async def payment_success_service(
    db: AsyncSession,
    tran_id: str,
    val_id: str,
    payment_status: str,
):
    print("Callback status:", payment_status)

    # Find payment using transaction ID
    result = await db.execute(
        select(Payment).where(
            Payment.transaction_id == tran_id
        )
    )

    payment = result.scalar_one_or_none()

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    # Prevent duplicate payment confirmation
    if payment.status == "paid":
        return {
            "message": "Payment already confirmed",
            "payment_id": payment.id,
            "order_id": payment.order_id,
            "transaction_id": payment.transaction_id,
            "status": payment.status,
        }

    # Validate val_id
    if not val_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Validation ID is required",
        )

    # Find order
    result = await db.execute(
        select(Order).where(
            Order.id == payment.order_id
        )
    )

    order = result.scalar_one_or_none()

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    # SSLCOMMERZ Validation API
    validation_params = {
        "val_id": val_id,
        "store_id": SSLCOMMERZ_STORE_ID,
        "store_passwd": SSLCOMMERZ_STORE_PASSWORD,
        "format": "json",
    }

    try:
        async with httpx.AsyncClient() as client:

            response = await client.get(
                SSLCOMMERZ_VALIDATION_URL,
                params=validation_params,
                timeout=30,
            )

            response.raise_for_status()

            validation_data = response.json()

    except (
        httpx.HTTPStatusError,
        httpx.RequestError,
        ValueError,
    ):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="SSLCOMMERZ validation failed",
        )

    # Check SSLCOMMERZ validation status
    ssl_status = validation_data.get("status")

    if ssl_status not in (
        "VALID",
        "VALIDATED",
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "SSLCOMMERZ payment validation failed: "
                f"{ssl_status}"
            ),
        )

    # Verify transaction ID
    validated_tran_id = validation_data.get("tran_id")

    if not validated_tran_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction ID missing from SSLCOMMERZ validation",
        )

    if validated_tran_id != payment.transaction_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction ID verification failed",
        )

    # Verify amount
    validated_amount_raw = validation_data.get("amount")

    if validated_amount_raw is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount missing from SSLCOMMERZ validation",
        )

    try:
        validated_amount = Decimal(
            str(validated_amount_raw)
        )

        payment_amount = Decimal(
            str(payment.amount)
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment amount received from SSLCOMMERZ",
        )

    if validated_amount != payment_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount verification failed",
        )

    # Verify currency
    currency = validation_data.get("currency")

    if currency != "BDT":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment currency verification failed",
        )

    # Mark payment as paid
    payment.status = "paid"

    # Confirm order
    order.status = OrderStatus.CONFIRMED

    # Save changes
    try:
        await db.commit()

        await db.refresh(payment)
        await db.refresh(order)

    except Exception:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to confirm payment",
        )

    # Publish payment notification event
    await publish_message(
        "notification_channel",
        {
            "user_id": order.user_id,
            "title": "Payment Successful",
            "message": f"Payment for order #{order.id} was successful.",
            "notification_type": "PAYMENT",
        },
    )

    # Return response
    return {
        "message": "Payment successfully verified",
        "payment_id": payment.id,
        "order_id": order.id,
        "transaction_id": payment.transaction_id,
        "status": payment.status,
        "order_status": order.status.value,
        "validation_status": ssl_status,
    }


# PAYMENT FAIL CALLBACK

async def payment_fail_service(
    db: AsyncSession,
    tran_id: str,
):
    # Find payment
    result = await db.execute(
        select(Payment).where(
            Payment.transaction_id == tran_id
        )
    )

    payment = result.scalar_one_or_none()

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    # Already paid payment cannot become failed
    if payment.status == "paid":
        return {
            "message": "Payment already confirmed",
            "payment_id": payment.id,
            "order_id": payment.order_id,
            "transaction_id": payment.transaction_id,
            "status": payment.status,
        }

    # Mark payment as failed
    payment.status = "failed"

    try:
        await db.commit()
        await db.refresh(payment)

    except Exception:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update payment status",
        )

    return {
        "message": "Payment failed",
        "payment_id": payment.id,
        "order_id": payment.order_id,
        "transaction_id": payment.transaction_id,
        "status": payment.status,
    }



# PAYMENT CANCEL CALLBACK

async def payment_cancel_service(
    db: AsyncSession,
    tran_id: str,
):
    # Find payment
    result = await db.execute(
        select(Payment).where(
            Payment.transaction_id == tran_id
        )
    )

    payment = result.scalar_one_or_none()

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    # Already paid payment cannot become cancelled
    if payment.status == "paid":
        return {
            "message": "Payment already confirmed",
            "payment_id": payment.id,
            "order_id": payment.order_id,
            "transaction_id": payment.transaction_id,
            "status": payment.status,
        }

    # Mark payment as cancelled
    payment.status = "cancelled"

    try:
        await db.commit()
        await db.refresh(payment)

    except Exception:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update payment status",
        )

    return {
        "message": "Payment cancelled",
        "payment_id": payment.id,
        "order_id": payment.order_id,
        "transaction_id": payment.transaction_id,
        "status": payment.status,
    }



# PAYMENT IPN

async def payment_ipn_service(
    db: AsyncSession,
    tran_id: str,
    val_id: str,
    payment_status: str,
):
    # Find payment
    result = await db.execute(
        select(Payment).where(
            Payment.transaction_id == tran_id
        )
    )

    payment = result.scalar_one_or_none()

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    # Already paid
    if payment.status == "paid":
        return {
            "message": "Payment already confirmed",
            "payment_id": payment.id,
            "order_id": payment.order_id,
            "transaction_id": payment.transaction_id,
            "status": payment.status,
        }

    # IPN status must be successful
    if payment_status != "VALID":
        if payment_status == "FAILED":
            payment.status = "failed"

        elif payment_status == "CANCELLED":
            payment.status = "cancelled"

        elif payment_status in ("EXPIRED", "UNATTEMPTED"):
            payment.status = "failed"

        else:
            return {
                "message": "Payment status not processed",
                "payment_id": payment.id,
                "transaction_id": payment.transaction_id,
                "status": payment_status,
            }

        await db.commit()
        await db.refresh(payment)

        return {
            "message": "Payment status updated",
            "payment_id": payment.id,
            "order_id": payment.order_id,
            "transaction_id": payment.transaction_id,
            "status": payment.status,
        }

    # val_id required for successful transaction
    if not val_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Validation ID is required",
        )

    # Find order
    result = await db.execute(
        select(Order).where(
            Order.id == payment.order_id
        )
    )

    order = result.scalar_one_or_none()

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    # Validate with SSLCOMMERZ
    validation_params = {
        "val_id": val_id,
        "store_id": SSLCOMMERZ_STORE_ID,
        "store_passwd": SSLCOMMERZ_STORE_PASSWORD,
        "format": "json",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                SSLCOMMERZ_VALIDATION_URL,
                params=validation_params,
                timeout=30,
            )

            response.raise_for_status()

            validation_data = response.json()

    except (
        httpx.HTTPStatusError,
        httpx.RequestError,
        ValueError,
    ):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="SSLCOMMERZ validation failed",
        )

    # Check validation status
    ssl_status = validation_data.get("status")

    if ssl_status not in (
        "VALID",
        "VALIDATED",
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "SSLCOMMERZ payment validation failed: "
                f"{ssl_status}"
            ),
        )

    # Verify transaction ID
    validated_tran_id = validation_data.get("tran_id")

    if validated_tran_id != payment.transaction_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction ID verification failed",
        )

    # Verify amount
    validated_amount_raw = validation_data.get("amount")

    if validated_amount_raw is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount missing from SSLCOMMERZ validation",
        )

    try:
        validated_amount = Decimal(
            str(validated_amount_raw)
        )

        payment_amount = Decimal(
            str(payment.amount)
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment amount",
        )

    if validated_amount != payment_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount verification failed",
        )

    # Verify currency
    if validation_data.get("currency") != "BDT":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment currency verification failed",
        )

    # Mark paid
    payment.status = "paid"
    order.status = OrderStatus.CONFIRMED

    try:
        await db.commit()

        await db.refresh(payment)
        await db.refresh(order)

    except Exception:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to confirm IPN payment",
        )

    return {
        "message": "IPN payment successfully verified",
        "payment_id": payment.id,
        "order_id": order.id,
        "transaction_id": payment.transaction_id,
        "status": payment.status,
        "order_status": order.status.value,
        "validation_status": ssl_status,
    }