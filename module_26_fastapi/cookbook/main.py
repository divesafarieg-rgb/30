from fastapi import FastAPI, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from database import SessionLocal, engine
from models import Base
from schemas import (
    RecipeCreate,
    RecipeUpdate,
    RecipeListResponse,
    RecipeDetailResponse,
    RecipeInDB
)
from crud import (
    get_recipe,
    get_recipes,
    create_recipe,
    increment_recipe_views,
    update_recipe,
    delete_recipe
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Cookbook API",
    description="""
    API для кулинарной книги.

    ## Возможности:
    * Получение списка всех рецептов (сортировка по популярности)
    * Получение детальной информации о рецепте
    * Создание нового рецепта
    * Обновление существующего рецепта
    * Удаление рецепта

    ## Сортировка рецептов:
    Рецепты сортируются по количеству просмотров (убывание),
    при равном количестве просмотров - по времени приготовления (возрастание).
    """,
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "support@cookbook.com",
    },
    license_info={
        "name": "MIT",
    },
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get(
    "/",
    tags=["Root"],
    summary="Корневой эндпоинт",
    description="Возвращает приветственное сообщение и ссылки на документацию"
)
async def root():
    return {
        "message": "Добро пожаловать в Cookbook API!",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "GET /recipes": "Получить список всех рецептов",
            "GET /recipes/{id}": "Получить детальную информацию о рецепте",
            "POST /recipes": "Создать новый рецепт",
            "PUT /recipes/{id}": "Обновить существующий рецепт",
            "DELETE /recipes/{id}": "Удалить рецепт"
        }
    }


@app.get(
    "/recipes",
    response_model=List[RecipeListResponse],
    status_code=status.HTTP_200_OK,
    tags=["Recipes"],
    summary="Получить список всех рецептов",
    description="""
    Возвращает список всех рецептов для отображения на первом экране.

    Результаты сортируются:
    1. По убыванию количества просмотров
    2. По возрастанию времени приготовления (если просмотров одинаково)

    Поля в ответе:
    * **id** - уникальный идентификатор рецепта
    * **title** - название блюда
    * **views** - количество просмотров
    * **cooking_time** - время приготовления в минутах
    """,
    response_description="Список рецептов для таблицы"
)
async def read_recipes(
        skip: int = Query(0, ge=0, description="Сколько рецептов пропустить"),
        limit: int = Query(100, ge=1, le=1000, description="Сколько рецептов вернуть"),
        db: Session = Depends(get_db)
):
    recipes = get_recipes(db, skip=skip, limit=limit)
    return recipes


@app.get(
    "/recipes/{recipe_id}",
    response_model=RecipeDetailResponse,
    status_code=status.HTTP_200_OK,
    tags=["Recipes"],
    summary="Получить детальную информацию о рецепте",
    description="""
    Возвращает подробную информацию о конкретном рецепте для второго экрана.

    При каждом запросе счетчик просмотров рецепта увеличивается на 1.

    Дополнительно к основным полям возвращается:
    * **ingredients_list** - список ингредиентов, разбитый по запятым и переносам строк
    """,
    responses={
        200: {
            "description": "Успешный ответ с деталями рецепта",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "Борщ",
                        "description": "Традиционный украинский суп...",
                        "ingredients": "свекла, капуста, картофель",
                        "ingredients_list": ["свекла", "капуста", "картофель"],
                        "cooking_time": 120,
                        "views": 42
                    }
                }
            }
        },
        404: {
            "description": "Рецепт не найден",
            "content": {
                "application/json": {
                    "example": {"detail": "Рецепт с id 999 не найден"}
                }
            }
        }
    }
)
async def read_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = increment_recipe_views(db, recipe_id)
    if recipe is None:
        raise HTTPException(
            status_code=404,
            detail=f"Рецепт с id {recipe_id} не найден"
        )
    return RecipeDetailResponse.from_recipe(RecipeInDB.model_validate(recipe))


@app.post(
    "/recipes",
    response_model=RecipeInDB,
    status_code=status.HTTP_201_CREATED,
    tags=["Recipes"],
    summary="Создать новый рецепт",
    description="""
    Создает новый рецепт в базе данных.

    Новый рецепт создается с количеством просмотров = 0.

    Поля для создания:
    * **title** - название блюда (обязательно)
    * **description** - описание приготовления (обязательно, минимум 10 символов)
    * **ingredients** - список ингредиентов (обязательно, минимум 5 символов)
    * **cooking_time** - время приготовления в минутах (обязательно, от 1 до 1440)
    """,
    responses={
        201: {
            "description": "Рецепт успешно создан",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "title": "Борщ",
                        "description": "Традиционный украинский суп...",
                        "ingredients": "свекла, капуста, картофель",
                        "cooking_time": 120,
                        "views": 0
                    }
                }
            }
        },
        422: {
            "description": "Ошибка валидации данных",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "cooking_time"],
                                "msg": "Время приготовления должно быть больше 0",
                                "type": "value_error"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def create_new_recipe(
        recipe: RecipeCreate,
        db: Session = Depends(get_db)
):
    return create_recipe(db=db, recipe=recipe)


@app.put(
    "/recipes/{recipe_id}",
    response_model=RecipeInDB,
    status_code=status.HTTP_200_OK,
    tags=["Recipes"],
    summary="Обновить существующий рецепт",
    description="Обновляет информацию о существующем рецепте"
)
async def update_existing_recipe(
        recipe_id: int,
        recipe: RecipeUpdate,
        db: Session = Depends(get_db)
):
    updated_recipe = update_recipe(db, recipe_id, recipe)
    if updated_recipe is None:
        raise HTTPException(
            status_code=404,
            detail=f"Рецепт с id {recipe_id} не найден"
        )
    return updated_recipe


@app.delete(
    "/recipes/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Recipes"],
    summary="Удалить рецепт",
    description="Удаляет рецепт из базы данных"
)
async def delete_existing_recipe(
        recipe_id: int,
        db: Session = Depends(get_db)
):
    deleted = delete_recipe(db, recipe_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Рецепт с id {recipe_id} не найден"
        )
    return None