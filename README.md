# CNC-Whiteboard Software
Full-stack software that converts digital images and SVGs into optimized G-code for my [CNC-Whiteboard](https://github.com/jeffrey500/CNC-Whiteboard), and plots them directly onto a whiteboard.

<img src="github_media/Screenshot%202026-07-28%20at%2010.36.43%E2%80%AFAM.png" width="49%" alt="title_image"> <img src="github_media/Screenshot%202026-07-28%20at%2010.50.45%E2%80%AFAM.png" width="49%" alt="title_image">

## Key Features

- **Web-based interface:** React-based front-end for uploading, managing, and previewing before plotting
- **Image Processing Pipeline:** Utilizes `OpenCV` to get skeletonized marker traces and a custom Depth First Search algorithm to generate pathing
- **SVG to G-code:** Utilizes `svgpathtools` and sampling to generate paths from non-linear SVG segments.
- **Path Optimization:** Greedy algorithm to optimize pathing
- **Containerized Deployment:** Fully Dockerized microservice architecture built to run headless on a Raspberry Pi.

## Tech Stack

- **Front-End:** React, Tailwind CSS, Nginx
- **Back-End:** Python, FastAPI, PostgreSQL, Uvicorn, OpenCV, svgpathtools
- **Hardware:** Raspberry Pi 3B+, [CNC-Whiteboard](https://github.com/jeffrey500/CNC-Whiteboard)

## System Architecture

- **Front-Container:** static React assets via Nginx
- **API-Container:** Handles file uploads, image-to-G-code processing, SVG-to-G-Code processing, database routing, and serial port streaming
- **Database Container:** PostgreSQL instance containing svg and image filepaths
- **Volume Mounts:** Binds local directories to ensure uploaded files and PostgreSQL databases survive container restarts.
- **Hardware Passthrough:** Maps selected serial port directly into the API container for CNC control

## Deployment
1. Clone this repository
```bash
git clone https://github.com/jeffrey500/CNC-Whiteboard-Software.git
```
2. Configure Network IPs:  
```text 
Open frontend/src/SVGs.jsx and frontend/src/Images.jsx and replace 
192.168.2.179 with your Raspberry Pi's local IP address.

Open backend/main.py and update the CORSMiddleware origins 
list to include your Pi's IP address.  
```
3. Rebuild the website
```bash
cd CNC-Whiteboard-Software
cd frontend
npm run build
```
4. Navigate to the project root
```bash
cd ..
```
5. Launch Containers
```bash
docker compose up -d --build
```
6. Access the webserver at your device's IP address