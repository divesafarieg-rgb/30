from sqlalchemy.orm import Session
from models import Recipe
from schemas import RecipeCreate, RecipeUpdate

def get_recipe(db: Session, recipe_id: int):
    return db.query(Recipe).filter(Recipe.id == recipe_id).first()

def get_recipes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Recipe).order_by(
        Recipe.views.desc(),
        Recipe.cooking_time.asc()
    ).offset(skip).limit(limit).all()

def create_recipe(db: Session, recipe: RecipeCreate):
    db_recipe = Recipe(
        title=recipe.title,
        description=recipe.description,
        ingredients=recipe.ingredients,
        cooking_time=recipe.cooking_time,
        views=0
    )
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe

def increment_recipe_views(db: Session, recipe_id: int):
    recipe = get_recipe(db, recipe_id)
    if recipe:
        recipe.views += 1
        db.commit()
        db.refresh(recipe)
    return recipe

def update_recipe(db: Session, recipe_id: int, recipe_update: RecipeUpdate):
    recipe = get_recipe(db, recipe_id)
    if recipe:
        for key, value in recipe_update.dict().items():
            setattr(recipe, key, value)
        db.commit()
        db.refresh(recipe)
    return recipe

def delete_recipe(db: Session, recipe_id: int):
    recipe = get_recipe(db, recipe_id)
    if recipe:
        db.delete(recipe)
        db.commit()
        return True
    return False