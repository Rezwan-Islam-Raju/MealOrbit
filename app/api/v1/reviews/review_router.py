from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.riview_schema import ReviewResponse, ReviewCreateRequest, ReviewUpdateRequest
from config.database import get_db

from app.dependencies.auth_dependecy import require_user_id



from app.services.review_service import (
    create_review_service,
    get_review_by_id_service,
    get_food_reviews_service,
    get_my_reviews_service,
    update_review_service,
    delete_review_service,
)


router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"],
)


#---------- CREATE REVIEW API ----------
@router.post(
    "/",
    response_model=ReviewResponse
)
async def create_review(
    request: ReviewCreateRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(require_user_id)
):
    result= await create_review_service(
        db=db,
        user_id=user_id,
        request=request
    )
    return result


#--------- GET MY REVIEWS API ----------
@router.get(
    "/my",
    response_model=List[ReviewResponse]
)
async def get_my_reviews(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(require_user_id)
):
    result= await get_my_reviews_service(
        db=db,
        user_id=user_id
    )
    return result


#----------- GET FOOD REVIEWS API -----------
@router.get(
    "/food/{food_id}",
    response_model=List[ReviewResponse]
)
async def get_food_reviews(
    food_id: int,
    db: AsyncSession = Depends(get_db),
):
    result= await get_food_reviews_service(
        db=db,
        food_id=food_id
    )
    return result


#------------ GET REVIEW API ----------

@router.get(
    "/{review_id}",
    response_model=ReviewResponse
)
async def get_review(
    review_id: int,
    db: AsyncSession = Depends(get_db)
):
    result= await get_review_by_id_service(
        db=db,
        review_id=review_id
    )
    return result


#----------- UPDATE REVIEW API ----------

@router.put(
    "/{review_id}",
    response_model=ReviewResponse,
)
async def update_review(
    review_id: int,
    request: ReviewUpdateRequest,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(require_user_id)
):
    result= await update_review_service(
        db=db,
        user_id=user_id,
        review_id=review_id,
        request=request
    )
    return result


#----------- DELETE REVIEW API -----------

@router.delete(
    "/{review_id}",
)
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(require_user_id)
):
    result= await delete_review_service(
        db=db,
        user_id=user_id,
        review_id=review_id
    )
    return result

