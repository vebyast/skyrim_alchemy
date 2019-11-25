fix:
	pipenv run isort --recursive .
	pipenv run black ./

lint:
	pipenv run pylint --rcfile=setup.cfg alchemy
	pipenv run pytype
