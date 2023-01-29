set -x

autoflake --remove-all-unused-imports --remove-unused-variables --in-place app --exclude=__init__.py
black app
isort app
