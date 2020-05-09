import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Avatar(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'avatar'
    
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    photo_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("photo.id"))
    photo = orm.relation('Photo')
    user = orm.relation('User', back_populates='avatar')