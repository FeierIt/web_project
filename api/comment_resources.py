from data import db_session
from data.photo import Photo
from data.users import User
from data.comment import Comment
from flask import jsonify
from flask_restful import reqparse, abort, Resource
parser = reqparse.RequestParser()
parser.add_argument('photo_id', required=True, type=int)
parser.add_argument('text', required=True)
parser.add_argument('password', required=True)
parser.add_argument('email', required=True)


class CommentPhotoResource(Resource):
    def get(self, photo_id):
        abort_if_photo_not_found(photo_id)
        session = db_session.create_session()
        comments = session.query(Comment).filter(Comment.photo_id == photo_id)
        list_comments = []
        for i in comments:
            list_comments.append({'comment_id': i.id, 'text': i.text,
                                  'user': {'id': i.user_id, 'name': i.user.name,
                                           'surname': i.user.surname}})
        return jsonify({'comments': list_comments})   
    
    
class CommentResource(Resource):
    def get(self, comment_id):
        abort_if_comment_not_found(comment_id)
        session = db_session.create_session()
        comment = session.query(Comment).get(comment_id)
        return jsonify({'comment_id': comment.id, 'text': comment.text,
                        'photo_id': comment.photo_id,
                        'user': {'id': comment.user_id, 
                                 'name': comment.user.name,
                                 'surname': comment.user.surname}})   


class CommentListResource(Resource):   
    def post(self):
        args = parser.parse_args()
        abort_if_photo_not_found(args['photo_id'])
        session = db_session.create_session()      
        user = session.query(User).filter(User.email == args['email']).first()
        if user and user.check_password(args['password']):     
            comment_db = Comment(
                text=args['text'],
                user_id=user.id,
                photo_id=args['photo_id']
            )
            session.add(comment_db)
            session.commit()            
            return jsonify({'success': 'OK'})
        abort(404, message='Incorrect email or password')
      
        
class CommentDeleteResource(Resource):      
    def delete(self, comment_id, email, password):
        abort_if_comment_not_found(comment_id)    
        session = db_session.create_session()      
        user = session.query(User).filter(User.email == email).first()
        if user and user.check_password(password):
            comment = session.query(Comment).get(comment_id)
            if comment.user_id == user.id:
                session.delete(comment)
                session.commit()
                return jsonify({'success': 'OK'})    
            abort(404, message='You can not delete this comment')
        abort(404, message='Incorrect email or password')
        

def abort_if_photo_not_found(photo_id):
    session = db_session.create_session()
    photo = session.query(Photo).get(photo_id)
    if not photo:
        abort(404, message=f"Photo {photo_id} not found")    
        
    
def abort_if_comment_not_found(comment_id):
    session = db_session.create_session()
    comment = session.query(Comment).get(comment_id)
    if not comment:
        abort(404, message=f"Comment {comment_id} not found")    