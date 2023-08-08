from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

import validators
import random

from . import models
from .database import engine, get_db
from . import crud
from . import schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

KEY_LEN = 6


@app.get("/")
def home():
    return RedirectResponse(url="https://www.krll.me", status_code=301)


@app.post("/api/urls", response_model=schemas.ShortenedURL)
def create(url: schemas.URLToShorten, db: Session = Depends(get_db)):
    if not validators.url(url.url):
        raise HTTPException(status_code=400, detail="Invalid URL")
    
    shortened_url = crud.get_shortened_url(db, url.url)
    
    if shortened_url is None:
        string = "abcdefghijklmnopqrstuvwxyz"
        string += string.upper()
        string += "0123456789"
        string = string * KEY_LEN

        key = "".join(random.sample(string, KEY_LEN))

        while not crud.get_original_url(db, key) is None:
            key = "".join(random.sample(string, KEY_LEN))

        shortened_url = crud.shorten_url(db, url.url, key)

        return {
            "key": key,
            "original_url": url.url
        }
    
    return shortened_url


@app.get("/{key}")
def redirect(key: str, db: Session = Depends(get_db)):
    shortened_url = crud.get_original_url(db, key)

    if shortened_url is None:
        raise HTTPException(status_code=404, detail="URL is not found.")
    
    return RedirectResponse(shortened_url.original_url, status_code=301)