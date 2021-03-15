PROJECT_NAME=wps
LINES=79

clean:  ## Clean python bytecodes, optimized files, logs, cache, coverage...
	@find . -name "*.pyc" | xargs rm -rf
	@find . -name "*.pyo" | xargs rm -rf
	@find . -name "__pycache__" -type d | xargs rm -rf
	@find . -name ".pytest_cache" -type d | xargs rm -rf
	@rm -f *.log

env: ## Create .env file
	@cp -n localenv .env

style: clean ## format code and sort imports
	@black -S -t py38 -l ${LINES} .
	@isort .

style-check: ## black format check
	@black --check -S -t py38 -l ${LINES} .

mypy-check: ## mypy type check
	@mypy ${PROJECT_NAME}/

pylint-check: ## pylint check
	@pylint --rcfile=.pylintrc ${PROJECT_NAME}/

flake8-check: ## flake8 check
	@flake8 ${PROJECT_NAME}/ --count --show-source --statistics

runserver: ## default port  8000
	@cd ${PROJECT_NAME} && uvicorn main:app --reload

rundocker: ## build and run docker image port 8000
	@docker-compose up -d --build --force-recreate

stopdocker: ## stop docker application
	@docker-compose down

shell: clean ## ipython shell
	@cd ${PROJECT_NAME} && ipython

test: clean ## test using pytest
	@cd ${PROJECT_NAME} && python -m pytest . -s -v
