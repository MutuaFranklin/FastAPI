from app import oauth2
from .. import models, schemas
from fastapi import Depends, status, HTTPException, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from fastapi.responses import JSONResponse
from typing import List, Optional
from sqlalchemy import func


router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.PostResponse])
def get_my_posts(db: Session=Depends(get_db), current_user: int =Depends(oauth2.get_current_user)):
    posts=db.query(models.Post).filter(models.Post.owner_id == current_user.id).all()
    # print(current_user.id)
    return posts

@router.get("/all", response_model=List[dict], status_code=status.HTTP_200_OK)
# @router.get("/all", response_model=List[schemas.PostVotesResponse], status_code=status.HTTP_200_OK)
def get_all_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 20, skip: int = 0, search: Optional[str] = "",
):
    # Apply filter() before limit() or offset()
    posts = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .outerjoin(models.Vote, models.Vote.post_id == models.Post.id)
        .filter(models.Post.title.contains(search))
        .group_by(models.Post.id)
        .limit(limit)
        .offset(skip)
        .all()
    )

    # Convert the tuple into a list of dictionaries
    results = [
        {
            "post": {key: value for key, value in post.__dict__.items() if not key.startswith('_')},
            "votes": votes,
        }
        for post, votes in posts
    ]

    return results


@router.post("/", status_code=status.HTTP_201_CREATED,response_model=schemas.PostResponse )
def create_post(post: schemas.CreatePost, db: Session =Depends(get_db), current_user: int =Depends(oauth2.get_current_user)):
    #new_post = models.Post(title=post.title, content=post.content, published=post.published)
    new_post = models.Post(owner_id=current_user.id,**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)    
    return new_post


@router.get("/{id}",  response_model=schemas.PostResponse)
def get_post(id:int, db: Session =Depends(get_db), current_user: int =Depends(oauth2.get_current_user)):    
    post=db.query(models.Post).filter(models.Post.id == id).first()  
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail =f"Post with id: {id} was not found")
          
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int, db: Session =Depends(get_db), current_user: int =Depends(oauth2.get_current_user)):    
    post_query =db.query(models.Post).filter(models.Post.id == id)
    
    post = post_query.first()
    
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail =f"Post with id: {id} was not found")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail =f"Not authorized to perform requested action")

    #post_query.delete(synchronized_session =False)
    db.delete(post)
    db.commit()    
    message = f"Post with id: {id} was successfully deleted"
    return JSONResponse(content={"message": message}, status_code=status.HTTP_204_NO_CONTENT)
          

@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(id:int, updated_post: schemas.UpdatePost, db: Session =Depends(get_db), current_user: int =Depends(oauth2.get_current_user)): 
       
    post_query=db.query(models.Post).filter(models.Post.id == id)
    
    existing_post= post_query.first()
    
    if existing_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail =f"Post with id: {id} was not found")
    
    if existing_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail =f"Not authorized to perform requested action")
    
    #post_query.update(post.dict(), synchronize_session=False) 
    # Update the existing post with the values from the updated_post
    for key, value in updated_post.dict().items():
        setattr(existing_post, key, value)    
    db.commit()    
    return post_query.first()  

