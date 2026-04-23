from pydantic import BaseModel

class BlogCreateSchema(BaseModel):
    title: str
    content: str
    banner_image: optional[str] = None


class BlogUpdateSchema (BaseModel):
    title: str
    content: str
    banner_image: optional[str] = None


class BlogResponse(BaseModel):
    id: int
    title: str
    content: str
    slug: str
    banner_image: optional[str] = None 
    created_at: optional[str] = None
    updated_at: optional[str] = None

    class Config:
        from_attributes = True