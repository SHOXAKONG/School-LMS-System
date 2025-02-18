from fake_database import *
from datetime import datetime, timedelta
from middleware import *


# --- Authentication Endpoints ---
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token_data = {
        "sub": user["username"],
        "role": user["role"],
        "branch_id": user.get("branch_id")
    }
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data.update({"exp": expire})
    access_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/branches")
def get_branches(current_user: User = Depends(get_current_user)):
    if current_user.role != Role.SUPERADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return fake_branches


# --- Teacher Router ---
teacher_router = APIRouter(prefix="/teachers", tags=["Teachers"])


@teacher_router.post("")
def create_teacher(teacher: Teacher, current_user: User = Depends(get_current_user)):
    if current_user.role != Role.ADMIN or teacher.branch_id != current_user.branch_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    fake_teachers.append(teacher)
    return teacher


@teacher_router.get("")
def get_teachers(current_user: User = Depends(get_current_user)):
    if current_user.role not in [Role.ADMIN, Role.TEACHER]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    if current_user.role == Role.TEACHER:
        teacher_id = teacher_mapping.get(current_user.username)
        if teacher_id is None:
            raise HTTPException(status_code=404, detail="Teacher not found")
        teacher = next((t for t in fake_teachers if t.id == teacher_id and t.branch_id == current_user.branch_id), None)
        if teacher is None:
            raise HTTPException(status_code=404, detail="Teacher not found")
        return teacher
    else:
        return [t for t in fake_teachers if t.branch_id == current_user.branch_id]


@teacher_router.put("/{teacher_id}")
def update_teacher(teacher_id: int, teacher: Teacher, current_user: User = Depends(get_current_user)):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    index = next((i for i, t in enumerate(fake_teachers) if t.id == teacher_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Teacher not found")
    if fake_teachers[index].branch_id != current_user.branch_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    if teacher.id != teacher_id:
        raise HTTPException(status_code=400, detail="Teacher id mismatch")
    fake_teachers[index] = teacher
    return teacher


@teacher_router.delete("/{teacher_id}")
def delete_teacher(teacher_id: int, current_user: User = Depends(get_current_user)):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    index = next((i for i, t in enumerate(fake_teachers) if t.id == teacher_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Teacher not found")
    if fake_teachers[index].branch_id != current_user.branch_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    deleted_teacher = fake_teachers.pop(index)
    return deleted_teacher


# --- Student Router ---
student_router = APIRouter(prefix="/students", tags=["Students"])


@student_router.post("")
def create_student(student: Student, current_user: User = Depends(get_current_user)):
    if current_user.role != Role.ADMIN or student.branch_id != current_user.branch_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    fake_students.append(student)
    return student


@student_router.get("")
def get_students(current_user: User = Depends(get_current_user)):
    if current_user.role == Role.STUDENT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    if current_user.role == Role.TEACHER:
        teacher = next(
            (t for t in fake_teachers if t.name == current_user.username and t.branch_id == current_user.branch_id),
            None
        )
        if teacher:
            teacher_groups = [g for g in fake_groups if g.teacher_id == teacher.id]
            student_ids = {s for g in teacher_groups for s in g.student_ids}
            return [s for s in fake_students if s.id in student_ids and s.branch_id == current_user.branch_id]
        else:
            raise HTTPException(status_code=404, detail="Teacher not found")
    return [s for s in fake_students if s.branch_id == current_user.branch_id]


@student_router.put("/{student_id}")
def update_student(student_id: int, student: Student, current_user: User = Depends(get_current_user)):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    index = next((i for i, s in enumerate(fake_students) if s.id == student_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Student not found")
    if fake_students[index].branch_id != current_user.branch_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    if student.id != student_id:
        raise HTTPException(status_code=400, detail="Student id mismatch")
    fake_students[index] = student
    return student


@student_router.delete("/{student_id}")
def delete_student(student_id: int, current_user: User = Depends(get_current_user)):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    index = next((i for i, s in enumerate(fake_students) if s.id == student_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Student not found")
    if fake_students[index].branch_id != current_user.branch_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    deleted_student = fake_students.pop(index)
    return deleted_student


# --- Group Router ---
group_router = APIRouter(prefix="/groups", tags=["Groups"])


@group_router.post("")
def create_group(group: Group, current_user: User = Depends(get_current_user)):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    teacher = next(
        (t for t in fake_teachers if t.id == group.teacher_id and t.branch_id == current_user.branch_id),
        None
    )
    if teacher is None:
        raise HTTPException(status_code=400, detail="Tanlangan teacher mavjud emas yoki sizning branchga tegishli emas")
    for student_id in group.student_ids:
        student = next((s for s in fake_students if s.id == student_id), None)
        if student is None:
            raise HTTPException(status_code=400, detail=f"Student with id {student_id} topilmadi")
        if student.branch_id != current_user.branch_id:
            raise HTTPException(status_code=400, detail=f"Student with id {student_id} sizning branchga tegishli emas")
    fake_groups.append(group)
    return group


@group_router.get("")
def get_groups(current_user: User = Depends(get_current_user)):
    if current_user.role == Role.STUDENT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    if current_user.role == Role.TEACHER:
        teacher_id = teacher_mapping.get(current_user.username)
        if teacher_id is None:
            raise HTTPException(status_code=404, detail="Teacher not found")
        return [g for g in fake_groups if g.teacher_id == teacher_id]
    if current_user.role == Role.ADMIN:
        branch_student_ids = [st.id for st in fake_students if st.branch_id == current_user.branch_id]
        return [g for g in fake_groups if any(s in branch_student_ids for s in g.student_ids)]
    return fake_groups


@group_router.put("/{group_id}")
def update_group(group_id: int, group: Group, current_user: User = Depends(get_current_user)):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    index = next((i for i, g in enumerate(fake_groups) if g.id == group_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Group not found")
    teacher = next(
        (t for t in fake_teachers if t.id == group.teacher_id and t.branch_id == current_user.branch_id),
        None
    )
    if teacher is None:
        raise HTTPException(status_code=400, detail="Tanlangan teacher mavjud emas yoki sizning branchga tegishli emas")
    for student_id in group.student_ids:
        student = next((s for s in fake_students if s.id == student_id), None)
        if student is None:
            raise HTTPException(status_code=400, detail=f"Student with id {student_id} topilmadi")
        if student.branch_id != current_user.branch_id:
            raise HTTPException(status_code=400, detail=f"Student with id {student_id} sizning branchga tegishli emas")
    if group.id != group_id:
        raise HTTPException(status_code=400, detail="Group id mos kelmadi")
    fake_groups[index] = group
    return group


@group_router.delete("/{group_id}")
def delete_group(group_id: int, current_user: User = Depends(get_current_user)):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    index = next((i for i, g in enumerate(fake_groups) if g.id == group_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Group not found")
    group = fake_groups[index]
    teacher = next((t for t in fake_teachers if t.id == group.teacher_id), None)
    if teacher is None or teacher.branch_id != current_user.branch_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this group")
    deleted_group = fake_groups.pop(index)
    return deleted_group


app.include_router(teacher_router)
app.include_router(student_router)
app.include_router(group_router)
