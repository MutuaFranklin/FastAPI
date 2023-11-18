
from fastapi import  FastAPI
from . import models
from .database import engine
from .routes import post, user, auth


#create tables in postgres
models.Base.metadata.create_all(bind=engine)


#Fast API App instance
app= FastAPI()

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
   
#routes    
@app.get("/")
def root():
    return {"Message": "Test case one"}