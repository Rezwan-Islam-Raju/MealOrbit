from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth_dependecy import require_user_id
from app.schemas.coupon_schema import CouponResponse, CouponCreateRequest
from app.services.coupon_service import create_coupon_service, get_coupons_service
from config.database import get_db

router = APIRouter()

#--------- CREATE COUPON API -------------

@router.post("/", response_model=CouponResponse)
async def create_coupon(
    request: CouponCreateRequest,
    admin_id: int = Depends(require_user_id),
    db: AsyncSession = Depends(get_db)
):
    result = await create_coupon_service(
        db=db,
        admin_id=admin_id,
        request=request

    )
    return result


#------- GET COUPONS API ---------

@router.get("/", response_model=list[CouponResponse])
async def get_coupons(
        db: AsyncSession = Depends(get_db)
):
    result= await get_coupons_service(
        db=db
    )
    return result