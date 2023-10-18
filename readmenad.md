py manage.py makemigrations
py manage.py migrate

py manage.py initialize_data
py manage.py seed_place
py manage.py seed_truck
py manage.py seed_nodes

<!-- run program -->

.\venv\Scripts\activate
python .\manage.py runserver

<!-- update ver -->
git add .
git commit -m "resolve"
git pull origin main

<!-- install module -->
pip install modulnya

<!-- update module -->
pip freeze > .\requirements.txt
