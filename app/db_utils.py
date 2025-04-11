import pandas as pd
from sqlalchemy import select
from sqlalchemy.dialects import mssql

def load_dataframe_chunks(model, columns: list, db_bind, chunksize: int = 1000):
    """
    Carga registros en chunks desde un modelo SQLAlchemy, usando columnas específicas.

    Parámetros:
    - model: Modelo de SQLAlchemy (ej. models.HiredEmployee)
    - columns: Lista de columnas a seleccionar (ej. [model.name, model.datetime])
    - db_bind: Objeto db.bind desde FastAPI
    - chunksize: Tamaño de bloques (default 1000)

    Retorna:
    - DataFrame combinado con todos los resultados
    """
    stmt = select(*columns)
    compiled = stmt.compile(dialect=mssql.dialect(), compile_kwargs={"literal_binds": True})
    query = str(compiled)

    chunks = pd.read_sql_query(query, db_bind, chunksize=chunksize)
    return pd.concat(chunks, ignore_index=True)
