from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
import re


class RecipeBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Название блюда")
    description: str = Field(..., min_length=10, description="Описание приготовления")
    ingredients: str = Field(..., min_length=5, description="Список ингредиентов")
    cooking_time: int = Field(..., gt=0, le=1440, description="Время приготовления в минутах")

    @field_validator('cooking_time')
    def validate_cooking_time(cls, v):
        if v <= 0:
            raise ValueError('Время приготовления должно быть больше 0')
        if v > 1440:
            raise ValueError('Время приготовления не может превышать 24 часа')
        return v

    @field_validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Название не может быть пустым')
        return v.strip()


class RecipeCreate(RecipeBase):
    pass


class RecipeUpdate(RecipeBase):
    pass


class RecipeInDB(RecipeBase):
    id: int
    views: int

    class Config:
        from_attributes = True


class RecipeListResponse(BaseModel):
    id: int
    title: str
    views: int
    cooking_time: int

    class Config:
        from_attributes = True


class RecipeDetailResponse(RecipeInDB):
    ingredients_list: List[str] = Field(..., description="Список ингредиентов в виде массива")

    @classmethod
    def from_recipe(cls, recipe: RecipeInDB):
        ingredients = re.split(r'[,\n]', recipe.ingredients)
        ingredients = [i.strip() for i in ingredients if i.strip()]

        return cls(
            id=recipe.id,
            title=recipe.title,
            description=recipe.description,
            ingredients=recipe.ingredients,
            ingredients_list=ingredients,
            cooking_time=recipe.cooking_time,
            views=recipe.views
        )