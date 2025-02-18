from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class Role(str, Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"


class User(BaseModel):
    username: str
    role: Role
    branch_id: Optional[int] = None


class Branch(BaseModel):
    id: int
    name: str
    admin_username: str


class Teacher(BaseModel):
    id: int
    name: str
    branch_id: int


class Student(BaseModel):
    id: int
    name: str
    branch_id: int


class Group(BaseModel):
    id: int
    name: str
    teacher_id: int
    student_ids: List[int]