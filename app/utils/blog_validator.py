def validate_blog_data(title: str, content: str):

    """Validate blog title and content"""
        #title validation
    if not title or not title.strip():
        return False, "Blog title is required"
    if len(title) < 5:
        return False, "Blog title must be at least 5 characters long"
    if len(title) > 200:
        return False, "Blog title must be less than 200 characters"
        #content validation
    if not content or not content.strip(): 
        return False, "Blog content is required"
    
    if len(content) < 20:
        return False, "Blog content must be at least 20 characters long"

    if len(content) > 5000:
        return False, "Blog content must be less than 5000 characters"

    return True, "Valid blog data"