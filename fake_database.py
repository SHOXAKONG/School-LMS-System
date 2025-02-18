from models import *

fake_users_db = {
    "superadmin": {"username": "superadmin", "role": Role.SUPERADMIN, "password": "secret"},
    "admin1": {"username": "admin1", "role": Role.ADMIN, "branch_id": 1, "password": "secret"},
    "teacher1": {"username": "teacher1", "role": Role.TEACHER, "branch_id": 1, "password": "secret"},
    "teacher2": {"username": "teacher2", "role": Role.TEACHER, "branch_id": 1, "password": "secret"},
    "teacher3": {"username": "teacher3", "role": Role.TEACHER, "branch_id": 2, "password": "secret"},
    "teacher4": {"username": "teacher4", "role": Role.TEACHER, "branch_id": 2, "password": "secret"}
}

fake_branches = [
    Branch(id=1, name="Branch 1", admin_username="admin1"),
    Branch(id=2, name="Branch 2", admin_username="admin2")
]

fake_teachers = [
    Teacher(id=1, name="Teacher One", branch_id=1),
    Teacher(id=2, name="Teacher Two", branch_id=1),
    Teacher(id=3, name="Teacher Three", branch_id=2),
    Teacher(id=4, name="Teacher Four", branch_id=2)
]

fake_students = [
    Student(id=1, name="Student One", branch_id=1),
    Student(id=2, name="Student Two", branch_id=1),
    Student(id=3, name="Student Three", branch_id=1),
    Student(id=4, name="Student Four", branch_id=1),
    Student(id=5, name="Student Five", branch_id=2),
    Student(id=6, name="Student Six", branch_id=2),
    Student(id=7, name="Student Seven", branch_id=2),
    Student(id=8, name="Student Eight", branch_id=2)
]

fake_groups = [
    Group(id=1, name="Group A", teacher_id=1, student_ids=[1, 2]),
    Group(id=2, name="Group B", teacher_id=2, student_ids=[1, 2, 3, 4]),
    Group(id=3, name="Group C", teacher_id=1, student_ids=[3, 4]),
    Group(id=4, name="Group D", teacher_id=3, student_ids=[5, 6]),
    Group(id=5, name="Group E", teacher_id=4, student_ids=[5, 6, 7, 8]),
    Group(id=6, name="Group F", teacher_id=3, student_ids=[7, 8]),
]

teacher_mapping = {
    "teacher1": 1,
    "teacher2": 2,
    "teacher3": 3,
    "teacher4": 4
}