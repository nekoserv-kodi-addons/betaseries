./venv/bin/coverage run --rcfile=./betaseries/tests/.coveragerc -m unittest discover -s betaseries/tests/
./venv/bin/coverage report -m
./venv/bin/coverage html
/usr/bin/firefox ./htmlcov/index.html