# -*- coding: utf8 -*-
import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Dialog(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'dialog'
        
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    friend_dialog_id1 = sqlalchemy.Column(sqlalchemy.Integer, 
                                          sqlalchemy.ForeignKey("users.id"))
    friend_dialog_id2 = sqlalchemy.Column(sqlalchemy.Integer, 
                                          sqlalchemy.ForeignKey("users.id"))
    message_id = sqlalchemy.Column(sqlalchemy.Integer, 
                                   sqlalchemy.ForeignKey("message.id"))
    friend_dialog1 = orm.relation('User', foreign_keys=[friend_dialog_id1]) 
    friend_dialog2 = orm.relation('User', foreign_keys=[friend_dialog_id2]) 
    message = orm.relation('Message')
