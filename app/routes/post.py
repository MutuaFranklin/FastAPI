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

@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.PostVotesResponse])
def get_my_posts(db: Session=Depends(get_db), current_user: int =Depends(oauth2.get_current_user)):
    # posts=db.query(models.Post).filter(models.Post.owner_id == current_user.id).all()
    # print(current_user.id)
    posts = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .outerjoin(models.Vote, models.Vote.post_id == models.Post.id)
        .filter(models.Post.owner_id == current_user.id)
        .group_by(models.Post.id)
        .all()
    )
  # Convert the tuple into a list of PostVotesResponse Pydantic models
    results = [
        schemas.PostVotesResponse(
            post=schemas.PostResponse(
                id=post.id,
                title=post.title,
                content=post.content,
                published=post.published,
                created_at=post.created_at,
                owner=schemas.UserResponse(
                    id=post.owner.id,
                    email=post.owner.email,
                    created_at=post.owner.created_at,
                ),
            ),
            votes=votes,
        )
        for post, votes in posts
    ]

    return results

@router.get("/all", response_model=List[schemas.PostVotesResponse], status_code=status.HTTP_200_OK)
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

  # Convert the tuple into a list of PostVotesResponse Pydantic models
    results = [
        schemas.PostVotesResponse(
            post=schemas.PostResponse(
                id=post.id,
                title=post.title,
                content=post.content,
                published=post.published,
                created_at=post.created_at,
                owner=schemas.UserResponse(
                    id=post.owner.id,
                    email=post.owner.email,
                    created_at=post.owner.created_at,
                ),
            ),
            votes=votes,
        )
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


@router.get("/{id}",  response_model=schemas.PostVotesResponse)
def get_post(id:int, db: Session =Depends(get_db), current_user: int =Depends(oauth2.get_current_user)):    
    # Directly use the result of the query without assigning to a variable
    post_and_votes = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .outerjoin(models.Vote, models.Vote.post_id == models.Post.id)
        .filter(models.Post.id == id)
        .group_by(models.Post.id)
        .first()
    )

    if not post_and_votes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} was not found")

    # Unpack the tuple only if it's not None
    post, votes = post_and_votes    
    
    # Convert the tuple into PostVotesResponse Pydantic models
    post_response = schemas.PostVotesResponse(
        post=schemas.PostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            published=post.published,
            created_at=post.created_at,
            owner=schemas.UserResponse(
                id=post.owner.id,
                email=post.owner.email,
                created_at=post.owner.created_at,
            )
        ),
        votes=votes,
    )
    
    return post_response


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

