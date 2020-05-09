# -*- coding: utf8 -*-
from flask import Flask, url_for, request, render_template, redirect, abort
from flask import make_response, jsonify, g
from data import db_session
from data.users import *
from data.photo import *
from data.like import *
from data.comment import *
from data.invite import *
from data.friend import *
from data.message import * 
from data.avatar import *
from data.dialog import *
from api import user_resources, photo_resources, comment_resources
from form.__all_form import *
from datetime import datetime
from flask_login import LoginManager, login_user, login_required, logout_user
from flask_login import current_user
from flask_restful import reqparse, abort, Api, Resource
from werkzeug.utils import secure_filename
import os 
from PIL import Image
import random

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['DEBUG'] = True
login_manager = LoginManager()
login_manager.init_app(app) 


def sort_friends(friends, id):
    if len(friends) <= 1:
        return friends
    q = random.choice(friends)
    if q.friend_id1 == id:
        q = f"{q.friend2.name} {q.friend2.surname}"
    else:
        q = f"{q.friend1.name} {q.friend1.surname}"   
    l = []
    m = []
    r = []   
    for i in range(len(friends)):
        if friends[i].friend_id1 == id:
            if f"{friends[i].friend2.name} {friends[i].friend2.surname}"  < q:
                l.append(friends[i]) 
            elif f"{friends[i].friend2.name} {friends[i].friend2.surname}" > q: 
                r.append(friends[i])
            else: 
                m.append(friends[i])
        else:
            if f"{friends[i].friend1.name} {friends[i].friend1.surname}"  < q:
                l.append(friends[i]) 
            elif f"{friends[i].friend1.name} {friends[i].friend1.surname}" > q: 
                r.append(friends[i])
            else: 
                m.append(friends[i])            
    return sort_friends(l, id) + m + sort_friends(r, id)


@app.route('/delete_photo', methods=['POST'])
@login_required
def delete_photo():
    session = db_session.create_session()
    if current_user.avatar is not None and current_user.avatar.photo_id == int(request.form['id']):
        avatar = current_user.avatar
        user = session.query(User).get(current_user.id) 
        user.avatar_id = None
        session.commit()
        for i in session.query(Avatar).filter(Avatar.photo_id == request.form['id']):
            session.delete(session.query(Avatar).get(i.id))
    photo = session.query(Photo).get(request.form['id'])
    os.remove(os.getcwd() + url_for("static", filename=photo.img_name))
    session.delete(photo)
    session.commit()
    return jsonify({'success': 'OK'})
    

@app.route('/delete_comment', methods=['POST'])
@login_required
def delete_comment():
    session = db_session.create_session() 
    session.delete(session.query(Comment).get(request.form['id']))
    session.commit()
    return jsonify({'success': 'OK'})


@app.route('/delete_friend', methods=['POST'])
@login_required
def delete_friend():
    session = db_session.create_session() 
    invite_db = Invite(
        sender_id=request.form['id'],
        receiver_id=current_user.id      
        )         
    a = session.query(Friends).filter(Friends.friend_id1 == request.form['id'],
                                      Friends.friend_id2 == current_user.id).first()
    if a:
        friend_invite = a
    else:
        friend_invite = session.query(Friends).filter(Friends.friend_id1 == current_user.id,
                                                      Friends.friend_id2 == request.form['id']).first() 
    if friend_invite:
        session.delete(session.query(Friends).get(friend_invite.id))
        friend1 = session.query(User).get(current_user.id)
        friend2 = session.query(User).get(request.form['id'])
        friend1.friends -= 1
        friend2.friends -= 1          
        session.add(invite_db)    
        session.commit()
        return jsonify({'id_invite': invite_db.id})
    abort(404)


@app.route('/set_avatar', methods=['POST'])
@login_required
def set_avatar():
    session = db_session.create_session() 
    avatar_db = Avatar(
        photo_id=int(request.form['id_photo'])
    )
    user = session.query(User).get(current_user.id) 
    session.add(avatar_db)
    session.commit()
    user.avatar_id = avatar_db.id
    session.commit()
    return jsonify({'success': 'OK'})    


@app.route('/send_invite', methods=['POST'])
@login_required
def send_invite():
    session = db_session.create_session() 
    invite = session.query(Invite).filter(Invite.sender_id == int(request.form['id']),
                                          Invite.receiver_id == current_user.id).first()  
    if not invite:
        invite_db = Invite(
            sender_id=current_user.id,
            receiver_id=request.form['id']
        )           
        session.add(invite_db)    
        session.commit()    
        return jsonify({'success': 'OK'}) 
    abort(404)
    
    
@app.route('/cancel_invite', methods=['POST'])
@login_required
def cancel_invite():
    session = db_session.create_session() 
    invite = session.query(Invite).filter(Invite.sender_id == current_user.id,
                                          Invite.receiver_id == int(request.form['id'])).first()  
    if invite:
        session.delete(invite)
        session.commit()    
        return jsonify({'success': 'OK'}) 
    abort(404)
    

@app.route('/search_friend', methods=['POST'])
@login_required
def search_friend():
    session = db_session.create_session()
    name = request.form['name'].lower().title()
    surname = request.form['surname'].lower().title()
    print(name, surname)
    list_user = session.query(User).filter(User.name.ilike(f"%{name}%"),
                                           User.surname.ilike(f"%{surname}%"))
    list_info_user = []
    for i in list_user:
        send = session.query(Invite).filter(Invite.sender_id == current_user.id,
                                            Invite.receiver_id == i.id).first()
        accept = session.query(Invite).filter(Invite.sender_id == i.id,
                                              Invite.receiver_id == current_user.id).first()
        a = session.query(Friends).filter(Friends.friend_id1 == i.id,
                                          Friends.friend_id2 == current_user.id).first()
        if a:
            friend_invite = a
        else:
            friend_invite = session.query(Friends).filter(Friends.friend_id1 == current_user.id,
                                                           Friends.friend_id2 == i.id).first()
        if send and not accept and not friend_invite:
            type_invite = 1
        elif not send and not accept and not friend_invite:
            type_invite = 0
        elif not send and accept and not friend_invite:
            type_invite = 2
        else:
            type_invite = 3        
        list_info_user.append({'type': type_invite, 'id': i.id, 
                               'name': i.name,'surname': i.surname, 
                               'avatar': i.avatar.photo.img_name if i.avatar else False})
    return jsonify({'users': list_info_user})


@app.route('/send_message', methods=['GET', 'POST'])
@login_required
def message():
    session = db_session.create_session()
    if request.method == 'POST':
        message_db = Message(
            text=request.form['text'],
            sender_message_id=request.form['sender'],
            receiver_message_id=request.form['receiver']
        )
        session.add(message_db)
        dialog = session.query(Dialog
                               ).filter(
                                   (Dialog.friend_dialog_id1 == request.form['sender']) |
                                   (Dialog.friend_dialog_id2 == request.form['receiver'])).first()
        if not dialog:
            dialog = session.query(Dialog
                                   ).filter(
                                       (Dialog.friend_dialog_id2 == request.form['sender']) |
                                       (Dialog.friend_dialog_id1 == request.form['receiver'])).first()
        print(dialog)
        if dialog:
            dialog.message_id = message_db.id
        else:
            dialog_db = Dialog(
                friend_dialog_id1=request.form['sender'],
                friend_dialog_id2=request.form['receiver'],
                message_id=message_db.id
            )
            session.add(dialog_db)
        session.commit() 
        return jsonify({'success': 'OK'})
    sender = request.args.get('sender')
    receiver = request.args.get('receiver')
    list_message = session.query(Message).filter(
        (Message.sender_message_id == sender) |
        (Message.sender_message_id == receiver)).filter(
            (Message.receiver_message_id == sender) |
            (Message.receiver_message_id == receiver))
    message = []
    for i in list_message:
        message.append([i.text, i.sender_message_id])
    return jsonify({'list_message': message})
    

@app.route('/like', methods=['POST'])
@login_required
def like():
    session = db_session.create_session()
    photo_like = []    
    for i in list(session.query(Like).filter(Like.user_id == current_user.id)):
        photo_like.append(i.photo_id)      
    if int(request.form['id']) not in photo_like:
        like_db = Like(
                    user_id=current_user.id,
                            photo_id=int(request.form['id'])
                )
        photo = session.query(Photo).get(int(request.form['id']))
        photo.likes += 1
        session.add(like_db)
        btn_class = "btn btn-outline-danger btn-lg"
    else:
        like_delete = session.query(Like).filter(Like.user_id == current_user.id,
                                                 Like.photo_id == int(request.form['id'])).first()
        like_delete = session.query(Like).get(like_delete.id)
        photo = session.query(Photo).get(int(request.form['id']))
        photo.likes -= 1  
        session.delete(like_delete)
        btn_class = "btn btn-outline-secondary btn-lg"
    session.commit()       
    return jsonify({'value': photo.likes, 'class': btn_class, 'like': photo_like})


@app.route('/accept_invite', methods=['POST'])
@login_required
def accept_invite():
    session = db_session.create_session()
    invite = session.query(Invite).filter(Invite.sender_id == request.form['id'],
                                           Invite.receiver_id == current_user.id).first()
    if invite:
        friend_db = Friends(
            friend_id1=current_user.id,
            friend_id2=int(request.form['id'])
        )
        session.delete(invite)
        session.add(friend_db)
        friend1 = session.query(User).get(current_user.id)
        friend2 = session.query(User).get(request.form['id'])
        friend1.friends += 1
        friend2.friends += 1           
        session.commit() 
        return jsonify({'success': 'OK'})
    abort(404)


@app.route('/add_archive', methods=['POST'])
@login_required
def add_archive():
    session = db_session.create_session()
    invite = session.query(Invite).get(request.form['id'])
    invite.archive = True         
    session.commit() 
    return jsonify({'success': 'OK'})


@app.route('/first_comments', methods=['GET'])
@login_required
def first_comments():
    session = db_session.create_session()
    all_comments = list(session.query(Comment).filter(Comment.photo_id == 
                                                      request.args.get('id')))
    all_comments.reverse()
    first_comments = []
    for i in range(3):
        if i < len(all_comments):
            first_comments.append([all_comments[i].user.name, all_comments[i].user.surname,
                                   all_comments[i].text, all_comments[i].user_id])
    return jsonify({'comments': first_comments})
    


@app.route('/comment', methods=['POST'])
@login_required
def comment():
    session = db_session.create_session()
    comment_db = Comment(
            text=request.form['text'],
            user_id=current_user.id,
            photo_id=int(request.form['id'])
        )
    session.add(comment_db)
    session.commit()
    return jsonify({'name': current_user.name, 'surname': current_user.surname, 
                    'id': current_user.id, 'id_comment': comment_db.id})
    
    
@app.route('/message/<int:id>', methods=['GET', 'POST'])
@login_required
def chat(id):
    session = db_session.create_session()
    if not (current_user.id != id and session.query(User).filter(User.id == id).first()):
        return abort(404)
    list_message = list(session.query(Message).filter(
        (Message.sender_message_id == current_user.id) |
        (Message.sender_message_id == id)).filter(
            (Message.receiver_message_id == current_user.id) |
            (Message.receiver_message_id == id)))
    current_user2 = session.query(User).filter(User.id == current_user.id).first()
    user = session.query(User).filter(User.id == id).first()
    return render_template('message.html', title='Сообщения', id=id, 
                           list_message=list_message, current_user2=current_user2,
                           user=user)


@app.route('/list_message', methods=['GET'])
@login_required
def list_dialog():
    session = db_session.create_session()
    list_dialog = list(session.query(Dialog).filter(
        (Dialog.friend_dialog_id1 == current_user.id) |
        (Dialog.friend_dialog_id2 == current_user.id)))
    list_dialog.reverse()
    list_last_message = []
    for i in list_dialog:
        if i.friend_dialog_id1 == current_user.id:
            list_last_message.append({'text': i.message.text, 'user': i.friend_dialog2})
        else:
            list_last_message.append({'text': i.message.text, 'user': i.friend_dialog1})
    current_user2 = session.query(User).filter(User.id == current_user.id).first()
    return render_template('list_message.html', title='Сообщения', current_user2=current_user2,
                           list_last_message=list_last_message)



@app.route('/invite_friends', methods=['GET'])
@login_required
def invite_friends():
    session = db_session.create_session()
    invite = list(session.query(Invite).filter((Invite.receiver_id == current_user.id)))
    current_user2 = session.query(User).filter(User.id == current_user.id).first()
    return render_template('invite_friends.html', title='Заявки', current_user2=current_user2,
                           invite=invite)


@app.route('/invite_archive', methods=['GET'])
@login_required
def invite_archive():
    session = db_session.create_session()
    invite = list(session.query(Invite).filter((Invite.receiver_id == current_user.id)))
    current_user2 = session.query(User).filter(User.id == current_user.id).first()
    return render_template('invite_archive.html', title='Архив', current_user2=current_user2,
                           invite=invite)


@app.route('/friends/<int:id>', methods=['GET', 'POST'])
@login_required
def friends(id):
    session = db_session.create_session()
    friends = list(session.query(Friends).filter((Friends.friend_id1 == id) |
                                                 (Friends.friend_id2 == id)))
    friends = sort_friends(friends, id)
    current_user2 = session.query(User).filter(User.id == current_user.id).first()
    return render_template('friends.html', title='Друзья', id=id, friends=friends,
                           current_user2=current_user2)


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    session = db_session.create_session()
    current_user2 = session.query(User).filter(User.id == current_user.id).first()
    return render_template('search.html', title='Поиск', current_user2=current_user2)
    

@app.route('/user/<int:id>', methods=['GET', 'POST'])
@login_required
def user(id):
    flag = False
    invite_flag = False
    session = db_session.create_session()
    user = session.query(User).filter(User.id == id).first()
    current_user2 = session.query(User).filter(User.id == current_user.id).first()
    photos = list(session.query(Photo).filter(Photo.user_id == id))
    photos.reverse()
    dict_like = {}
    dict_comment = {}
    for i in photos:
        dict_like[i.id] = '♥️ ' + str(i.likes)
        commen = list(session.query(Comment).filter(Comment.photo_id == i.id))
        commen.reverse()
        dict_comment[i.id] = commen
    photo_like = []  
    for i in list(session.query(Like).filter(Like.user_id == current_user.id)):
        photo_like.append(i.photo_id)    
    if user:       
        if current_user.id == id:
            form = UploadPhoto()
            flag = True
            if form.validate_on_submit():
                file = form.photo.data
                filename = secure_filename(file.filename)
                path = os.path.join(os.getcwd(), 'static/img', filename)
                file.save(path)
                img = Image.open(path)
                filename = datetime.now().strftime("%d%m%y%H%M%S%f") + '.jpeg'
                img = img.convert('RGB')
                img.save(os.path.join(os.getcwd(), 'static/img', filename), quality=50)
                os.remove(path)
                photo = Photo(
                    img_name='img/' + filename,
                    user_id=current_user.id
                )
                session.add(photo)
                session.commit()
                return redirect('/user/' + str(id))
            return render_template('user.html', user=user, flag=flag, form=form,
                                   photos=photos, likes=dict_like, photo_like=photo_like,
                                   list_comment=dict_comment, invite_flag=invite_flag,
                                   current_user2=current_user2)
        else:
            invite = FriendForm()
            invite_flag = True 
            send = session.query(Invite).filter(Invite.sender_id == current_user.id,
                                                Invite.receiver_id == id).first()
            accept = session.query(Invite).filter(Invite.sender_id == id,
                                                  Invite.receiver_id == current_user.id).first()
            a = session.query(Friends).filter(Friends.friend_id1 == id,
                                              Friends.friend_id2 == current_user.id).first()
            if a:
                friend_invite = a
            else:
                friend_invite = session.query(Friends).filter(Friends.friend_id1 == current_user.id,
                                                              Friends.friend_id2 == id).first()
            if send and not accept and not friend_invite:
                type_invite = 1
            elif not send and not accept and not friend_invite:
                type_invite = 0
            elif not send and accept and not friend_invite:
                type_invite = 2
            else:
                type_invite = 3
            if invite.validate_on_submit() and invite.submit.data:
                if type_invite == 0:
                    invite_db = Invite(
                        sender_id=current_user.id,
                        receiver_id=id      
                        )
                    session.add(invite_db)
                elif type_invite == 1:
                    session.delete(session.query(Invite).get(send.id))    
                elif type_invite == 2:
                    friend_db = Friends(
                        friend_id1=current_user.id,
                        friend_id2=id
                        )
                    friend1 = session.query(User).get(current_user.id)
                    friend2 = session.query(User).get(id)
                    friend1.friends += 1
                    friend2.friends += 1
                    session.delete(session.query(Invite).get(accept.id))  
                    session.add(friend_db)
                elif type_invite == 3:
                    invite_db = Invite(
                        sender_id=id,
                        receiver_id=current_user.id      
                        )         
                    session.delete(session.query(Friends).get(friend_invite.id))
                    friend1 = session.query(User).get(current_user.id)
                    friend2 = session.query(User).get(id)
                    friend1.friends -= 1
                    friend2.friends -= 1          
                    session.add(invite_db)                    
                session.commit()   
                return redirect('')  
        return render_template('user.html', user=user, flag=flag, photos=photos,
                               likes=dict_like, photo_like=photo_like, list_comment=dict_comment,
                               invite_flag=invite_flag, invite=invite, type_invite=type_invite,
                               current_user2=current_user2)
    abort(404)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    if current_user.is_authenticated:
        return redirect("/")    
    form = RegisterForm()
    if form.validate_on_submit():
        y, m, d = form.birthday.data.year, form.birthday.data.month, form.birthday.data.day
        date_now = datetime.now()
        date_birthday = datetime(y, m, d)
        delta = (abs(date_birthday - date_now))
        if delta.days / 366 < 13:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Некорректная дата рождения")
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            surname=form.surname.data.lower().title(),
            name=form.name.data.lower().title(),
            email=form.email.data,
            birthday=form.birthday.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect("/")
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect("/")
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/', methods=['GET', 'POST'])
def index():
    session = db_session.create_session()
    form = LoginForm()
    if form.validate_on_submit():
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('index.html',
                               message="Неправильный логин или пароль",
                    form=form)
    if current_user.is_authenticated:
        friends = list(session.query(Friends).filter((Friends.friend_id1 == current_user.id) |
                                                     (Friends.friend_id2 == current_user.id)))
        list_id = []
        for i in friends:
            if i.friend_id1 == current_user.id: 
                list_id.append(i.friend_id2)
            else:
                list_id.append(i.friend_id1)
        photos = list(session.query(Photo).filter(Photo.user_id.in_(list_id)))
        photos.reverse()
        dict_like = {}
        dict_comment = {}
        for i in photos:
            dict_like[i.id] = '♥️ ' + str(i.likes)
            commen = list(session.query(Comment).filter(Comment.photo_id == i.id))
            commen.reverse()
            dict_comment[i.id] = commen
        photo_like = []    
        for i in list(session.query(Like).filter(Like.user_id == current_user.id)):
            photo_like.append(i.photo_id)          
        current_user2 = session.query(User).filter(User.id == current_user.id).first()
        return render_template('index.html', title="Social", form=form, photos=photos,
                               photo_like=photo_like, likes=dict_like, 
                               list_comment=dict_comment, current_user2=current_user2)
    return render_template('index.html', title="Social", form=form)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def main():
    try:
        db_session.global_init("db/social.sqlite")    
    except:
        pass 
    api.add_resource(photo_resources.PhotoResource, '/api/photo/<int:photo_id>')
    api.add_resource(photo_resources.PhotoDeleteResource, '/api/delete_photo/<int:photo_id>&<email>&<password>')
    api.add_resource(photo_resources.PhotoUserResource, '/api/get_photos/<int:user_id>')
    api.add_resource(comment_resources.CommentResource, '/api/comment/<int:comment_id>')
    api.add_resource(comment_resources.CommentDeleteResource, '/api/delete_comment/<int:comment_id>&<email>&<password>')
    api.add_resource(comment_resources.CommentListResource, '/api/comments')
    api.add_resource(comment_resources.CommentPhotoResource, '/api/get_comments/<int:photo_id>')
    api.add_resource(user_resources.UsersListResource, '/api/users') 
    api.add_resource(user_resources.UserResource, '/api/user/<int:user_id>')
    api.add_resource(user_resources.FriendsUserResource, '/api/friends/<int:user_id>')
    app.run()


if __name__ == '__main__':
    main()
