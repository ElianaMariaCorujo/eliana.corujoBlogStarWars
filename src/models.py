import enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

db = SQLAlchemy()

# Definimos el Enum para el tipo de favorito
class FavoriteNature(enum.Enum):
    planet = "planet"
    character = "character"


class User(db.Model):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(180), nullable=False)
    firstname: Mapped[str] = mapped_column(String(50), nullable=True)
    lastname: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relación: Un usuario tiene muchos favoritos
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="user")

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "firstname": self.firstname,
            "lastname": self.lastname
        }

class Planet(db.Model):
    __tablename__ = 'planet'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    population: Mapped[int] = mapped_column(Integer, nullable=True)
    url: Mapped[str] = mapped_column(String(150), nullable=True)

    # Relación: Un planeta puede estar en muchas listas de favoritos
    favorited_by: Mapped[list["Favorite"]] = relationship(back_populates="planet")

    def serialize(self):
        return { "id": self.id, "name": self.name, "population": self.population }

class Character(db.Model):
    __tablename__ = 'character'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=True)
    url: Mapped[str] = mapped_column(String(180), nullable=True)
    
    # Relación: Un personaje puede estar en muchas listas de favoritos
    favorited_by: Mapped[list["Favorite"]] = relationship(back_populates="character")

    def serialize(self):
        return { "id": self.id, "name": self.name, "description": self.description }

class Favorite(db.Model):
    __tablename__ = 'favorite'
    id: Mapped[int] = mapped_column(primary_key=True)

    # Qué tipo de favorito es
    nature: Mapped[FavoriteNature] = mapped_column(Enum(FavoriteNature), nullable=False)

    # Claves Foráneas (FK) - Nulables
    planet_id: Mapped[int] = mapped_column(ForeignKey("planet.id"), nullable=True)
    character_id: Mapped[int] = mapped_column(ForeignKey("character.id"), nullable=True)

    # A quién le pertenece
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    # Relaciones de vuelta (back_populates)
    user: Mapped["User"] = relationship(back_populates="favorites")
    planet: Mapped["Planet"] = relationship(back_populates="favorited_by")
    character: Mapped["Character"] = relationship(back_populates="favorited_by")

    def serialize(self):
        # Serialización condicional para mostrar el nombre
        item_name = ""
        if self.nature == FavoriteNature.planet and self.planet:
            item_name = self.planet.name
        elif self.nature == FavoriteNature.character and self.character:
            item_name = self.character.name

        return {
            "id": self.id,
            "nature": self.nature.name,
            "user_id": self.user_id,
            "item_id": self.planet_id if self.nature == FavoriteNature.planet else self.character_id,
            "item_name": item_name
        }