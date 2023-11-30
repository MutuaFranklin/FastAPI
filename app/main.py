
from fastapi import  FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import engine
from .routes import post, user, auth, vote


#create tables in postgres
#models.Base.metadata.create_all(bind=engine)


#Fast API App instance
app= FastAPI()

origins =["*"]

#Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)
   
#routes    
@app.get("/")
def root():
    return {"message": "The server is running successfully!"}