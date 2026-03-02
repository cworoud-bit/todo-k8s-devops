# Laboratoire Docker Compose - Application Todo

## Architecture

Application trois-tiers avec :
- **Frontend** : Nginx servant des fichiers statiques
- **Backend** : Python/Flask (API REST)
- **Base de données** : PostgreSQL 15

## Structure des réseaux
- `frontend-net` : Communication frontend ↔ backend
- `backend-net` : Communication backend ↔ database

## Prérequis
- Docker Engine 20.10+
- Docker Compose 2.0+


#les details de conteneur
docker-compose ps 

#Vérification de l'isolation réseau
docker network ls

# le frontend appeler l'API backend
docker exec todo-frontend curl http://todo-backend:5000/health

# Depuis le backend, tester la connexion DB
docker exec todo-backend python -c "import psycopg2; conn=psycopg2.connect(host='database', dbname='todoapp', user='todouser', password='todopassword123'); print('Connexion DB OK')"



