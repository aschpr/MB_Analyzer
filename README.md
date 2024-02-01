# Web Project README

This README.md provides instructions for setting up and running the local development environment for the mb-analyzer with Angular 15 for the frontend, FastAPI for the backend, and a file server.

## Prerequisites

Before you begin, make sure you have the following installed on your machine:

- Node.js (for Angular)
- Angular CLI
- Python (for FastAPI)

## Getting Started

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/aschpr/MB_Analyzer.git
   cd your-web-project
   ```

2. **Frontend Setup:**

   ```bash
   cd mb_frontend
   npm install
   ```

3. **Backend Setup:**

   ```bash
   cd mb_backend
   # If not using pipenv
   pip install -r requirements.txt
   ```

4. **File Server Setup:**

   ```bash
    cd data 

    // Only once
    pip install uploadserver
    python3 -m uploadserver 3334

    // NEW TERMINAL
    python server.py
   ```


6. **Running the Application:**

   - Start the Angular Development Server:

     ```bash
     cd frontend
     ng serve
     ```

     Access the frontend application at `http://localhost:4200`.

   - Start the FastAPI Server:

     ```bash
     cd backend
     uvicorn main:app --reload
     // or
     python3 main.py
     ```

     Access the backend API at `http://localhost:8000`.

6. **Accessing the Application:**

   Open your web browser and navigate to `http://localhost:4200` to access the web application.

## Additional Notes

- **Database Setup:**

The database will run automatically 
