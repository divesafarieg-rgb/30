from sqlalchemy import Column, Integer, String, Text
from database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    ingredients = Column(Text, nullable=False)
    cooking_time = Column(Integer, nullable=False)
    views = Column(Integer, default=0)

    def __repr__(self):
        return f"<Recipe(title='{self.title}', views={self.views})>"