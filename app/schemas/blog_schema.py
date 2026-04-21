from pydantic import BaseModel

class BlogCreateSchema(BaseModel):
    title: str
    content: str


class BlogUpdateSchema (BaseModel):
    title: str
    content: str


class BlogResponse(BaseModel):
    id: int
    title: str
    content: str
    slug: str

    class Config:
        from_attributes = True