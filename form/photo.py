# -*- coding: utf8 -*-
from flask_wtf import FlaskForm
from wtforms import SubmitField
from flask_wtf.file import FileField, FileAllowed, FileRequired


class UploadPhoto(FlaskForm):
    # Форма загрузки фотографии
    photo = FileField('Загрузить фото', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only'),
        FileRequired()
    ])
    submit = SubmitField('Загрузить')