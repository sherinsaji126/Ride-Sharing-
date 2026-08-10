
# Import the FastAPI class from the FastAPI library.
from fastapi import FastAPI
from Database import Base,engine

# Import all models so SQLAlchemy registers them

# When Python imports this file:
# 1. The class is loaded into memory.
# 2. SQLAlchemy registers the table definition.
# 3. users table information is added to Base.metadata.

from Models.User import User
from Models.RefreshToken import RefreshToken


# Create a FastAPI application instance.
# It simply creates an application object(think of it as : Create an empty FastAPI application) where FastAPI can store:Routes, Middleware, 
# Exception handlers, Startup events, API documentation.

app=FastAPI()

# Base.metadata : Contains information about all models.
# create_all() : Checks whether tables exist. If not, SQLAlchemy creates them.
# bind=engine: Tells SQLAlchemy which database connection to use.
Base.metadata.create_all(bind=engine)