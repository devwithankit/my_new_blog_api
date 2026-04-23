from app.models.blog_model import Blog
from sqlalchemy.orm import Session
from app.utils.slug import generate_slug
from app.utils.image_utils import process_and_save_image, delete_image, get_image_url
from typing import Optional


async def create_blog(db: Session, title: str, content: str, author_id: int, image_file=None) -> Optional[Blog]:
    """Create a new blog post with optional banner image"""
    
    # Generate slug
    slug = generate_slug(title)
    
    # Check if slug already exists
    existing_blog = db.query(Blog).filter(Blog.slug == slug).first()
    if existing_blog:
        slug = f"{slug}-{author_id}-{db.query(Blog).count() + 1}"
    
    # Create blog object
    blog = Blog(
        title=title,
        content=content,
        slug=slug,
        author_id=author_id
    )
    
    # Add to database first to get blog ID
    db.add(blog)
    db.commit()
    db.refresh(blog)

    # Handle banner image if provided
    if image_file and image_file.filename:  # Check if file actually exists
        try:
            # Read image content
            if hasattr(image_file, "read"):
                image_content = await image_file.read()
            else:
                image_content = image_file.read()
            
            # Process and save image
            image_path = process_and_save_image(image_content, image_file.filename, blog.id)
            
            if image_path:
                blog.banner_image = image_path
                db.commit()
                db.refresh(blog)
            
        except Exception as e:
            print(f"Error processing image: {e}")
    
    # Add image URL attribute for response
    blog.image_url = get_image_url(blog.banner_image)
    return blog


def get_all_blogs(db: Session):
    """Get all blogs with image URLs"""
    blogs = db.query(Blog).all()
    
    # Add image URLs to response
    for blog in blogs:
        blog.image_url = get_image_url(blog.banner_image)
    
    return blogs


def get_blog_by_id(db: Session, blog_id: int):
    """Get single blog by ID with image URL"""
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    
    if blog:
        blog.image_url = get_image_url(blog.banner_image)
    
    return blog


async def update_blog(db: Session, blog_id: int, title: str, content: str, author_id: int, image_file=None):
    """Update a blog post with optional image"""
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    
    if not blog:
        return None
    
    # Check authorization
    if blog.author_id != author_id:
        return "Unauthorized"
    
    # Update fields
    blog.title = title
    blog.content = content
    blog.slug = generate_slug(title)
    
    # Handle image update
    if image_file and image_file.filename:
        try:
            # Delete old image if exists
            if blog.banner_image:
                delete_image(blog.banner_image)
            
            # Read and upload new image
            if hasattr(image_file, "read"):
                image_content = await image_file.read()
            else:
                image_content = image_file.read()
            
            image_path = process_and_save_image(image_content, image_file.filename, blog.id)
            if image_path:
                blog.banner_image = image_path
                
        except Exception as e:
            print(f"Error updating image: {e}")
    
    db.commit()
    db.refresh(blog)
    blog.image_url = get_image_url(blog.banner_image)
    
    return blog


def delete_blog(db: Session, blog_id: int, author_id: int):
    """Delete a blog post and its image"""
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    
    if not blog:
        return None
    
    # Check authorization
    if blog.author_id != author_id:
        return "Unauthorized"
    
    # Delete associated image
    if blog.banner_image:
        delete_image(blog.banner_image)
    
    db.delete(blog)
    db.commit()
    return True
# from app.models.blog_model import Blog
# from sqlalchemy.orm import Session
# from app.utils.slug import generate_slug

# from app.utils.blog_validator import validate_blog_data
# from app.utils.image_utils import process_and_save_image, get_image_url
# from typing import Optional
# from sqlalchemy.orm import Session

# async def create_blog(db: Session, title: str, content: str, author_id: int, image_file=None)->Optional[Blog]:
#     """Create a new blog post with optional banner image"""
#     #generate slug
#     slug = generate_slug(title)
#     # Check if slug already exists
#     existing_blog = db.query(Blog).filter(Blog.slug == slug).first()
#     if existing_blog:
#         slug = f"{slug}-{author_id}-{db.query(Blog).count() + 1}"
    
#     blog = Blog(
#         title=title,
#         content=content,
#         slug=slug,
#         author_id=author_id
#     )
    
#     db.add(blog)
#     db.commit()
#     db.refresh(blog)

#     # Handle banner image if provided
#     if image_file:
#         try: 
#             if hasattr(image_file, "read"):
#                 image_content = await image_file.read()
#             else:
#                 image_content = image_file.read()
 
#             image_path = process_and_save_image(image_content, image_file.filename, blog.id)
           
#             if image_path:
#                 blog.banner_image = image_path
#                 db.commit()
#                 db.refresh(blog)
            
#         except Exception as e:
#             print(f"Error processing image: {e}")
#     #add image url attribute for response
#     blog.image_url = get_image_url(blog.banner_image)
#     return blog


# def get_all_blogs(db: Session):
#     """Get all blogs with image URLs"""

#     blogs = db.query(Blog).all()
#     for blog in blogs:
#         blog.banner_image = get_image_url(blog.banner_image)

#     return blogs

# def get_blog_by_id(db: Session, blog_id: int):
#     """Get single blog by ID"""

#     return db.query(Blog).filter(Blog.id == blog_id).first()


# def update_blog(db: Session, blog_id: int, data: dict, author_id: int):
#     """Update a blog post (author only)"""
#     blog = db.query(Blog).filter(Blog.id == blog_id).first()
    
#     if not blog:
#         return None
    
#     # Check authorization
#     if blog.author_id != author_id:
#         return "Unauthorized"
    
#     # Update fields
#     blog.title = data.title
#     blog.content = data.content
#     blog.slug = generate_slug(data.title)
    
#     db.commit()
#     db.refresh(blog)
#     return blog


# def delete_blog(db: Session, blog_id: int, author_id: int):
#     """Delete a blog post (author only)"""
#     blog = db.query(Blog).filter(Blog.id == blog_id).first()
    
#     if not blog:
#         return None
    
#     # Check authorization
#     if blog.author_id != author_id:
#         return "Unauthorized"
    
#     db.delete(blog)
#     db.commit()
#     return True