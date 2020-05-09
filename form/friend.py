# -*- coding: utf8 -*-
from flask_wtf import FlaskForm
from wtforms import SubmitField


class FriendForm(FlaskForm):
    submit = SubmitField()