start:
	python3 main.py -d
	python3 manage.py runserver -d


mig:
	python3 manage.py makemigrations
	python3 manage.py migrate
