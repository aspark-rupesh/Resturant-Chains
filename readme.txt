Setup steps:

1) Clone the repo

2) cd to the repository's directory

3) Create and activate a virtual environment.
    -> python3 -m venv 
    -> source venv/bin/activate  (for ubuntu)

4) Install dependencies.
    -> pip install -r requirements.txt

5) Ensure the mongodb server is running on the system. (mongodb://localhost:27017)

6) Copy the json files (one.json, two.json and three.json) on this working directory as the readme.txt file.

7) load the data files and populate the database using th load_data.py script
    -> python3 load_data.py

8) Start the fastapi server on a port 8000.
    -> uvicorn main:app --port 8000 --host 0.0.0.0 --reload 
    

9)Open the index.txt file on a web browser for the user interface to search for products.
    -> Product ids always starts from 1. So you can check using ids 1,2,3...and so on.
