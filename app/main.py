from fastapi import FastAPI
from . import models, database, routes
from fastapi.middleware.cors import CORSMiddleware


models.Base.metadata.create_all(bind=database.engine)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "https://tryoffset.onrender.com"
]

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(routes.router)
