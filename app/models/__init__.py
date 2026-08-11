from app.models import users
from models import student, teacher

def create_table():
    student.create_table()
    teacher.create_table()
    users.create_table()