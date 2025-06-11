"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Characters,  FavoriteCharacteres, Planets,  FavoritePlanets 
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


#obtener todos los usuarios 
@app.route('/users', methods=['GET'])
def get_users():
    users= User.query.all()
    print (users)
    user_serialized = []
    for user in users:
        user_serialized.append(user.serialize())
    return jsonify({'msg': 'ok', 'results' : user_serialized}), 200


#obtener un usuario por su id
@app.route('/users/<int:id>', methods=['GET'])
def get_user_by_id(id):
    user= User.query.get(id)# query.get solo funciona para devolver primary key. para devolver otro campo usar query.filter_by
    print (user)
    if user is None:
        return jsonify ({'msg': 'Usuario no encontrado'}), 404
    return jsonify({'msg': 'ok', 'result': user.serialize()}), 200 # convierte de tipo Class a diccionario con el metodo serialize


#obtener todos los favoritos de un usuario *******************************
@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    user=User.query.get(user_id)
    if user is None :
        return jsonify({'msg': f'el usuario con {user_id} no existe'})
    favorites_serialized_character=[]
    favorites_serialized_planet=[]
    for favorite in user.favorite_character:
        print (favorite.characters)
        favorites_serialized_character.append(favorite.characters.serialize())  
    for favorite in user.favorite_planet:
        print (favorite.planets)
        favorites_serialized_planet.append(favorite.planets.serialize()) 
    return jsonify({'msg': 'ok', 
                    f'para el usurio {user_id} los favoritos son' 
                    'personajes': favorites_serialized_character, 
                    'planetas' : favorites_serialized_planet }), 200
 

# endpoint del POST de un usuario
@app.route('/users', methods=['POST'])
def crear_usuario():
    body= request.get_json(silent=True)
    if body is None:
        return jsonify ({'msg': 'Debes enviar informacion'}), 404
    if 'email' not in body:
        return jsonify ({'msg': 'El campo email es obligatorio'}), 404
    if 'password' not in body: 
        return jsonify ({'msg': 'Debes introducir una contraseña'}), 404
    
    nuevo_usuario = User() # nuevo_usuario es una instancia de la clase 
    nuevo_usuario.email = body['email']
    nuevo_usuario.password= body['password']
    nuevo_usuario.is_active = True
    db.session.add(nuevo_usuario)
    db.session.commit()
    return jsonify({'msg': 'ok', 'result': nuevo_usuario.serialize()}), 200


# ---------------------PERSONAJES-----------------------------------------
#obtener todos los personajes 
@app.route('/characters', methods=['GET'])
def get_characters():
    personaje= Characters.query.all() # obtener todos los personaje de la clase Characters
    print (personaje)
    personaje_serialized = [] # hago un diccionario vacio
    for pers in personaje:
        personaje_serialized.append(pers.serialize()) # agrego cada personaje al diccionario que cree y lo serializo
    return jsonify({'msg': 'ok', 'estos son los personajes' : personaje_serialized}), 200
 

# #obtener  un personaje por su id
@app.route('/characters/<int:id>', methods =['GET'])
def get_character_by_id(id):
    personaje_id = Characters.query.get(id)# solo se usa query.get con la primary key, para obtener otro campo q no sea el PK se usa filter_by 
    print (personaje_id)
    if personaje_id is None:
        return({'msg': 'el id no corresponde a ningun personaje'}), 400
    return ({'msg': 'ok', 'el personaje es': personaje_id.serialize()}), 200
    
  
#POST de personajes 
@app.route('/characters', methods= ['POST'])
def post_personaje():
    body= request.get_json(silent=True)
    if body is None: 
        return ({'msg': 'debe introducir un personaje'}), 400
    if 'name' not in body:
        return ({'msg': 'debe introducir un nombre de un personaje en la variable "name"'}), 400
    if 'heigth' not in body :
        return ({'msg': 'debe introducir la altura del personaje en la variable "heigth"'}), 400
    if 'weigth' not in body:
        return ({'msg': 'debe introducir el peso del personaje en la variable "weigth"'}), 400
    nuevo_personaje= Characters() # ahora le asigno a cada campo d la clase Characters lo que recivo en body
    nuevo_personaje.name= body['name']
    nuevo_personaje.heigth= body['heigth']
    nuevo_personaje.weigth=body['weigth']
    db.session.add(nuevo_personaje)
    db.session.commit()
    return ({'msg':'ok', 'results': nuevo_personaje.serialize()}) # convierto de clase a diccionario

#post de un personaje favorito por un person_id a un usuario user_id
@app.route ('/favorite/<int:u_id>/characters/<int:ch_id>', methods = ['POST'])
def add_favorite_personaje_a_usuario(ch_id, u_id):
    usuario = User.query.get(u_id)
    personaje= Characters.query.get(ch_id)
    if usuario is None :
        return jsonify({'msg': f'este usuario con id {u_id} no existe'}), 400
    if personaje is None :
        return jsonify({'msg': f'este personaje con id {ch_id} no existe'}), 400
    favorito= FavoriteCharacteres.query.filter_by(character_id = ch_id, user_id = u_id ).all()
    print(favorito)
    if len(favorito) !=0: # si ya hay elemento en el dicc es que ya ese personajen es favorito de ese usuario
         return jsonify({'msg': f'este personaje con id {ch_id} ya es un favorito del usuario {u_id}'}), 400
    nuevo_favorito= FavoriteCharacteres()
    nuevo_favorito.user_id= u_id
    nuevo_favorito.character_id= ch_id
    db.session.add(nuevo_favorito)
    db.session.commit()
    return jsonify({'msg':'ok', 'results': nuevo_favorito.serialize()}), 200

#DELETE /favorite/characters/<int:character_id> Elimina un personaje FAVORITO con el id = character_id
@app.route('/favorite/characters/<int:character_id>', methods = ['DELETE'])
def borrar_personaje_favorito(character_id):
    personaje_f = FavoriteCharacteres.query.get(character_id)
    if personaje_f is None :
        return jsonify({'msg': f'el id {character_id} no coincide con ningun personaje favorito'}), 400
    print(personaje_f)
    db.session.delete(personaje_f)
    db.session.commit()
    return jsonify({'msg': f'el personaje favorito con ID {character_id} ha sido borrado de la lista de favoritos'}), 200

#DELETE de un personaje en la tabla Characters
@app.route('/characters/<int:character_id>', methods= ['DELETE'])
def borrar_personaje(personaje_id):
    pers= Characters.query.get(personaje_id)
    if pers is None:
        return jsonify({'msg': f'el planeta con id {personaje_id} no existe '}), 400
    db.session.delete(personaje_id)
    db.session.commit()
    return ({'msg': f'el personaje con id {personaje_id} ha sido borrado de la tabla personajes'}), 200


#PUT DE UN personaje. actualiza sus campos
@app.route('/characters-put/<int:character_id>', methods= ['PUT'])
def actualizar_personaje(character_id):
    personaje=Characters.query.get(character_id)
    body= request.get_json(silent=True)
    if personaje is None:
        return jsonify({'msg': 'no existe ningun personaje con ese ID '}), 400
    if body is None :
        return jsonify({'msg': 'debe introducir los campos a modificar'}), 400
    if 'name' not in body:
        return ({'msg': 'debe introducir un nombre de un personaje en la variable name'}), 400
    if 'heigth' not in body :
        return ({'msg': 'debe introducir la altura del personaje en la variable heigth'}), 400
    if 'weigth' not in body:
        return ({'msg': 'debe introducir el peso del personaje en la variable weigth'}), 400
       
    #cada campo de la instancia Personajes con el id requerido se actualiza con lo que pasamor en el body
   
    personaje.name=body['name']
    personaje.heigth=body['heigth']
    personaje.weigth=body['weigth']
    db.session.commit() #no hago .add porque est actualizando , no agregando , ya existe esa instancia de planeta
    return jsonify({'msg':f'se ha actualizado el id {character_id} en la tabla planetas', 'results': personaje.serialize() }), 200


#---------------------------------------PLANETAS-----------------------------------------------------
#GET todos los planetas 
@app.route('/planets', methods=['GET'])
def get_planetas():
    planetas= Planets.query.all() # obtener todos los planetas de la clase Planets
    print (planetas)
    planeta_serialized = []
    for planet in planetas:
        planeta_serialized.append(planet.serialize()) #serializo todo el arreglo
    return jsonify({'msg': 'ok', 'results' : planeta_serialized}), 200

#GET un planeta por su id 
@app.route('/planets/<int:id>', methods= ['GET'])
def get_planet_by_id(id):
    planeta= Planets.query.get(id)
    print(planeta)
    if planeta is None:
        return ({'msg': 'el id no corresponde con ningun planeta'}), 400
    return ({'msg': 'ok', 'result': planeta.serialize()}), 200

#hacer el POST de un planeta
@app.route('/planets', methods=['POST'])
def post_planeta():
    body= request.get_json(silent=True)
    if body is None :
        return ({'msg': 'debe introducir un planeta'})
    if 'name' not in body :
        return ({'msg': 'debe introducir un nombre del planeta'})
    if 'population' not in body:
        return ({'msg': 'debe introducir la poblacion del planeta'})
    if 'diameter' not in body :
        return ({'msg': 'debe introducir el diametro del planeta'})
    
    nuevo_planeta= Planets()
    nuevo_planeta.name= body['name']
    nuevo_planeta.population= body['population']
    nuevo_planeta.diameter= body['diameter']
    db.session.add(nuevo_planeta)
    db.session.commit()
    return ({'msg': 'ok', 'result': nuevo_planeta.serialize()})

#POST de un planeta FAVORITO a un usuario segun planet_id /favorite/planet/<int:planet_id>
@app.route('/favorite/<int:user_id>/planet/<int:planet_id>', methods = ['POST'])
def add_favorite_planet_a_usuario(planet_id, user_id):
    usuario= User.query.get(user_id)
    planeta= Planets.query.get(planet_id)
    if usuario is None :    
       return jsonify({'msg': f' no exite un usuario con id {user_id}'}), 400
    if planeta is None :
        return jsonify({'msg': 'no existe este planets'}), 400
    favorite = FavoritePlanets.query.filter_by(user_id = user_id, planet_id = planet_id ).all()
    #aqui filtro q el user_id q pase como parametro sea igual al valor de la columna user_id en FavoritePlanets
    if len(favorite) != 0:
        return jsonify({'msg': 'este favorito ya lo agregaste'}), 400
    print (favorite)
    nuevo_favorito= FavoritePlanets()
    nuevo_favorito.user_id = user_id
    nuevo_favorito.planet_id = planet_id 
    db.session.add(nuevo_favorito)
    db.session.commit()
    return jsonify({'msg':'ok', 'results': nuevo_favorito.serialize()}), 200

#DELETE  Elimina un planet FAVORITO con el id = planet_id. /favorite/planet/<int:planet_id>
@app.route('/favorite/planet/<int:planet_id>', methods = ['DELETE'])
def eliminar_planeta_por_id(planet_id):
    planeta= FavoritePlanets.query.get(planet_id)
    if planeta is None :
        return jsonify({'msg': f'no existe un planeta favorito con id {planet_id}'}), 400
    db.session.delete(planeta)
    db.session.commit()
    return jsonify({'msg':'ok', 'results': f'el planeta con id {planet_id} ha sido borrado dela lista de favoritos'}), 200


#DELETE de un planeta
@app.route('/planets/<int:planet_id>', methods= ['DELETE'])
def eliminar_personaje_por_id(planet_id):
    planeta= Planets.query.get(planet_id)
    if planeta is None:
        return jsonify({'msg': f'el planeta con id {planet_id} no existe '}), 400
    db.session.delete(planeta)
    db.session.commit()
    return ({'msg': f'el planeta con id {planet_id} ha sido borrado de la tabla Planetas'}), 200

#PUT DE UN PLANETA
@app.route('/planets-put/<int:planet_id>', methods= ['PUT'])
def actualizar_planeta(planet_id):
    planeta=Planets.query.get(planet_id)
    body= request.get_json(silent=True)
    if planeta is None:
        return jsonify({'msg': 'no existe ningun planeta con ese ID '}), 400
    if body is None :
        return jsonify({'msg': 'debe introducir los campos a modificar'}), 400
 
    #cada campo de la instancia Planetas con el id requerido se actualiza con lo que pasamor en el body
    
    planeta.name=body['name']
    planeta.population=body['population']
    planeta.diameter=body['diameter']
    db.session.commit() #no hago .add porque est actualizando , no agregando , ya existe esa instancia de planeta
    return jsonify({'msg':f'se ha actualizado el id {planet_id} en la tabla planetas', 'results': planeta.serialize() }), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
