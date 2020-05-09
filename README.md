# Socialize
![](https://github.com/f31er/web_project/blob/master/static/img/big_logo.png)  
**Socialize** - это социальная сеть для **общения**. В ней вы сможете делиться своими **фотографиями** и cвоими эмоциями в **комментариях**.
# API
* Пользователи
  + **GET**
    - **/api/users88 - все пользователи сайта.
    - **/api/user/int:user_id** - информация по определенному пользователю по его id.
    - **/api/friends/int:user_id** - информаци о друзьях пользователя по его id.
* Фотографии
  + **GET**
    - **/api/get_photos/int:user_id** - все фотографии по id пользователя.
    -**/api/photo/<int:photo_id>** - информация о фотографии по её id.
  + **DELETE**
    - **/api/delete_photo/int:photo_id&email&password** - удаление фотографии по id.
* Комментарии
  + **GET**
    - **/api/comment/int:comment_id>** - информации комментария по его id.
    - **/api/get_comments/int:photo_id** - получить все комментарии под фотографией.
  + **POST**
    - **/api/comments** - отправка комментария с обязательными полями(photo_id, text, email, password).  
    ```post('http://localhost:5000/api/comments',json={'photo_id': 2, 'email': 'mail@gmail.com', 'password': 'qwerty', 'text': 'test'})```
  + **DELETE**
    - **/api/delete_comment/int:comment_id&email&password** - удаление комментария по id.
