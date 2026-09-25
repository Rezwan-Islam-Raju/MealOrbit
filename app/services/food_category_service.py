from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status


from app.models.food_category_model import FoodCategory
from app.schemas.food_category_schema import (
    FoodCategoryCreateRequest,
    FoodCategoryUpdateRequest,
)


async def food_create_category_service(
    request: FoodCategoryCreateRequest,
    db: AsyncSession
):
    name = request.name.strip()

    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name cannot be empty"
        )

    result = await db.execute(
        select(FoodCategory).where(FoodCategory.name.ilike(name),
            FoodCategory.is_active.is_(True)
        )
    )

    existing_category = result.scalar_one_or_none()

    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Food category already exists"
        )

    category = FoodCategory(
        name=name,
        description=request.description,
        img_url=request.img_url,
        is_active=True,
    )

    db.add(category)

    await db.commit()
    await db.refresh(category)

    return category

async def food_get_all_categories_service(
    db: AsyncSession
):
    result = await db.execute(select(FoodCategory).where( FoodCategory.is_active == True)
        .order_by(
            FoodCategory.name.asc()
        )
    )

    categories = result.scalars().all()

    return categories


async def food_search_category_service(
    db: AsyncSession,
    query: str
):
    query = query.strip()

    if not query:
        return []

    search_query = f"%{query}%"

    result = await db.execute(
        select(FoodCategory).where(
            FoodCategory.is_active == True,
            or_(FoodCategory.name.ilike(search_query),
                FoodCategory.description.ilike(search_query),
            )
        ) .order_by(
            FoodCategory.id.desc()
        )
    )

    categories = result.scalars().all()

    return categories


async def food_get_category_by_id_service(
    category_id: int,
    db: AsyncSession
):
    result = await db.execute(
        select(FoodCategory).where(FoodCategory.id == category_id,
            FoodCategory.is_active == True
        )
    )

    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
            detail="Food category not found"
        )

    return category


async def food_update_category_service(
    request: FoodCategoryUpdateRequest,
    category_id: int,
    user_id: int,
    db: AsyncSession
):
    # Find category
    result = await db.execute(
        select(FoodCategory).where(
            FoodCategory.id == category_id,
            FoodCategory.is_active.is_(True)
        )
    )

    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food category not found"
        )

    # Update name
    if request.name is not None:

        new_name = request.name.strip()

        if not new_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name cannot be empty"
            )

        # Check duplicate category name
        duplicate_result = await db.execute(
            select(FoodCategory).where(
                FoodCategory.name==new_name,
                FoodCategory.id != category_id,
                FoodCategory.is_active.is_(True)
            )
        )

        duplicate_category = duplicate_result.scalar_one_or_none()

        if duplicate_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Food category name already exists"
            )

        category.name = new_name

    # Update description
    if request.description is not None:
        category.description = request.description.strip()

    # Update image URL
    if request.img_url is not None:
        category.img_url = request.img_url.strip()

    # Update active status
    if request.is_active is not None:
        category.is_active = request.is_active

    await db.commit()
    await db.refresh(category)

    return category

async def food_delete_category_service(

    user_id: int,
    db: AsyncSession
):
    result = await db.execute(select(FoodCategory).where(
        FoodCategory.user_id == user_id,
            FoodCategory.is_active.is_(True)
        )
    )

    category = result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food category not found"
        )

    category.is_active = False

    await db.commit()

    return {
        "message": "Food category deleted successfully",
        "success": True
    }