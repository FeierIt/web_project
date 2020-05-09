from data import db_session
from data.photo import Photo
from data.users import User
from data.comment import Comment
from data.avatar import Avatar
from flask import jsonify, request
from flask_restful import reqparse, abort, Api, Resource
import os 
from flask import url_for


class PhotoUserResource(Resource):
    def get(self, user_id):
        # Получение информации о фотографиях пользователя
        abort_if_users_not_found(user_id)
        session = db_session.create_session()
        photos = session.query(Photo).filter(Photo.user_id == user_id)
        list_photos = []
        for i in photos:
            comments = len(list(session.query(Comment).filter(Comment.photo_id == i.id)))
            list_photos.append({'photo_id': i.id, 'likes': i.likes,
                                'comments': comments})
        return jsonify({'photos': list_photos}) 
    
    
class PhotoResource(Resource):
    def get(self, photo_id):
        # Получение информации фотографии по её id
        abort_if_photo_not_found(photo_id)
        session = db_session.create_session()
        photo = session.query(Photo).get(photo_id)
        comments = len(list(session.query(Comment).filter(Comment.photo_id == photo_id)))                 
        return jsonify({'likes': photo.likes, 'comments': comments,
                        'user': {'id': photo.user_id, 'surname': photo.user.surname,
                                 'name': photo.user.name}})
    
    
class PhotoDeleteResource(Resource):
    def delete(self, photo_id, email, password):
        # Удаление фотографии по её id
        abort_if_photo_not_found(photo_id)    
        session = db_session.create_session()      
        user = session.query(User).filter(User.email == email).first()
        if user and user.check_password(password):
            photo = session.query(Photo).get(photo_id)
            if photo.user_id == user.id:
                if user.avatar is not None and user.avatar.photo_id == photo_id:
                    avatar = user.avatar
                    user = session.query(User).get(user.id) 
                    user.avatar_id = None
                    session.commit()
                    for i in session.query(Avatar).filter(Avatar.photo_id == photo_id):
                        session.delete(session.query(Avatar).get(i.id))
                os.remove(os.getcwd() + url_for("static", filename=photo.img_name))                
                session.delete(photo)
                session.commit()
                return jsonify({'success': 'OK'})    
            abort(404, message='You can not delete this photo')
        abort(404, message='Incorrect email or password')    


def abort_if_users_not_found(users_id):
    # Возвращает ошибку 404 если пользователь не найден
    session = db_session.create_session()
    user = session.query(User).get(users_id)
    if not user:
        abort(404, message=f"User {users_id} not found")    
        

def abort_if_photo_not_found(photo_id):
    # Возвращает ошибку 404 если фото не найдено
    session = db_session.create_session()
    photo = session.query(Photo).get(photo_id)
    if not photo:
        abort(404, message=f"Photo {photo_id} not found")    