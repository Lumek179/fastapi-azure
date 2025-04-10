from fastapi import FastAPI, UploadFile, File, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app import models, schemas
from app.db import SessionLocal, engine, Base
import pandas as pd
from io import StringIO
from datetime import datetime
import random

# Crear las tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency para obtener una sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Mapeo explícito de nombres de tabla a modelos
model_map = {
    "departments": models.Department,
    "jobs": models.Job,
    "hired_employees": models.HiredEmployee,
}

@app.post("/upload-csv/{table_name}")
def upload_csv(table_name: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    model = model_map.get(table_name)
    if model is None:
        return {"error": "Invalid table name"}

    contents = file.file.read().decode("utf-8")
    df = pd.read_csv(StringIO(contents), header=None)

    default_counts = {}

    if table_name == "departments":
        df.columns = ["id", "department"]
        df["id"] = df["id"].astype(int)
        default_counts["department"] = int(df["department"].isna().sum())
        df["department"] = df["department"].fillna("Unknown Department")

    elif table_name == "jobs":
        df.columns = ["id", "job"]
        df["id"] = df["id"].astype(int)
        default_counts["job"] = int(df["job"].isna().sum())
        df["job"] = df["job"].fillna("Unknown Job")

    elif table_name == "hired_employees":
        df.columns = ["id", "name", "datetime", "department_id", "job_id"]

        default_counts["name"] = int(df["name"].isna().sum())
        default_counts["department_id"] = int(df["department_id"].isna().sum())
        default_counts["job_id"] = int(df["job_id"].isna().sum())

        df["name"] = df["name"].fillna("Unknown")
        df["department_id"] = df["department_id"].fillna(-1).astype(int)
        df["job_id"] = df["job_id"].fillna(-1).astype(int)
        df["id"] = df["id"].astype(int)

        # Limpieza y conversión segura de fechas
        df["datetime"] = df["datetime"].astype(str).str.strip().str.replace(r"[^\x00-\x7F]+", "", regex=True)
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce", utc=True)
        df["datetime"] = df["datetime"].dt.tz_convert(None)
        default_counts["datetime"] = int(df["datetime"].isna().sum())
        df["datetime"] = df["datetime"].fillna(pd.Timestamp("2000-01-01"))

        # Fallback -1 en claves foráneas si no existen
        if not db.query(models.Department).filter_by(id=-1).first():
            db.add(models.Department(id=-1, department="Unknown Department"))
        if not db.query(models.Job).filter_by(id=-1).first():
            db.add(models.Job(id=-1, job="Unknown Job"))
        db.commit()

    # Conversión a lista de registros
    records = df.to_dict(orient="records")

    # Inserción por lotes
    BATCH_SIZE = 1000
    for i in range(0, len(records), BATCH_SIZE):
        db.bulk_insert_mappings(model, records[i:i + BATCH_SIZE])

    db.commit()

    return {
        "message": f"{len(records)} records inserted into {table_name}",
        "defaults_applied": default_counts
    }

@app.post("/seed")
def seed_data(db: Session = Depends(get_db)):
    # Carga dummy de datos si se quiere testear sin CSV
    names = ["Alice", "Bob", "Carol", "David", "Eva", "Frank"]
    for _ in range(10):
        db.add(models.Department(department=f"Dept-{random.randint(1,10)}"))
        db.add(models.Job(job=f"Job-{random.randint(1,10)}"))
    db.commit()

    depts = db.query(models.Department).all()
    jobs = db.query(models.Job).all()

    for _ in range(50):
        employee = models.HiredEmployee(
            name=random.choice(names),
            datetime=datetime.strptime(f"2021-{random.randint(1,12)}-{random.randint(1,28)}", "%Y-%m-%d"),
            department_id=random.choice(depts).id,
            job_id=random.choice(jobs).id
        )
        db.add(employee)
    db.commit()
    return {"message": "Seeded dummy data"}

@app.get("/report/hirings-per-quarter")
def hirings_per_quarter(db: Session = Depends(get_db)):
    results = db.query(
        models.Department.department,
        models.Job.job,
        func.sum(func.case([(extract("quarter", models.HiredEmployee.datetime) == 1, 1)], else_=0)).label("Q1"),
        func.sum(func.case([(extract("quarter", models.HiredEmployee.datetime) == 2, 1)], else_=0)).label("Q2"),
        func.sum(func.case([(extract("quarter", models.HiredEmployee.datetime) == 3, 1)], else_=0)).label("Q3"),
        func.sum(func.case([(extract("quarter", models.HiredEmployee.datetime) == 4, 1)], else_=0)).label("Q4"),
    ).join(models.Department, models.HiredEmployee.department_id == models.Department.id
    ).join(models.Job, models.HiredEmployee.job_id == models.Job.id
    ).filter(extract("year", models.HiredEmployee.datetime) == 2021
    ).group_by(models.Department.department, models.Job.job
    ).order_by(models.Department.department, models.Job.job).all()

    return [dict(r._asdict()) for r in results]

@app.get("/report/above-average-hirings")
def above_average_hirings(db: Session = Depends(get_db)):
    subquery = db.query(
        models.HiredEmployee.department_id,
        func.count(models.HiredEmployee.id).label("hired")
    ).filter(
        extract("year", models.HiredEmployee.datetime) == 2021
    ).group_by(models.HiredEmployee.department_id).subquery()

    avg = db.query(func.avg(subquery.c.hired)).scalar()

    result = db.query(
        models.Department.id,
        models.Department.department,
        subquery.c.hired
    ).join(subquery, models.Department.id == subquery.c.department_id
    ).filter(subquery.c.hired > avg
    ).order_by(subquery.c.hired.desc()).all()

    return [dict(r._asdict()) for r in result]
