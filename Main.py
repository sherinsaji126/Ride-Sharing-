
# Import the FastAPI class from the FastAPI library.
from fastapi import FastAPI
from Api.Routers import Auth,Users,Add_Trip

from Database import Base,engine,SessionLocal

# Create a FastAPI application instance.
# It simply creates an application object(think of it as : Create an empty FastAPI application) where FastAPI can store:Routes, Middleware, 
# Exception handlers, Startup events, API documentation.

app=FastAPI(title="Ride Sharing Project",version="1.0.0")

# Base.metadata : Contains information about all models.
# create_all() : Checks whether tables exist. If not, SQLAlchemy creates them.
# bind=engine: Tells SQLAlchemy which database connection to use.

app.include_router(Auth.router)
app.include_router(Users.router)
app.include_router(Add_Trip.router)

# Base.metadata.create_all(bind=engine)

def get_db():

    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()










