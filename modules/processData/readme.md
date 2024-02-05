add new model then run this command to generate migration:

```
alembic revision --autogenerate -m "Description of changes"

```


now run this command to run the new migration:

```
alembic upgrade head

```