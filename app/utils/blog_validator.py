def validate_blog_data(title: str, content: str):
    if not title or len(title.strip()) < 3:
        return False, "Title must be at least 3 characters"

    if len(title) > 150:
        return False, "Title too long (max 150 characters)"

    if not content or len(content.strip()) < 10:
        return False, "Content must be at least 10 characters"

    if len(content) > 5000:
        return False, "Content too long (max 5000 characters)"

    return True, ""