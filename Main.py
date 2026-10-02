
# Import the FastAPI class from the FastAPI library.
from fastapi import FastAPI

from Database import Base,engine,SessionLocal

# Create a FastAPI application instance.
# It simply creates an application object(think of it as : Create an empty FastAPI application) where FastAPI can store:Routes, Middleware, 
# Exception handlers, Startup events, API documentation.

app=FastAPI()

# Base.metadata : Contains information about all models.
# create_all() : Checks whether tables exist. If not, SQLAlchemy creates them.
# bind=engine: Tells SQLAlchemy which database connection to use.


Base.metadata.create_all(bind=engine)

def get_db():

    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()










