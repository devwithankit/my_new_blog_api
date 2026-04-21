from app.models.blog_model import Blog
from sqlalchemy.orm import Session
from app.utils.slug import generate_slug


def create_blog(db: Session, data, author_id: int):
    """Create a new blog post"""
    slug = generate_slug(data.title)
    
    # Check if slug already exists
    existing_blog = db.query(Blog).filter(Blog.slug == slug).first()
    if existing_blog:
        slug = f"{slug}-{author_id}"
    
    blog = Blog(
        title=data.title,
        content=data.content,
        slug=slug,
        author_id=author_id
    )
    
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog


def get_all_blogs(db: Session):
    """Get all blogs with author info"""
    return db.query(Blog).all()


def get_blog_by_id(db: Session, blog_id: int):
    """Get single blog by ID"""

    return db.query(Blog).filter(Blog.id == blog_id).first()


def update_blog(db: Session, blog_id: int, data, author_id: int):
    """Update a blog post (author only)"""
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    
    if not blog:
        return None
    
    # Check authorization
    if blog.author_id != author_id:
        return "Unauthorized"
    
    # Update fields
    blog.title = data.title
    blog.content = data.content
    blog.slug = generate_slug(data.title)
    
    db.commit()
    db.refresh(blog)
    return blog


def delete_blog(db: Session, blog_id: int, author_id: int):
    """Delete a blog post (author only)"""
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    
    if not blog:
        return None
    
    # Check authorization
    if blog.author_id != author_id:
        return "Unauthorized"
    
    db.delete(blog)
    db.commit()
    return True