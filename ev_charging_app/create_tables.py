# This will create all the tables defined in the models
from app import models, database

models.Base.metadata.create_all(bind=database.engine)
