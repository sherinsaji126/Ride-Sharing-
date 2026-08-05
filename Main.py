
from fastapi import FastAPI
from Database import Base,engine

# Import all models so SQLAlchemy registers them
from Models.User import User
from Models.RefreshToken import RefreshToken


app=FastAPI()

Base.metadata.create_all(bind=engine)