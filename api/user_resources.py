from data import db_session
from data.users import User
from data.friend import Friends
from flask import jsonify, request
from flask_restful import reqparse, abort, Api, Resource


class UserResource(Resource):
    def get(self, user_id):
        # Получение информации о пользователе по его id
        abort_if_users_not_found(user_id)
        session = db_session.create_session()
        users = session.query(User).get(user_id)
        return jsonify(users.to_dict(only=('surname', 
                                           'name',
                                           'friends')) 
                       )
    
    
class UsersListResource(Resource):
    def get(self):
        # Получение всех пользователей
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users':
                        [item.to_dict(only=('id',
                                            'surname', 
                                            'name', 
                                            'friends')) 
                         for item in users]
                        }
                       )
    
    
class FriendsUserResource(Resource):
    def get(self, user_id):
        # Получение друзей определенного пользователя
        abort_if_users_not_found(user_id)
        session = db_session.create_session()
        list_friends = []
        for i in session.query(Friends).filter(Friends.friend_id1 == user_id):
            list_friends.append({'id': i.friend_id2, 'name': i.friend2.name,
                                 'surname': i.friend2.surname, 
                                 'friends': i.friend2.friends})
        for i in session.query(Friends).filter(Friends.friend_id2 == user_id):
            list_friends.append({'id': i.friend_id1, 'name': i.friend1.name,
                                 'surname': i.friend1.surname, 
                                 'friends': i.friend1.friends})                                    
        return jsonify({'friends': list_friends})


def abort_if_users_not_found(users_id):
    # Возвращает ошибку 404 если пользователь не найден
    session = db_session.create_session()
    user = session.query(User).get(users_id)
    if not user:
        abort(404, message=f"User {users_id} not found")    