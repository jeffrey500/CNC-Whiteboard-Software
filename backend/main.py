import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

import psycopg2
import uvicorn
from fastapi import FastAPI, HTTPException, File, UploadFile
from starlette import status

from backend.db import insert, selectAll, select
from backend.model import Image

app = FastAPI()

# DB connection
conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="mysecretpassword",
    port="5432"
)


# upload image to database
@app.post("/image/", status_code=201)
async def create_image(file: Annotated[UploadFile, File()]):
    filename = file.filename
    file_path = Path(__file__).parent / "data" / "image_inputs" / filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        current_time = datetime.now(timezone.utc)
        insert(conn, filename, current_time, str(file_path))

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# get all images in database
@app.get("/image/", response_model=list[Image])
def list_all():
    try:
        return selectAll(conn)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# get a specific image from database
@app.get("/image/{id}", response_model=Image, status_code=200)
def list(id: int):
    try:
        return select(conn, id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


if __name__ == "__main__":
    # Specify the port keyword argument here
    uvicorn.run("main:app", host="0.0.0.0", port=5050, reload=True)

    # DB close
    conn.close()
