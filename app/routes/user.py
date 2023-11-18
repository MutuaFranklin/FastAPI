from .. import models, schemas, utils
from fastapi import Depends, status, HTTPException, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from app import oauth2


router = APIRouter(
     prefix="/users",
     tags=['Users']
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user: schemas.CreateUser, db: Session =Depends(get_db)):
    
    #hash the password
    hashed_password =utils.hash(user.password)
    user.password =hashed_password
    
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)    
    return new_user


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.UserResponse)
def get_user(id:int, db: Session =Depends(get_db),current_user: int =Depends(oauth2.get_current_user)):    
    user=db.query(models.User).filter(models.User.id == id).first()  
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail =f"User with id: {id} does not exist")
          
    return user
