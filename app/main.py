from fastapi import FastAPI
import models, database, routes


models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
app.include_router(routes.router)
