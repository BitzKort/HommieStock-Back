# HommieStock Backend Repository

This repository contains the backend for the final project in the NoSQL databases course. The project uses MongoDB as a non-relational database and a REST API built with FastAPI to deliver a complete inventory management solution.

---

## Project Description

HommieStock is a solution designed to manage the real-time inventory of a retail chain. It provides functionalities for managing products, inventories, orders, suppliers, returns, and reports, all optimized to take full advantage of a NoSQL database like MongoDB.

---

## Prerequisites

Before running the project, ensure you have the following installed:

- Python 3.9 or higher.
- [Pipenv](https://pipenv.pypa.io/en/latest/) for virtual environment management.
- A MongoDB instance (local or cloud, such as [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)) properly configured.

---

## How to Run the Project

Follow these steps to set up and run the backend:

1. Install Pipenv:

   ```bash
   pip install pipenv
   ```
2. Create an venv:

    ```bash
    pipenv shell
    ```
3. Install dependencies

    ```bash
    pipenv install -r requirements.txt
    ```
4. Run de server:

    ```bash
    python -m uvicorn main:app --reload
    ```
5. Open on your browser: http://127.0.0.1:8000      

---
## Important Notes

### MongoDB Connection:
If you encounter issues connecting to MongoDB, make sure that:

1. Your IP address is allowed in your MongoDB Atlas account.
2. The credentials and URI in the configuration file are correct.

### Virtual Environment:

Make sure you are working within the virtual environment created with Pipenv before executing any commands.

---

## Branch Structure
* main: Main branch with the stable version of the project.
* feature/mongodb_structure: Branch with the initial implementation of the MongoDB structure.
