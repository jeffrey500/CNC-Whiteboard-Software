import os
import shutil

import uvicorn
from typing import Annotated
from fastapi import FastAPI, HTTPException, File, Form, UploadFile
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# client -> post -> image -> stored

@app.post("/images/", status_code=201)
async def create_image(
    file: Annotated[UploadFile, File()]
):
    filename = file.filename
    content_type = file.content_type

    file_path = os.path.join("./temp", filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    print("created")


# client -> get -> all images stored

if __name__ == "__main__":
    # Specify the port keyword argument here
    uvicorn.run("main:app", host="0.0.0.0", port=5050, reload=True)