from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey, Table, Column
from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


user_planets = Table(
    "user_planets",
    db.metadata,
    Column("user_id", ForeignKey("user.id")),
    Column("planet_id", ForeignKey("planet.id")),
)


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    userName: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    firstName: Mapped[str] = mapped_column(String(120), nullable=False)
    lastName: Mapped[str] = mapped_column(String(120), nullable=False)

    favPlanets: Mapped[List["Planet"]] = relationship(
        secondary=user_planets, back_populates="favoriteBy")
    favChars: Mapped[List["FavoritesCharacters"]
                     ] = relationship(back_populates="user")

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "userName": self.userName,
            "favPlanets": [planet.serialize() for planet in self.favPlanets],
            "favChars": [char.serialize() for char in self.favChars]
            # do not serialize the password, its a security breach
        }


class Planet(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    size: Mapped[int] = mapped_column(nullable=False)
    solarSystem: Mapped[str] = mapped_column(
        String(120), nullable=False)
    fauna: Mapped[str] = mapped_column(String(120), nullable=False)
    flora: Mapped[str] = mapped_column(String(120), nullable=False)

    favoriteBy: Mapped[List["User"]] = relationship(
        secondary=user_planets, back_populates="favPlanets")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "size": self.size,
            "solarSystem": self.solarSystem,
            "fauna": self.fauna,
            "flore": self.flora
        }


class Charaters(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    race: Mapped[str] = mapped_column(String(120), nullable=False)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    hair_color: Mapped[str] = mapped_column(String(120), nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)

    favoritesBy: Mapped[List["FavoritesCharacters"]
                        ] = relationship(back_populates="char")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "race": self.race,
            "city": self.city,
            "hairColor": self.hair_color,
            "age": self.age,
            "favoritesBy": [by.serialize() for by in self.favoritesBy]
            
        }


class FavoritesCharacters(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    user: Mapped["User"] = relationship(back_populates="favChars")

    char_id: Mapped[int] = mapped_column(ForeignKey("charaters.id"))

    char: Mapped["Charaters"] = relationship(back_populates="favoritesBy")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "char_id": self.char_id
        }
