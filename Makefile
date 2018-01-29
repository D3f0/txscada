# Some Makefile utilities
define PRINT_HELP_PYSCRIPT
import re, sys

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

lines = []
print('''
{BOLD}Docker Compose management{ENDC}
This Makefile provides targets to develop on a the dev environment\
and build the porduction image(s).
'''.format(**bcolors.__dict__))
targets = []
for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		targets.append((target, help))

for target, help in sorted(targets):
	print(r"%s%-32s%s %s" % (bcolors.OKGREEN, target, bcolors.ENDC, help))

print("""

""".format(**bcolors.__dict__))

endef
export PRINT_HELP_PYSCRIPT

all: up

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST) | less

up:  ## Turn on all containers, builds if necessary
	docker-compose up --build -d

up_no_build:  ## Starts containers skiping build
	docker-compose up -d

build:  ## Builds containers
	docker-compose build

build_no_cache:  ## Builds containers without using cache
	docker-compose build --no-cache

shell:   ## Creates a shell on existing container
	docker-compose exec $(ENV) django bash 

shell_new: ## Creates a new container running a shell
	docker-compose run --rm $(ENV) django bash

shell_no_install:  ## Creates a container with a shell, without installing dev tools
	$(eval ENV := -e $(ENV) NO_INSTALL=1)
	docker-compose run --rm $(ENV) django bash

shell_root:   ## Runs a shell as root in django container
	@docker-compose exec $(ENV) -u 0 django bash

quick_run:  CMD = bash
quick_run:  ## Run command
	@docker-compose run --rm -e NO_INSTALL=1 django $(CMD)

manage.py: CMD = help
manage.py:
	@docker-compose exec django python $(MODULES) manage.py $(CMD)

diffsettings:  ## Shows active settings
	@$(MAKE) manage.py CMD='diffsettings'

syncdb:  ## Old Django command for syncing DBs
	@$(MAKE) manage.py CMD='syncdb --noinput --migrate'

collectstatic:  ## Collect static files
	@$(MAKE) manage.py CMD='collectstatic --noinput'


logs:  ## Show logs
	@docker-compose logs $(SERVICE)

log_tail:
	@docker-compose logs -f $(SERVICE)

ps:  ## Show current 
	@docker-compose ps

re:  ## Rebuilds
	@docker-compose down
	@docker-compose up --build -d 
	@$(MAKE) log_tail SERVICE=django

runserver_pdb: PORT = 8000
runserver_pdb:
	docker-compose run \
		-p 8000:$(PORT) \
		-e NO_INSTALL=1 \
		django python -m pdb \
		manage.py runserver --noreload --nothreading  0:8000

	
fix_local_linting:  ## Fix local linting
