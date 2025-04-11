# FastAPI - Azure SQL API Project (English Version)

This project implements a REST API using **FastAPI**, connected to an **Azure SQL** database. Its main goal is to streamline the upload, validation, storage, and querying of employee hiring data across departments and jobs.

---

## 🔍 Project Structure

```
fastapi-azure/
├── app/
│   ├── main.py               # Main file with all endpoints
│   ├── db.py                 # DB connection setup
│   ├── models.py             # ORM models with SQLAlchemy
│   ├── schemas.py            # Pydantic schemas (optional/future use)
│   ├── db_utils.py           # Utility functions for chunked reading
│   └── main_deprecated.py    # Old version of main (optional)
```

---

## 🚀 Key Features

- Upload `.csv` files to populate `departments`, `jobs`, and `hired_employees` tables.
- Deduplication using pandas merge vs database content.
- Automatic handling of nulls, date conversion, and foreign keys.
- Efficient memory usage with chunked loading (`chunksize=1000`).
- Reporting endpoints to analyze hiring metrics.

---

## 🛠️ Run the App with Docker

To **start the app** using Docker Compose:
```bash
docker compose -f docker-compose.yml up --build
```

To **stop the app**:
```bash
docker compose -f docker-compose.yml down
```

---

## 🔗 Main Endpoints

### 1. Upload CSV files (validated and deduplicated)
Endpoint:
```http
POST /upload-csv-dfa-sql/{table_name}
```
Allowed `table_name` values:
- `hired_employees`
- `departments`
- `jobs`

#### 🚗 CURL examples
```bash
curl -X POST http://localhost:8000/upload-csv-dfa-sql/hired_employees -F "file=@hired_employees.csv"
curl -X POST http://localhost:8000/upload-csv-dfa-sql/departments -F "file=@departments.csv"
curl -X POST http://localhost:8000/upload-csv-dfa-sql/jobs -F "file=@jobs.csv"
```

#### 📏 Postman instructions
- Method: `POST`
- URL: `http://localhost:8000/upload-csv-dfa-sql/{table_name}`
- Body: `form-data`
  - Key: `file`
  - Type: `File`
  - Value: Select your `.csv` file from disk

---

### 2. Quarterly hiring by job and department (2021)
- **Description**: Total employees hired for each job and department in 2021, divided by quarter. Sorted alphabetically by department and job.
- **Endpoint**:
```http
GET http://0.0.0.0:8000/report/hirings-per-quarter
```

### 3. Departments above average hiring in 2021
- **Description**: Departments with more hires than the 2021 average. Ordered descending by total hires.
- **Endpoint**:
```http
GET http://0.0.0.0:8000/report/above-average-hirings-2021
```

### 4. Departments above 2021 average (all time)
- **Description**: Departments whose total hiring (all time) exceeds the average of all departments in 2021.
- **Endpoint**:
```http
GET http://0.0.0.0:8000/report/above-average-hirings-all
```

---

## 📊 Utility Functions (`app/db_utils.py`)

```python
load_dataframe_chunks(model, columns, db_bind, chunksize=1000)
```
Loads a table in memory-safe chunks using SQLAlchemy and pandas. Returns a full combined DataFrame.

---

## 🛡️ Validation Rules

- Skip duplicates using pandas `merge()`
- Convert timezone-aware datetimes to naive for proper comparison
- Fill nulls with defaults (e.g., "Unknown", `-1`)
- Exclude dates before `1753-01-01` (SQL Server valid range)

