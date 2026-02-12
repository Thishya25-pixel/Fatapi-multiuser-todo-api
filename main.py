from fastapi import FastAPI,Depends,HTTPException
from pydantic import BaseModel
import models
import schemas
from database import engine,SessionLocal
from sqlalchemy.orm import Session
import auth
from fastapi.security import OAuth2AuthorizationCodeBearer,OAuth2PasswordBearer,OAuth2PasswordRequestForm

from jose import JWTError,jwt

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="login")

app=FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            auth.SECRET_KEY,
            algorithms=[auth.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(
        models.User.username == username
    ).first()

    if user is None:
        raise credentials_exception

    return user



@app.post("/signup",response_model=schemas.UserResponse)
def signup(user:schemas.UserCreate,db:Session=Depends(get_db)):
   existing=db.query(models.User).filter(models.User.username==user.username).first()
   if existing:
       raise HTTPException(status_code=400,detail="Username already exists")
   
   new_user=models.User(username=user.username,hashed_password=auth.hashed_password(user.password))
   db.add(new_user)
   db.commit()
   db.refresh(new_user)
   return new_user


from fastapi.security import OAuth2PasswordRequestForm

from fastapi.security import OAuth2PasswordRequestForm

@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(
        models.User.username == form_data.username
    ).first()

    if not db_user or not auth.verify_password(
        form_data.password,
        db_user.hashed_password
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth.create_acess_tokens({"sub": db_user.username})
    return {
        "access_token": token,
        "token_type": "bearer"
    }


@app.post("/todos",response_model=schemas.TodoResponse)
def create_todo(todo:schemas.TodoCreate,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
    new_todo=models.Todo(title=todo.title,owner_id=current_user.id)
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo


@app.get("/todos",response_model=list[schemas.TodoResponse])
def get_todod(db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
    return db.query(models.Todo).filter(models.Todo.owner_id==current_user.id).all()


@app.put("/todos/{todo_id}",response_model=schemas.TodoResponse)
def update_todo(todo_id:int,todo:schemas.TodoCreate,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
    db_todo=db.query(models.Todo).filter(models.Todo.id==todo_id,models.Todo.owner_id==current_user.id).first()

    if not db_todo:
        raise HTTPException(status_code=404,detail="Todo not found")
    
    db_todo.title=todo.title
    db_todo.completed=True
    db.commit()
    db.refresh(db_todo)

    return db_todo


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id:int,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
    db_todo=db.query(models.Todo).filter(models.Todo.id==todo_id,models.Todo.owner_id==current_user.id).first()
    if not db_todo:
        raise HTTPException(status_code=404,detail="Todo not found")
    
    db.delete(db_todo)
    db.commit()

    return {"message":"Todo deleted succesfully"}
