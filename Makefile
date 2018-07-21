COMPOSE_FILE?=dev.yml
BASE=docker-compose -f $(COMPOSE_FILE)
RUN_DJANGO = $(BASE) run --rm django

shell:
	$(RUN_DJANGO) manage shell

shell_plus:
	$(RUN_DJANGO) manage shell_plus

migrate:
	$(RUN_DJANGO) manage migrate

makemigrations:
	$(RUN_DJANGO) manage makemigrations

test:
	$(BASE) run django pytest ../tests/

sh:
	$(RUN_DJANGO) sh

up:
	$(BASE) up

stop:
	$(BASE) stop

down:
	$(BASE) down

build:
	$(BASE) build

runserver:
	$(BASE) run --service-ports --rm django runserver

runserver_plus:
	$(BASE) run --service-ports --rm django runserver_plus

outdated:
	$(BASE) pip list --outdated --format=columns

isort:
	$(RUN_DJANGO) isort

mypy:
	$(RUN_DJANGO) mypy

black:
	$(RUN_DJANGO) black

