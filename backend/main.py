import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

import psycopg2
import uvicorn
from fastapi import FastAPI, HTTPException, File, UploadFile
from starlette import status

from backend.db import image_insert, get_images, get_image
from backend.model import Image
from src.image_processing import generate_gcode_from_image
from src.svg_processing import generate_gcode_from_svg

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

    # save the uploaded file to the "data/image_inputs" directory
    filename = file.filename
    file_path = Path(__file__).parent / "data" / "image_inputs" / filename

    # gcode file name
    gcode_filename = file_path.with_suffix(".gcode")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # convert image to gcode and get timestamp
        generate_gcode_from_image(gcode_filename)
        current_time = datetime.now(timezone.utc)

        # insert image into database
        image_insert(conn, filename, current_time, str(file_path), gcode_filename)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# get all images in database
@app.get("/image/", response_model=list[Image])
def list_images():
    try:
        return get_images(conn)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# get a specific image from database
@app.get("/image/{id}", response_model=Image, status_code=200)
def list_image(id: int):
    try:
        return get_image(conn, id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# delete a specific image from database
@app.delete("/image/{id}", status_code=204)
def delete_image(id: int):
    try:
        delete_image(conn, id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# upload svg to database
@app.post("/svg/", status_code=201)
async def create_svg(file: Annotated[UploadFile, File()]):
    # save the uploaded file to the "data/svg_inputs" directory
    filename = file.filename
    file_path = Path(__file__).parent / "data" / "svg_inputs" / filename

    # gcode file name
    gcode_filename = file_path.with_suffix(".gcode")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # convert svg to gcode and get timestamp
        generate_gcode_from_svg(gcode_filename)
        current_time = datetime.now(timezone.utc)

        # insert image into database
        image_insert(conn, filename, current_time, str(file_path), gcode_filename)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# get all svgs in database

# get a specific svg from database

if __name__ == "__main__":
    # Specify the port keyword argument here
    uvicorn.run("main:app", host="0.0.0.0", port=5050, reload=True)

    # DB close
    conn.close()

#Need another endpoint for starting plotting

