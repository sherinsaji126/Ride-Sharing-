from fastapi import FastAPI
from Database import engine,Base

app=FastAPI()

Base.metadata.create_all(bind=engine)