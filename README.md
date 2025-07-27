# 🚙 Uway (Backend)
------------------

<p align="center">
    <img src="./public/Uguee.png" alt="Uway Logo" width="300">
</p>

## Description

It is an online platform that allows educational institutions to manage student transportation
on and off campus through the combined use geolocation and QR codes. In addition, ‬‭real-time
tracking of the location of associated vehicles, facilitating the planning of their movements on 
and off campus.
Provides:

- Real-time location streaming over WebSocket  
- Temporary buffering of locations in Redis  
- Batch persistence to PostgreSQL/PostGIS via Celery  
- RESTful endpoints for trips, drivers and passengers  
- QR-based boarding validation  
- Automatic detection of route deviations and incidents  

## 🗝️ Key Features

- 🔒 **Authentication & Authorization** using JWT
- 📝 **Trip management**: create, list, start, complete  
- 👥 **Passenger enrollment** and QR boarding validation  
- 🔁 **WebSockets** for live vehicle location updates  
- 🟥 **Redis buffer** for temporary location storage and avoid overloading the database
- 🥬 **Celery tasks** for executing background jobs like location persistence and heavy processing
- 🌍 **Deviation & incident analysis** with GeoDjango/PostGIS
- 🪣 **AWS S3** integration for storing users documents and college logos


## Tech Stack

- Python 
- Django + Django REST Framework
- PostgreSQL + PostGIS 
- Django Channels for WebSockets
- Celery 
- Redis  
- Docker & Docker Compose


## How to Run
1. Clone and enter the repository:
   ```bash
   git clone https://github.com/Uway-Univalle/Uway-Backend.git
   cd Uway-Backend
   ```
2. Copy the example environment file to create your own `.env` file (Make sure to fill in the required variables):
   ```bash
   cp .env.example .env
   ```
3. Convert line endings to Unix format (if on Windows):
   ```bash
   dos2unix wait-for-it.sh start.sh
   ```
4. Build and start all containers:
   ```bash
   docker compose up --build
   ```
5. Verify the API is running by visiting: http://localhost:8000/api/docs/swagger/#/