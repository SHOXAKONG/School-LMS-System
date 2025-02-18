from jose import jwt, JWTError
import time
from fastapi import FastAPI, Request, Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models import *

app = FastAPI()

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

@app.middleware("http")
async def global_middleware(request: Request, call_next):
    start_time = time.time()

    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            request.state.current_user = User(
                username=payload.get("sub"),
                role=payload.get("role"),
                branch_id=payload.get("branch_id")
            )
        except JWTError:
            request.state.current_user = None
    else:
        request.state.current_user = None

    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"[{request.method}] {request.url.path} completed in {process_time:.4f} sec")
    return response


def get_current_user(request: Request) -> User:
    user = request.state.current_user
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or not authenticated")
    return user