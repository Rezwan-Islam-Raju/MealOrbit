from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from app.models.review_model import Review
from app.models.food_model import Food
from app.models.order_model import Order
from app.schemas.riview_schema import ReviewCreateRequest, ReviewUpdateRequest



async def create_review_service(
    db: AsyncSession,
    user_id: int,
    request: ReviewCreateRequest,
):
    # Check order belongs to logged-in user
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.items)
        )
        .where(
            Order.id == request.order_id,
            Order.user_id == user_id,
        )
    )

    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    # Check food exists
    result = await db.execute(
        select(Food).where(
            Food.id == request.food_id
        )
    )

    food = result.scalar_one_or_none()

    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food not found",
        )

    # Check food belongs to the order
    food_exists_in_order = any(
        item.food_id == request.food_id
        for item in order.items
    )

    if not food_exists_in_order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This food does not belong to this order",
        )

    # Check duplicate review
    result = await db.execute(
        select(Review).where(
            Review.user_id == user_id,
            Review.food_id == request.food_id,
            Review.order_id == request.order_id,
        )
    )

    existing_review = result.scalar_one_or_none()

    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already reviewed this food for this order",
        )

    review = Review(
        user_id=user_id,
        food_id=request.food_id,
        order_id=request.order_id,
        rating=request.rating,
        comment=request.comment.strip()
        if request.comment
        else None,
    )

    db.add(review)

    await db.commit()
    await db.refresh(review)

    return review


async def get_review_by_id_service(
    db: AsyncSession,
    review_id: int,
):
    result = await db.execute(
        select(Review)
        .options(
            selectinload(Review.user),
            selectinload(Review.food),
            selectinload(Review.order),
        )
        .where(
            Review.id == review_id
        )
    )

    review = result.scalar_one_or_none()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    return review


async def get_food_reviews_service(
    db: AsyncSession,
    food_id: int,
):

    # 1. Check food exists


    result = await db.execute(
        select(Food).where(
            Food.id == food_id
        )
    )

    food = result.scalar_one_or_none()

    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food not found",
        )


    # 2. Get reviews


    result = await db.execute(
        select(Review)
        .where(
            Review.food_id == food_id
        )
        .order_by(
            Review.created_at.desc()
        )
    )

    return result.scalars().all()


# GET MY REVIEWS


async def get_my_reviews_service(
    db: AsyncSession,
    user_id: int,
):
    result = await db.execute(
        select(Review)
        .where(
            Review.user_id == user_id
        )
        .order_by(
            Review.created_at.desc()
        )
    )

    return result.scalars().all()



# UPDATE REVIEW


async def update_review_service(
    db: AsyncSession,
    user_id: int,
    review_id: int,
    request: ReviewUpdateRequest,
):

    # 1. Find user's review


    result = await db.execute(
        select(Review).where(
            Review.id == review_id,
            Review.user_id == user_id,
        )
    )

    review = result.scalar_one_or_none()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )


    # 2. Update rating


    if request.rating is not None:
        review.rating = request.rating


    # 3. Update comment


    if request.comment is not None:
        comment = request.comment.strip()

        review.comment = comment if comment else None


    # 4. Save changes


    await db.commit()
    await db.refresh(review)

    return review



# DELETE REVIEW


async def delete_review_service(
    db: AsyncSession,
    user_id: int,
    review_id: int,
):

    # 1. Find user's review


    result = await db.execute(
        select(Review).where(
            Review.id == review_id,
            Review.user_id == user_id,
        )
    )

    review = result.scalar_one_or_none()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )


    # 2. Delete review


    await db.delete(review)

    await db.commit()

    return {
        "message": "Review deleted successfully"
    }