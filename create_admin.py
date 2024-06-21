from db import models, schemas, crud
from db.crud import get_db
from main import get_password_hash

username = input('用户名：')
password = input('输入密码：')
password_2 = input('再次输入以确认密码：')

if password != password_2:
    print('两次输入的密码不匹配，请重新输入')
with get_db() as db:
    crud.create_admin(db, schemas.AdminSchema(username=username, password=get_password_hash(password)))
    print('创建成功')