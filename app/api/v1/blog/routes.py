from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.schemas.blog_schema import BlogCreateSchema, BlogUpdateSchema 
from app.utils.response import SuccessResponse, ErrorResponse
from app.api.v1.blog.service import (
    create_blog, get_all_blogs, update_blog, delete_blog, get_blog_by_id
)
from app.db.session import get_db
from app.dependencies.auth_dependency import get_current_user
from app.dependencies.api_key_dependency import verify_api_keys
from app.utils.blog_validator import validate_blog_data

router = APIRouter(
    prefix="/blogs",
    tags=["Blogs"],
    dependencies=[Depends(verify_api_keys)]  # This ensures ALL endpoints in this router require API keys
)


@router.post("/post_blog", summary="Create a new blog", description="Create a blog post (Requires API Keys + JWT Token)")
def create_blog_post(
    data: BlogCreateSchema, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    is_valid, msg = validate_blog_data(data.title, data.content)
    if not is_valid:
        return ErrorResponse(msg, status_code=400)
 

    """Create a new blog post (Authentication required)"""
    blog = create_blog(db, data, current_user.id)
    return SuccessResponse(
        message="Blog created successfully", 
        status_code=status.HTTP_201_CREATED, 
        data={
            "blog_id": blog.id, 
            "title": blog.title, 
            "slug": blog.slug,
            "author_id": blog.author_id
        }
    )


@router.get("/get_blogs", summary="Get all blogs", description="Retrieve all blog posts (Requires API Keys only)")
def read_all_blogs(db: Session = Depends(get_db)):
    """Get all blog posts - Only API keys required"""
    blogs = get_all_blogs(db)
    return SuccessResponse(
        message="Blogs retrieved successfully", 
        status_code=status.HTTP_200_OK, 
        data=[
            {
                "blog_id": blog.id, 
                "title": blog.title, 
                "slug": blog.slug,
                "content": blog.content[:200] + "..." if len(blog.content) > 200 else blog.content,
                "author_id": blog.author_id
            } 
            for blog in blogs
        ]
    )


@router.get("/blog/{blog_id}", summary="Get single blog", description="Get a specific blog by ID (Requires API Keys only)")
def read_single_blog(blog_id: int, db: Session = Depends(get_db)):
    """Get a single blog post by ID - Only API keys required"""
    blog = get_blog_by_id(db, blog_id)
    
    if not blog:
        return ErrorResponse(message="Blog not found", status_code=status.HTTP_404_NOT_FOUND)
    
    return SuccessResponse(
        message="Blog retrieved successfully", 
        status_code=status.HTTP_200_OK, 
        data={
            "blog_id": blog.id, 
            "title": blog.title, 
            "slug": blog.slug,
            "content": blog.content,
            "author_id": blog.author_id
        }
    )


@router.put("/update_blog/{blog_id}", summary="Update blog", description="Update a blog post (Requires API Keys + JWT Token)")
def update_blog_post(
    blog_id: int, 
    data: BlogUpdateSchema, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    is_valid, msg = validate_blog_data(data.title, data.content)
    if not is_valid:
        return ErrorResponse(msg, status_code=400)
        
    """Update a blog post (Only the author can update)"""
    result = update_blog(db, blog_id, data, current_user.id)

    if result is None:
        return ErrorResponse("Blog not found", status_code=status.HTTP_404_NOT_FOUND)
    if result == "Unauthorized":
        return ErrorResponse("Unauthorized - You can only update your own blogs", 
                           status_code=status.HTTP_403_FORBIDDEN)

    return SuccessResponse(
        message="Blog updated successfully", 
        status_code=status.HTTP_200_OK, 
        data={
            "blog_id": result.id, 
            "title": result.title, 
            "slug": result.slug,
            "content": result.content
        }
    )


@router.delete("/delete_blog/{blog_id}", summary="Delete blog", description="Delete a blog post (Requires API Keys + JWT Token)")
def delete_blog_post(
    blog_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    """Delete a blog post (Only the author can delete)"""
    result = delete_blog(db, blog_id, current_user.id)

    if result is None:
        return ErrorResponse("Blog not found", status_code=status.HTTP_404_NOT_FOUND)
    if result == "Unauthorized":
        return ErrorResponse("Unauthorized - You can only delete your own blogs", 
                           status_code=status.HTTP_403_FORBIDDEN)

    return SuccessResponse(
        message="Blog deleted successfully", 
        status_code=status.HTTP_200_OK
    )