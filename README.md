To Start the Local Testing
docker compose -f docker-compose.yml up -d

To Stop the Local Testing (Ctrl+C)
docker compose -f docker-compose.yml down

To Test the creation of records:
http://localhost:8000/seed POST

To Get the Records of a db via API
http://localhost:8000/items GET



Resumen rápido para Postman

Subir departments.csv
Opc1:
POST form-data
http://localhost:8000/upload-csv/departments
Opc2:
curl -X POST http://localhost:8000/upload-csv/departments \
  -F "file=@departments.csv"



Subir jobs.csv
Opc1:
POST form-data
http://localhost:8000/upload-csv/jobs
Opc2:
curl -X POST http://localhost:8000/upload-csv/jobs \
  -F "file=@jobs.csv"


Subir hired_employees.csv
Opc1:
POST form-data
http://localhost:8000/upload-csv/hired_employees
Opc2:
curl -X POST http://localhost:8000/upload-csv/hired_employees \
  -F "file=@hired_employees.csv"



Reporte contrataciones por trimestre
Opc1:
GET
http://localhost:8000/report/hirings-per-quarter
Opc2:
curl http://localhost:8000/report/hirings-per-quarter



Reporte departamentos sobre media
Opc1:
GET
http://localhost:8000/report/above-average-hirings
Opc2:
curl http://localhost:8000/report/above-average-hirings