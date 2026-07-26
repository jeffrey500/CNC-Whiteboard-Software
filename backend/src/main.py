import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

import numpy as np
import psycopg2
import time
import uvicorn
from fastapi import FastAPI, HTTPException, File, UploadFile
from starlette import status

import src.db as db
from src.model import Image, SVG, SVGEditRequest, PlotRequest
from src.image_processing import generate_gcode_from_image
from src.plot import send_gcode
from src.svg_processing import generate_gcode_from_svg
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.2.179:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


while True:
    try:
        conn = psycopg2.connect(
            host="db", # Uses the Docker Compose service name
            database="postgres",
            user="postgres",
            password="mysecretpassword",
            port="5432"
        )
        print("Successfully connected to the database!")
        break
    except psycopg2.OperationalError:
        print("Waiting for database to start...")
        time.sleep(2)


# expose static files
app.mount("/static", StaticFiles(directory="backend/data"), name="static")


# upload image to database
@app.post("/image/", status_code=201)
async def create_image(file: Annotated[UploadFile, File()]):
    # save the uploaded file to the "data/image_inputs" directory
    filename = file.filename
    file_path = Path(__file__).parent.parent / "data" / "image_inputs" / filename

    # gcode file name
    gcode_filename = (Path(__file__).parent.parent / "data" / "image_gcode_output" / filename).with_suffix(".gcode")

    # render file name
    render = (Path(__file__).parent.parent / "data" / "image_render" / filename).with_suffix(".png")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # convert image to gcode and get timestamp
        generate_gcode_from_image(file_name=filename, output_path_name=file_path.stem)
        current_time = datetime.now(timezone.utc)

        # insert image into database
        db.image_insert(conn, filename, current_time, str(file_path), str(gcode_filename), str(render))

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# get all images in database
@app.get("/image/", response_model=list[Image])
def get_images():
    try:
        return db.get_images(conn)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# get a specific image from database
@app.get("/image/{id}", response_model=Image, status_code=200)
def get_image(id: int):
    try:
        return db.get_image(conn, id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# delete a specific image from database
@app.delete("/image/{id}", status_code=204)
def delete_image(id: int):
    try:
        # delete image entry from database
        file_paths = db.delete_image(conn, id)

        # delete image and gcode files
        for file_path in file_paths:
            Path(file_path).unlink(missing_ok=True)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# plot image gcode
@app.post("/image/plot/{id}", status_code=200)
def plot_image(id: int, params: PlotRequest):
    try:
        img = db.get_image(conn, id)
        file_name = Path(img.name)
        file_path =  Path(__file__).parent.parent / "data" / "image_gcode_output" / f"{file_name.stem}.gcode"

        send_gcode(str(file_path), params.port)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# upload svg to database
@app.post("/svg/", status_code=201)
async def create_svg(file: Annotated[UploadFile, File()]):
    # save the uploaded file to the "data/image_inputs" directory
    filename = file.filename
    file_path = Path(__file__).parent.parent / "data" / "svg_inputs" / filename

    # gcode file name
    gcode_filename = (Path(__file__).parent.parent / "data" / "svg_gcode_output" / filename).with_suffix(".gcode")

    # render file name
    render = (Path(__file__).parent.parent / "data" / "svg_render" / filename).with_suffix(".png")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # convert svg to gcode and get timestamp
        generate_gcode_from_svg(file_name=filename, output_path_name=file_path.stem)
        current_time = datetime.now(timezone.utc)

        # insert svg into database
        db.svg_insert(conn, filename, current_time, str(file_path), str(gcode_filename), str(render))

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# get all svgs in database
@app.get("/svg/", response_model=list[SVG])
def get_svgs():
    try:
        return db.get_svgs(conn)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# get a specific svg from database
@app.get("/svg/{id}", response_model=SVG, status_code=200)
def get_svg(id: int):
    try:
        return db.get_svg(conn, id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# delete a specific svg from database
@app.delete("/svg/{id}", status_code=204)
def delete_svg(id: int):
    try:
        # delete svg entry from database
        file_paths = db.delete_svg(conn, id)

        # delete svg and gcode files
        for file_path in file_paths:
            Path(file_path).unlink(missing_ok=True)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

# re-render a specific svg from database
@app.put("/svg/{id}", status_code=201)
def edit_svg(id: int, params: SVGEditRequest):
    try:
        # edit svg entry from database
        matrix = np.array([[params.x_scale, 0, params.x_translate], [0, params.y_scale, params.y_translate], [0, 0, 1]])

        svg = db.get_svg(conn, id)
        file_name = Path(svg.name)

        generate_gcode_from_svg(file_name=svg.name,output_path_name=file_name.stem,matrix=matrix)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# plot svg gcode
@app.post("/svg/plot/{id}", status_code=200)
def plot_svg(id: int, params: PlotRequest):
    try:
        svg = db.get_svg(conn, id)
        file_name = Path(svg.name)
        file_path =  Path(__file__).parent.parent / "data" / "svg_gcode_output" / f"{file_name.stem}.gcode"

        send_gcode(str(file_path), params.port)

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