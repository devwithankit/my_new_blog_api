from fastapi import APIRouter, Depends, status, File, UploadFile, Form
from typing import Optional
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
from app.utils.image_utils import validate_image_file

router = APIRouter(
    prefix="/blogs",
    tags=["Blogs"],
    dependencies=[Depends(verify_api_keys)]
)


@router.post("/post_blog", summary="Create a new blog", description="Create a blog post (Requires API Keys + JWT Token)")
async def create_blog_post(
    title: str = Form(...),
    content: str = Form(...),
    banner_image: UploadFile = File(None),
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    """Create a new blog post with optional banner image (Only authenticated users can create)"""
    
    # Validate blog data
    is_valid, msg = validate_blog_data(title, content)
    if not is_valid:
        return ErrorResponse(msg, status_code=400)
    
    # Validate image file if provided
    if banner_image and banner_image.filename:
        # Read file content for validation
        image_content = await banner_image.read()
        is_valid_image, image_msg = validate_image_file(banner_image.filename, image_content)
        if not is_valid_image:
            return ErrorResponse(image_msg, status_code=400)
        
        # Reset file pointer after validation
        await banner_image.seek(0)
    
    # IMPORTANT: AWAIT the async function
    blog = await create_blog(db, title, content, current_user.id, banner_image if banner_image and banner_image.filename else None)
    
    return SuccessResponse(
        message="Blog created successfully", 
        status_code=status.HTTP_201_CREATED, 
        data={
            "blog_id": blog.id, 
            "title": blog.title, 
            "slug": blog.slug,
            "author_id": blog.author_id,
            "banner_image": blog.image_url if hasattr(blog, "image_url") else blog.banner_image
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
                "author_id": blog.author_id,
                "banner_image": blog.image_url if hasattr(blog, "image_url") else blog.banner_image
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
            "author_id": blog.author_id,
            "banner_image": blog.image_url if hasattr(blog, "image_url") else blog.banner_image,
            "created_at": blog.created_at.isoformat() if hasattr(blog, 'created_at') and blog.created_at else None,
            "updated_at": blog.updated_at.isoformat() if hasattr(blog, 'updated_at') and blog.updated_at else None
        }
    )


@router.put("/update_blog/{blog_id}", summary="Update blog", description="Update a blog post with optional image")
async def update_blog_post(
    blog_id: int,
    title: str = Form(...),
    content: str = Form(...),
    banner_image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a blog post (Only the author can update)"""
    
    # Validate blog data
    is_valid, msg = validate_blog_data(title, content)
    if not is_valid:
        return ErrorResponse(msg, status_code=400)
    
    # Validate image if provided
    if banner_image and banner_image.filename:
        image_content = await banner_image.read()
        is_valid_img, img_msg = validate_image_file(banner_image.filename, image_content)
        if not is_valid_img:
            return ErrorResponse(img_msg, status_code=400)
        await banner_image.seek(0)
    
    # AWAIT the async update function
    result = await update_blog(db, blog_id, title, content, current_user.id, banner_image if banner_image and banner_image.filename else None)

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
            "content": result.content,
            "banner_image": result.image_url if hasattr(result, 'image_url') else result.banner_image
        }
    )


@router.delete("/delete_blog/{blog_id}", summary="Delete blog", description="Delete a blog post")
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
# from fastapi import APIRouter, Depends, status, HTTPException,File, UploadFile, Form
# from sqlalchemy.orm import Session
# from app.schemas.blog_schema import BlogCreateSchema, BlogUpdateSchema 
# from app.utils.response import SuccessResponse, ErrorResponse
# from app.api.v1.blog.service import (
#     create_blog, get_all_blogs, update_blog, delete_blog, get_blog_by_id
# )
# from app.db.session import get_db
# from app.dependencies.auth_dependency import get_current_user
# from app.dependencies.api_key_dependency import verify_api_keys
# from app.utils.blog_validator import validate_blog_data
# from app.utils.image_utils import validate_image_file

# router = APIRouter(
#     prefix="/blogs",
#     tags=["Blogs"],
#     dependencies=[Depends(verify_api_keys)]  # This ensures ALL endpoints in this router require API keys
# )


# @router.post("/post_blog", summary="Create a new blog", description="Create a blog post (Requires API Keys + JWT Token)")
# async def create_blog_post(
#     title: str = Form(...),
#     content: str = Form(...),
#     banner_image: UploadFile = File(None),
#     db: Session = Depends(get_db), 
#     current_user = Depends(get_current_user)
# ):

#     """"Create a new blog post with optional banner image (Only authenticated users can create)"""
#     #validate blog data
#     is_valid, msg = validate_blog_data(title, content)
#     if not is_valid:
#         return ErrorResponse(msg, status_code=400)
 
#     # Validate image file if provided
#     if banner_image and banner_image.filename:
#         # Read file content for validation
#         image_content = await banner_image.read()
#         is_valid_image, image_msg = validate_image_file(banner_image.filename, image_content)
#         if not is_valid_image:
#             return ErrorResponse(image_msg, status_code=400)
        
#         # Reset file pointer after validation
#         await banner_image.seek(0)
    
#     # IMPORTANT: AWAIT the async function
#     blog = await create_blog(db, title, content, current_user.id, banner_image if banner_image and banner_image.filename else None)
    
#     return SuccessResponse(
#         message="Blog created successfully", 
#         status_code=status.HTTP_201_CREATED, 
#         data={
#             "blog_id": blog.id, 
#             "title": blog.title, 
#             "slug": blog.slug,
#             "author_id": blog.author_id,
#             "banner_image": blog.image_url if hasattr(blog, "image_url") else blog.banner_image
#         }
#     )


# @router.get("/get_blogs", summary="Get all blogs", description="Retrieve all blog posts (Requires API Keys only)")
# def read_all_blogs(db: Session = Depends(get_db)):
#     """Get all blog posts - Only API keys required"""
#     blogs = get_all_blogs(db)
#     return SuccessResponse(
#         message="Blogs retrieved successfully", 
#         status_code=status.HTTP_200_OK, 
#         data=[
#             {
#                 "blog_id": blog.id, 
#                 "title": blog.title, 
#                 "slug": blog.slug,
#                 "content": blog.content[:200] + "..." if len(blog.content) > 200 else blog.content,
#                 "author_id": blog.author_id,
#                 "banner_image": blog.image_url if hasattr(blog, "image_url") else blog.banner_image
#             } 
#             for blog in blogs
#         ]
#     )


# @router.get("/blog/{blog_id}", summary="Get single blog", description="Get a specific blog by ID (Requires API Keys only)")
# def read_single_blog(blog_id: int, db: Session = Depends(get_db)):
#     """Get a single blog post by ID - Only API keys required"""
#     blog = get_blog_by_id(db, blog_id)
    
#     if not blog:
#         return ErrorResponse(message="Blog not found", status_code=status.HTTP_404_NOT_FOUND)
    
#     return SuccessResponse(
#         message="Blog retrieved successfully", 
#         status_code=status.HTTP_200_OK, 
#         data={
#             "blog_id": blog.id, 
#             "title": blog.title, 
#             "slug": blog.slug,
#             "content": blog.content,
#             "author_id": blog.author_id
#         }
#     )


# @router.put("/update_blog/{blog_id}", summary="Update blog", description="Update a blog post (Requires API Keys + JWT Token)")
# def update_blog_post(
#     blog_id: int, 
#     title: str = Form(...),
#     content: str = Form(...),
#     db: Session = Depends(get_db), 
#     current_user = Depends(get_current_user)
# ):
#     is_valid, msg = validate_blog_data(title, content)
#     if not is_valid:
#         return ErrorResponse(msg, status_code=400)
        
#     """Update a blog post (Only the author can update)"""
#     result = update_blog(db, blog_id, {"title": title, "content": content}, current_user.id)

#     if result is None:
#         return ErrorResponse("Blog not found", status_code=status.HTTP_404_NOT_FOUND)
#     if result == "Unauthorized":
#         return ErrorResponse("Unauthorized - You can only update your own blogs", 
#                            status_code=status.HTTP_403_FORBIDDEN)

#     return SuccessResponse(
#         message="Blog updated successfully", 
#         status_code=status.HTTP_200_OK, 
#         data={
#             "blog_id": result.id, 
#             "title": result.title, 
#             "slug": result.slug,
#             "content": result.content
#         }
#     )


# @router.delete("/delete_blog/{blog_id}", summary="Delete blog", description="Delete a blog post (Requires API Keys + JWT Token)")
# def delete_blog_post(
#     blog_id: int, 
#     db: Session = Depends(get_db), 
#     current_user = Depends(get_current_user)
# ):
#     """Delete a blog post (Only the author can delete)"""
#     result = delete_blog(db, blog_id, current_user.id)

#     if result is None:
#         return ErrorResponse("Blog not found", status_code=status.HTTP_404_NOT_FOUND)
#     if result == "Unauthorized":
#         return ErrorResponse("Unauthorized - You can only delete your own blogs", 
#                            status_code=status.HTTP_403_FORBIDDEN)

#     return SuccessResponse(
#         message="Blog deleted successfully", 
#         status_code=status.HTTP_200_OK
#     )