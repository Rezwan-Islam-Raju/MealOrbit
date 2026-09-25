from decimal import Decimal

import httpx
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.models import User
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


    #  Find payment using transaction ID


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


    #  Already paid

    if payment.status == "paid":

        return {
            "message": "Payment already confirmed",
            "payment_id": payment.id,
            "order_id": payment.order_id,
            "transaction_id": payment.transaction_id,
            "status": payment.status,
        }


    #  Callback status check

    if payment_status.lower() != "success":

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment was not successful",
        )


    #  Validate val_id


    if not val_id:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Validation ID is required",
        )


    #  Find order


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


    #  SSLCOMMERZ VALIDATION


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


    #  Check validation status


    ssl_status = validation_data.get(
        "status"
    )

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


    #  Verify transaction ID


    validated_tran_id = validation_data.get(
        "tran_id"
    )

    if validated_tran_id != payment.transaction_id:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction ID verification failed",
        )


    #  Verify amount


    validated_amount = Decimal(
        str(
            validation_data.get(
                "amount"
            )
        )
    )

    payment_amount = Decimal(
        str(payment.amount)
    )

    if validated_amount != payment_amount:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount verification failed",
        )


    #  Verify currency


    currency = validation_data.get(
        "currency"
    )

    if currency != "BDT":

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment currency verification failed",
        )


    # MARK PAYMENT AS PAID


    payment.status = "paid"


    #  CONFIRM ORDER


    order.status = OrderStatus.CONFIRMED


    #  SAVE


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


    #  RETURN


    return {
        "message": "Payment successfully verified",

        "payment_id": payment.id,

        "order_id": order.id,

        "transaction_id": payment.transaction_id,

        "status": payment.status,

        "order_status": order.status.value,

        "validation_status": ssl_status,
    }