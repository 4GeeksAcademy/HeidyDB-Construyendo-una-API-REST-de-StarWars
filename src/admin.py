import os
from flask_admin import Admin
from models import db, User, Characters,  FavoriteCharacteres, Planets,  FavoritePlanets
from flask_admin.contrib.sqla import ModelView

class UserModelView(ModelView):
    column_auto_selected_related =True
    column_list= ['id', 'email', 'password', 'is_active', 'favorite_character', 'favorite_planet']

class CharactersModelView(ModelView):
    column_auto_selected_related=True
    column_list= ['id', 'name', 'heigth', 'weigth', 'favorite_by']

class FavoriteCharacteresModelView(ModelView):
    column_auto_selected_related=True
    column_list= ['id', 'user_id', 'user', 'character_id', 'characters']

class PlanetsModelView(ModelView):
    column_auto_selected_related=True
    column_list= ['id', 'name', 'population', 'diameter', 'favorite_by']   

class FavoritePlanetsModelView(ModelView):
    column_auto_selected_related=True
    column_list= ['id', 'user_id', 'user', 'planet_id', 'planets']  

def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')

    
    # Add your models here, for example this is how we add a the User model to the admin
    admin.add_view(UserModelView(User, db.session))
    admin.add_view(CharactersModelView(Characters, db.session))
    admin.add_view(FavoriteCharacteresModelView(FavoriteCharacteres, db.session))
    admin.add_view(PlanetsModelView(Planets, db.session))
    admin.add_view(FavoritePlanetsModelView(FavoritePlanets, db.session))

    # You can duplicate that line to add mew models
    # admin.add_view(ModelView(YourModelName, db.session))