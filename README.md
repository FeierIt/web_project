# Socialize
![](https://github.com/f31er/web_project/blob/master/static/img/big_logo.png)  
**Socialize** - это социальная сеть для **общения**. В ней вы сможете делиться своими **фотографиями** и cвоими эмоциями в **комментариях**.
# API
* Фотографии
  * **/api/photo/<int:photo_id>** - получения информации о фотографии по её id.
  * **/api/delete_photo/<int:photo_id>&<email>&<password>** - удаление фотографии по id.
  * **/api/get_photos/<int:user_id>** - все фотографии по id пользователя.
