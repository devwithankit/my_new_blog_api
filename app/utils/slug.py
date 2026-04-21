import re
# def generate_unique_slug(db: Session, title: str):
#     base_slug = generate_slug(title)
#     slug = base_slug
#     counter = 1

#     while db.query(Blog).filter(Blog.slug == slug).first():
#         slug = f"{base_slug}-{counter}"
#         counter += 1

#     return slug
    
def generate_slug(title: str) -> str:
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    return slug.strip('-')