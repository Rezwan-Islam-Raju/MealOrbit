import httpx

from app.services.payment_service import SSLCOMMERZ_STORE_ID, SSLCOMMERZ_STORE_PASSWORD, SSLCOMMERZ_SUCCESS_URL, \
    SSLCOMMERZ_FAIL_URL, SSLCOMMERZ_CANCEL_URL, SSLCOMMERZ_IPN_URL, SSLCOMMERZ_PAYMENT_URL


async def initiate_sslcommerz_payment(
    payment_id: int,
    order_id: int,
    amount: float
):
    tran_id = f"PAY-{payment_id}-ORDER-{order_id}"

    payload = {
        "store_id": SSLCOMMERZ_STORE_ID,
        "store_passwd": SSLCOMMERZ_STORE_PASSWORD,
        "total_amount": amount,
        "currency": "BDT",

        "tran_id": tran_id,

        "success_url": SSLCOMMERZ_SUCCESS_URL,
        "fail_url": SSLCOMMERZ_FAIL_URL,
        "cancel_url": SSLCOMMERZ_CANCEL_URL,
        "ipn_url": SSLCOMMERZ_IPN_URL,

        "cus_name": "Customer",
        "cus_email": "customer@example.com",
        "cus_add1": "Dhaka",
        "cus_city": "Dhaka",
        "cus_country": "Bangladesh",
        "cus_phone": "01700000000",

        "shipping_method": "NO",
        "product_name": "Ecommerce Order",
        "product_category": "General",
        "product_profile": "general"
    }

    async with httpx.AsyncClient() as client:

        response = await client.post(
            SSLCOMMERZ_PAYMENT_URL,
            data=payload,
        )

        response.raise_for_status()

        return response.json()

