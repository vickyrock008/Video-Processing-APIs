

---

# **Video Processing API Backend**

This project is a complete FastAPI backend application designed for a video editing platform. It provides a robust API for handling video uploads, asynchronous processing (transcoding, trimming, overlays), and database management using PostgreSQL. The entire application is built to be modular, efficient, and easy to test.

---

## **🎥 Features**

This application successfully implements all requirements from the assignment brief:

* **Level 1: Upload & Metadata**: A POST /api/upload endpoint to upload videos and a GET /api/videos endpoint to list their metadata from the database.  
* **Level 2: Trimming**: A POST /api/trim endpoint that accepts a video ID and timestamps, returning a trimmed video file for direct download.  
* **Level 3: Overlays & Watermarking**:  
  * POST /api/overlay/text: Adds large, centered text to a video for a specified duration.  
  * POST /api/overlay/watermark: Adds an image watermark to the bottom-right corner of a video.  
* **Level 4: Async Processing & Status Checks**:  
  * Uses FastAPI's built-in BackgroundTasks for non-blocking, asynchronous video transcoding upon upload.  
  * Implements a robust status check system ("processing" vs. "complete") to prevent users from accessing files before they are ready.  
* **Level 5: Multiple Output Qualities**:  
  * Automatically transcodes uploaded videos into **1080p, 720p, and 480p** versions.  
  * A GET /api/download/{video\_id} endpoint allows users to download any specific quality version of the processed video.

---

## **🛠️ Setup and Installation**

### **Prerequisites**

Before you begin, ensure you have the following installed on your system:

* Python 3.10+  
* PostgreSQL  
* FFmpeg

### **Step 1: Clone the Repository**

First, clone your repository to your local machine.

Bash

git clone \<your-github-repo-url\>  
cd backend

### **Step 2: Set Up the Python Environment**

Create and activate a Python virtual environment to manage project dependencies.

Bash

\# For Windows  
python \-m venv venv  
venv\\Scripts\\activate

\# For macOS/Linux  
python3 \-m venv venv  
source venv/bin/activate

Install the required Python packages using the requirements.txt file.

Bash

pip install \-r requirements.txt

*(Note: To generate the requirements.txt file, run pip freeze \> requirements.txt in your activated virtual environment.)*

### **Step 3: Configure the Database**

1. Ensure your PostgreSQL server is running. Create a new database for this project (e.g., video\_db).  
2. Open the **alembic.ini** file and update the sqlalchemy.url with your database username, password, and database name.  
   Ini, TOML  
   sqlalchemy.url \= postgresql://YOUR\_USER:YOUR\_PASSWORD@localhost/video\_db

3. Open the **app/models/models.py** file and update the SQLALCHEMY\_DATABASE\_URL to match the one in alembic.ini.

### **Step 4: Run Database Migrations**

With the database configured, apply the schema using Alembic. This will create all the necessary tables.

Bash

alembic upgrade head

### **Step 5: Add Watermark Asset**

Download the logo.png file from the assets link provided in the assignment and place it in the root of the **backend** folder.

---

## **🚀 How to Run the Application**

Once the setup is complete, you can run the FastAPI server using Uvicorn.

Bash

uvicorn app.main:app \--reload

The server will start, and the API will be available at http://127.0.0.1:8000.

---

## **🧪 How to Test**

This application comes with interactive API documentation (Swagger UI) for easy testing.

1. With the server running, navigate to **http://127.0.0.1:8000/docs** in your web browser.  
2. You will see a complete, interactive list of all available API endpoints.  
3. You can expand any endpoint, click "Try it out," fill in the parameters, and click "Execute" to test the full functionality of the application live in your browser.