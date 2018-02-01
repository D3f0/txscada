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

# Verbosity switch
ifeq ($(V),1)
Q =
else
Q = @
endif

all: up

help:
	$(Q)python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST) | less

up:  ## Turn on all containers, builds if necessary
	$(Q)docker-compose up --build -d

down:  ## Bing containers down
	$(Q)docker-compose down $(SERVICE)

up_no_build:  ## Starts containers skiping build
	$(Q)docker-compose up -d

re:  ## Rebuild the image
	$(Q)$(MAKE) down
	$(Q)docker-compose up --build -d 
	

build:  ## Builds containers
	$(Q)docker-compose build

build_no_cache:  ## Builds containers without using cache
	$(Q)docker-compose build --no-cache

exec:  SERVICE = django
exec:  ## Executes command CMD in runnning container SERVICE
	$(Q)docker-compose exec $(ENV) $(SERVICE) $(CMD) || \
		echo "Cannot start $(CMD) in $(SERVICE), run: make up first. If fails try make tail_log"

wait:
	$(Q)echo "Wating for server to be running"
	$(MAKE) CMD="python wait.py localhost 8000" exec
	$(Q)echo "Wating for server to be running"

shell:   ## Creates a shell on existing container
	$(Q)$(MAKE) exec CMD=bash SERVICE=django
		
# if [ docker inspect -f '{{.State.Running}}' $$(docker-compose ps -q django)` == "false" ]; then \
# 	echo "Django container seems down. Try make up" \
# fi

shell_new_cont: ## Creates a new diposable container running a shell 
	$(Q)docker-compose run --rm $(ENV) django bash

shell_new_cont_quick: ## Creates a new container running a shell
	docker-compose run --rm $(ENV) -e NO_django bash

shell_root:   ## Runs a shell as root in django container
	$(Q)docker-compose exec $(ENV) -u 0 django bash

quick_run:  CMD = bash
quick_run:  ## Run command
	$(Q)docker-compose run --rm -e NO_INSTALL=1 django $(CMD)

manage.py: CMD = help
manage.py:
	$(Q)docker-compose exec django python $(MODULES) manage.py $(CMD)

diffsettings:  ## Shows active settings
	$(Q)$(MAKE) manage.py CMD='diffsettings'

syncdb:  ## Old Django command for syncing DBs
	$(Q)$(MAKE) manage.py CMD='syncdb --noinput --migrate'

collectstatic:  ## Collect static files
	$(Q)$(MAKE) manage.py CMD='collectstatic --noinput'

logs:  ## Show logs
	$(Q)docker-compose logs $(SERVICE)

tail_log:
	$(Q)docker-compose logs -f $(SERVICE)

ps:  ## Show current 
	$(Q)docker-compose ps

runserver_pdb: PORT = 8000
runserver_pdb:
	$(Q)docker-compose run \
		-p 8000:$(PORT) \
		-e NO_INSTALL=1 \
		django python -m pdb \
		manage.py runserver --noreload --nothreading  0:8000

	
fix_local_linting:  ## Fix local linting
