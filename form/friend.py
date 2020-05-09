# -*- coding: utf8 -*-
from flask_wtf import FlaskForm
from wtforms import SubmitField


class FriendForm(FlaskForm):
    # Форма с кнопкой заявок в друзья
    submit = SubmitField()