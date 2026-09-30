

from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from app.dependencies.auth_dependecy import require_user_id
from app.schemas.payment_schema import (
    PaymentCreateRequest,
    PaymentCreateResponse
)
from app.services.payment_service import create_payment_service, payment_success_service, payment_cancel_service, \
    payment_ipn_service, payment_fail_service

router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


@router.post(
    "/create",
    response_model=PaymentCreateResponse,
)
async def create_payment(
    request: PaymentCreateRequest,
    user_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db),
):
    payment = await create_payment_service(
        db=db,
        user_id=user_id,
        order_id=request.order_id,
        payment_method=request.payment_method,
    )

    return payment


@router.post("/success")
async def payment_success(
    tran_id: str = Form(...),
    val_id: str = Form(...),
    status: str = Form(...),
    db: AsyncSession = Depends(get_db),
):

    result = await payment_success_service(
        db=db,
        tran_id=tran_id,
        val_id=val_id,
        payment_status=status,
    )

    return result



@router.post("/fail")
async def payment_fail(
    tran_id: str,
    db: AsyncSession = Depends(get_db)
):
    result= await payment_fail_service(
        db=db,
        tran_id=tran_id
    )
    return result



@router.post("/cancel")
async def payment_cancel(
    tran_id: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    result = await payment_cancel_service(
        db=db,
        tran_id=tran_id,
    )

    return result


@router.post("/ipn")
async def payment_ipn(
    tran_id: str = Form(...),
    val_id: str = Form(None),
    status: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    result = await payment_ipn_service(
        db=db,
        tran_id=tran_id,
        val_id=val_id,
        payment_status=status,
    )

    return result