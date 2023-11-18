from fastapi import Depends, status, HTTPException, APIRouter
from .. import models, utils, oauth2
from sqlalchemy.orm import Session
from ..database import get_db
from fastapi.security.oauth2 import OAuth2PasswordRequestForm




router = APIRouter(
     tags=['Authentication']
)




@router.post("/login", status_code=status.HTTP_200_OK )
#def login_user(user_credentials: schemas.UserLogin,db: Session =Depends(get_db)):
def login_user(user_credentials: OAuth2PasswordRequestForm=Depends(),db: Session =Depends(get_db)):
    #user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()  
    
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail =f"Invalid Credentials")
    
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail =f"Invalid Credentials")
        
    #create token
    access_token=oauth2.create_access_token(data = {"user_id": user.id})
    #return token
    return {"access_token": access_token, "token_type": "bearer"}

