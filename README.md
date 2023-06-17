# Projeto Dundie API - LINUXtips

Este projeto é parte do treinamento Python Web API da [LinuxTips](https://linuxtips.io)

Este material serve de apoio para as aulas em video. Alguns desses comandos podem conter erros, pois no momento da execução 
não tinha Token (via JWT) para autenticar o usuario, quando tiver tempo atualizarei esses comandos.

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
docker-compose exec api dundie shell
```
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

Tem que incluir token de acesso

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

```bash
curl -X 'POST' -H 'Content-Type: application/json' \
  --data-raw '{"email": "pam@dm.com", "dept": "Accounting", "password": "jimjim", "name": "Pam Besly"}' \
  -k 'http://localhost:8000/user/'
```

### Criando Token

```bash
curl -X 'POST' \
  'http://localhost:8000/token' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=pam-besly&password=jimjim' | jq
```

```bash
curl -X 'POST' \
  'http://localhost:8000/token' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=mizuno&password=1234' | jq
```

### Atualizando dados de profile 

Usando Swagger com usuario mizuno

```bash
curl -X 'PATCH' \
  'http://localhost:8000/user/pam-besly/?fresh=false' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtaXp1bm8iLCJmcmVzaCI6dHJ1ZSwiZXhwIjoxNjg2OTUxMzc0LCJzY29wZSI6ImFjY2Vzc190b2tlbiJ9.GWoHCUbfK_kilIYEEPUqd-_66OalgqV9V2MtElacSok' \
  -H 'Content-Type: application/json' \
  -d '{
  "avatar": "https://test.com/pam.png",
  "bio": "I am the boss"
}'
```

Usando Swagger com usuario ganso

```bash
curl -X 'PATCH' \
  'http://localhost:8000/user/pam-besly/?fresh=false' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnYW5zbyIsImZyZXNoIjp0cnVlLCJleHAiOjE2ODY5NTEzMzcsInNjb3BlIjoiYWNjZXNzX3Rva2VuIn0.9zPSKxLO0W8ejLfOz_PuXVvLQgP9Xoh6tKf5u2AnA2E' \
  -H 'Content-Type: application/json' \
  -d '{
  "avatar": "https://test.com/pam.png",
  "bio": "I am the boss"
}'
```

### Resetando password

```bash
curl -X 'POST' \
'http://localhost:8000/user/pam-besly/password/' \
 -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtaXp1bm8iLCJmcmVzaCI6dHJ1ZSwiZXhwIjoxNjg2OTU0NzI4LCJzY29wZSI6ImFjY2Vzc190b2tlbiJ9.ujfmX3kRdA070I7oDy_RuHgK10m1DQPk7-1K8M5B6to' \
 -H 'Content-Type: application/json'  \
 -d '{"password": "234551231313213", "password_confirm": "234551231313213"}' | jq
```

Note que o hashs mudaram

Antigo - $2b$12$GrY0qZhLOF/Y.rBDz4Nnmu19JGHSBTGzyGmOdY3CZZ9BE5l2UJvZW

Novo - $2b$12$M4Wia32V9PO/eDoWDkQKCO1T2ViyMxzBdyy9TFRyyqSdSnHSPrGRC

### Esqueci senha

```bash
docker-compose exec api dundie shell
```

```bash
from dundie.tasks.user import try_to_send_pwd_reset_email

try_to_send_pwd_reset_email('pam@dm.com')
```

Procure na raiz do projeto um arquivo email.log

```bash
curl -X 'POST' \
'http://localhost:8000/user/pam-besly/password/?pwd_reset_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJwYW0tYmVzbHkiLCJleHAiOjE2ODcwMDg1OTMsInNjb3BlIjoicHdkX3Jlc2V0In0.pAi4apawiBsFu5XQWaic-i0AxAbq2B8OGaeOLhVyYKw' \
 -H 'Content-Type: application/json'  \
 -d '{"password": "234551231313213", "password_confirm": "234551231313213"}' | jq
```

