from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.dependencies.auth_dependecy import require_user_id
from app.schemas.food_category_schema import (
FoodCategoryResponse,
FoodCategoryCreateRequest,
FoodCategoryUpdateRequest
)
from app.services.food_category_service import (
food_create_category_service,
food_get_all_categories_service,
food_search_category_service,
food_get_category_by_id_service,
food_update_category_service,
food_delete_category_service
)
from config.database import get_db

router = APIRouter()




# ---------CREATE CATEGORY API --------

@router.post(
    "/",
    response_model=FoodCategoryResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_category(
    request: FoodCategoryCreateRequest,
    db: AsyncSession = Depends(get_db)

):
    try:
        category = await food_create_category_service(
            db=db,
            request=request

        )

        return category

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,detail=str(e))

#------ GET ALL CATEGORIES SERVICE API -------

@router.get("/",response_model=list[FoodCategoryResponse])
async def get_categories(db:AsyncSession=Depends(get_db)):

    category = await food_get_all_categories_service(
        db=db
    )
    return category

#------- SEARCH CATEGORY API------
@router.get("/search",response_model=list[FoodCategoryResponse])
async def search_category(query:str,db:AsyncSession=Depends(get_db)):

    search_categories = await food_search_category_service(
        db=db,
        query=query
    )
    return search_categories

#-------- SEARCH CATEGORY BY ID-------
@router.get("/{category_id}",response_model=FoodCategoryResponse)
async def get_categories(category_id:int,db:AsyncSession=Depends(get_db)):

    category = await food_get_category_by_id_service(
        db=db,
        category_id=category_id
    )
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Category not found")

    return category

#---------UPDATE CATEGORY API--------

@router.put("/{category_id}", response_model=FoodCategoryResponse)
async def update_category(
    request: FoodCategoryUpdateRequest,
    category_id: int,
    db: AsyncSession = Depends(get_db),
    user_id:int=Depends(require_user_id)

):
    try:
        result = await food_update_category_service(
            db=db,
            category_id=category_id,
            user_id=user_id,
            request=request
        )

        return result

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

#------ DELETE CATEGORY API-----------

@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(require_user_id)
):
    try:
        result = await food_delete_category_service(
            category_id=category_id,
            user_id=user_id,
            db=db
        )

        return result

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,detail=str(e))