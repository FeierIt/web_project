# -*- coding: utf8 -*-
import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class Message(SqlAlchemyBase, UserMixin, SerializerMixin):
    # Таблица с сообщениями
    __tablename__ = 'message'
        
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    sender_message_id = sqlalchemy.Column(sqlalchemy.Integer, 
                                          sqlalchemy.ForeignKey("users.id"))
    receiver_message_id = sqlalchemy.Column(sqlalchemy.Integer, 
                                            sqlalchemy.ForeignKey("users.id"))
    sender_message = orm.relation('User', foreign_keys=[sender_message_id]) 
    receiver_message = orm.relation('User', foreign_keys=[receiver_message_id]) 
    dialog = orm.relation('Dialog', back_populates='message')