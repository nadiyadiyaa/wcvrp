py manage.py makemigrations
py manage.py migrate

python .\manage.py loaddata .\master\fixtures\
<!-- py manage.py initialize_data -->
py manage.py seed_place
py manage.py seed_truck
py manage.py seed_nodes

<!-- cara run program -->
.\venv\Scripts\activate
python .\manage.py runserver

<!-- cara update ver -->
git pull origin main