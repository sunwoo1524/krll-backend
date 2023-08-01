from pydantic import BaseModel


class ShortenedURL(BaseModel):
    key: str
    original_url: str


class URLToShorten(BaseModel):
    url: str