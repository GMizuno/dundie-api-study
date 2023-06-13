# Projeto Dundie API - LINUXtips

Este projeto é parte do treinamento Python Web API da LINUXtips. https://linuxtips.io

Este material serve de apoio para as aulas em video.

O e-book do treinamento pode ser acessado em [Ebook](https://rochacbruno.github.io/dundie-api/)

## Comandos uteis 

### Iniciando container

```bash
docker-compose up -d 
```

### Parando container

```bash
docker-compose down
```

### Acessar CLI no docker 

```bash
docker-compose exec api dundie --help
```
### Logs da Api

```bash
docker-compose logs api --follow
```

### Comandos presentes na CLI

```bash
docker-compose exec api dundie user-list
docker-compose exec api dundie shell
docker-compose exec api /bin/bash
```
Criando usuário no Shell

```python
user = User(email='fgabsjdab', username='Gabriel', password='12345', name='Gabriel Mizuno', dept='sales', currency='USD')
session.add(user)
session.commit()
```

### Criando usuario usando Serializer

OBS: usar comando dundie shell

```python
from dundie.models.user import UserRequest

new = UserRequest(
    name="German Cano",
    email="cano@flu.com",
    dept="Sales",
    password="123412132asdasd",
)

db_user = User.from_orm(new)
session.add(db_user)
session.commit()
```

### Listando usuarios

```bash
curl --location 'http://localhost:8000/user' | jq
```
### Criandon usuario

```bash
curl -X 'POST' \
  'http://localhost:8000/user/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "Ganso",
  "email": "ganso@flu.com",
  "dept": "Adm",
  "password": "1231111",
  "currency": "USD"
}' | jq
```