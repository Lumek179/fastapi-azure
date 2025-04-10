from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app import models, schemas
from app.db import SessionLocal, engine, Base
import random

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency para obtener sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/items", response_model=list[schemas.Item])
def read_items(db: Session = Depends(get_db)):
    return db.query(models.Item).limit(10).all()

@app.post("/seed")
def seed_data(db: Session = Depends(get_db)):
    names = ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf"]
    for _ in range(10):
        name = random.choice(names) + "-" + str(random.randint(100, 999))
        db_item = models.Item(name=name)
        db.add(db_item)
    db.commit()
    return {"message": "Datos dummy insertados correctamente"}
