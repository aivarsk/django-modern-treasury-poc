up:
	docker compose up

upd:
	docker compose up -d

pgtail:
	MSYS_NO_PATHCONV=1 docker compose exec -it postgres tail -n 0 -f /tmp/postgresql.log

pgshell:
	docker compose exec -it postgres bash -c 'PGPASSWORD=postgres psql -U postgres -h localhost -d postgres'	

bash:
	docker compose exec -it django bash

migrate:
	docker compose exec -it django python ./manage.py migrate

lint:
	docker compose exec -it django black debitcredit/*py
	docker compose exec -it django isort debitcredit/*py
