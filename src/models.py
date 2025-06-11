
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import String, Boolean, Integer,ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


db = SQLAlchemy()

class User(db.Model):
    __tablename__= 'user' # se le pone el mismo nombre de la clase en minuscula
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    favorite_character: Mapped[list['FavoriteCharacteres']]= relationship(back_populates ='user' )
    favorite_planet: Mapped[list['FavoritePlanets']]= relationship(back_populates ='user' )
    def __str__(self):
        return f'Usuario {self.email}' # para devolver en la tablas el nombre del usuario en si y no la variable

    def serialize(self):#aqui pongo todo lo q quiero devolver en forma de diccionario de esta tabla 
        return {
            'id': self.id,
            'email': self.email,
            'is_active': self.is_active
            # do not serialize the password, its a security breach
        }

class Characters(db.Model):
    __tablename__ = 'characters'
    id: Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str] = mapped_column(String(50), nullable=False, unique= True)
    heigth: Mapped[int] = mapped_column(Integer)
    weigth: Mapped[int] = mapped_column(Integer)

    favorite_by: Mapped[list['FavoriteCharacteres']]= relationship(
        back_populates= 'characters')  
    def __str__(self):
        return f'Personaje {self.name} '
    
    def serialize(self):#aqui pongo todo lo q quiero devolver en forma de diccionario de esta tabla 
        return {
            "id": self.id,
            "name": self.name,
            "heigth": self.heigth,
            "weigth": self.weigth
            }


class FavoriteCharacteres(db.Model):
    __tablename__= 'favorite_characters'
    id: Mapped[int] = mapped_column(Integer, primary_key= True)
    user_id: Mapped[int]= mapped_column(ForeignKey('user.id'))
    character_id: Mapped[int] = mapped_column(ForeignKey('characters.id'))

    user: Mapped[User] = relationship(back_populates = 'favorite_character')
    characters: Mapped[Characters] = relationship(back_populates = 'favorite_by')
    def __str__(self):
        return f'El  {self.user} le gusta el  {self.characters}.' 
       
    def serialize(self):#aqui pongo todo lo q quiero devolver en forma de diccionario de esta tabla .
         #NO SE PONEN RELATIOSHIP
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id
        }

class Planets(db.Model):
    __tablename__= 'planets'
    id: Mapped[int]= mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    population: Mapped[int]= mapped_column(Integer)
    diameter: Mapped[int] = mapped_column(Integer)

    favorite_by: Mapped[list['FavoritePlanets']]= relationship(
        back_populates= 'planets', cascade='all, delete-orphan') #esto va en la parte de uno-a-muchos 
    def __str__(self):
        return f'Planeta {self.name} '
    
    def serialize(self):#aqui pongo todo lo q quiero devolver en forma de diccionario de esta tabla 
        return {
            "id": self.id,
            "name": self.name,
            "population": self.population,
            "diameter": self.diameter
        }

class FavoritePlanets(db.Model):
    __tablename__='favorite_planets'
    id: Mapped[int] = mapped_column(Integer, primary_key= True)
    user_id: Mapped[int]= mapped_column(ForeignKey('user.id')) #tabla user, campo id
    planet_id: Mapped[int] = mapped_column(ForeignKey('planets.id')) #tabla planets, campo id
       
    user : Mapped[User] = relationship(back_populates= 'favorite_planet')  
    planets:  Mapped['Planets']= relationship(back_populates= 'favorite_by')
    def __str__(self):
        return f'El  {self.user} le gusta el  {self.planets}.'
    def serialize(self):
        return {
            "user_id": self.user_id,
            "planet_id": self.planet_id
        }