# Simple Library Management App


## Table of Contents
  - [Features](#features)
    - [Implemented](#implemented)
    - [Todo](#todo)
  - [Installation guide](#installation-guide)
    - [Dependacies Installation](#dependacies-installation)
    - [Database Initialization](#database-initialization)
  - [Testing and Running Guide](#testing-and-running-guide)
  - [Key Python Modules Used](#key-python-modules-used)
  - [Reference Resources](#reference-resources)


## Features
### Implemented
1. Create User
![Register-User Screenshot](/screenshots/Screenshot-01-Register-User.png "Register User")

2. Login User
![Login-User Screenshot](/screenshots/Screenshot-02-Login.png "Login User")

3. Create, List, Read and Delete Book
![List Books Screenshot](/screenshots/Screenshot-03-List-Books.png "List Books")
![View Book Screenshot](/screenshots/Screenshot-04-View-Book.png "View Books")
![Update Book Screenshot](/screenshots/Screenshot-05-Update-Book.png "Update Book")

4. Create, List, Read and Delete Member
![Create Memmber Screenshot](/screenshots/Screenshot-07-Create-Member.png "Create Member")
![List Members Screenshot](/screenshots/Screenshot-08-List-Members.png "List Members")
![View Member Screenshot](/screenshots/Screenshot-09-View-Member.png "View Member")

5. Search Book using Title, Author or ISBN
6. Search Member using Name or ID Number
7. Issue a book to a member
![View Book Issue Transaction List Screenshot](/screenshots/Screenshot-11-List-Transactions.png "List Book Issue Transactions")

8. Issue a book return from a member
![View Member Screenshot](/screenshots/Screenshot-12-Transactions-Details.png "View Book Issue Transaction in Detail")

### Todo
-

## Installation Guide

### Dependacies Installation

- Installing the application locally requires
	1. [Python 3.7+](https://www.python.org/downloads/release/python-393/) - download and install it.
	2. [virtualenv](https://docs.python-guide.org/dev/virtualenvs/) - To create a virtual environment and activate it, run the following commands.
	```bash
	python3 -m venv venv
	source venv/bin/activate
	```
- Install the project dependacies from requirements.txt by running the following command in shell:
```bash
pip install -r requirements.txt
```
- The project contains a `.env.sample` file at its root with the environment variables required to run the app. Copy the file and name it `.env`, populating it with the correct values.
  __NOTE:__ The 'SECRET_KEY' environment variables is a long random bytes or str. You can easily generate the long random string by running the following command:
  ```bash
  python -c 'import secrets; print(secrets.token_hex())'
  ```
### Database Initialization
- This Flask application uses a [SQLite3](https://www.sqlite.org/) database to store data. The database has already been created and can be found in `/instance/library.db`. If not created install sqlite3 and create the `/instance/library.db` database.
- Run the following commands to set-up(create tables for the project) the database using [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/index.html):
```bash
flask db init
flask db migrate -m 'set-up the db'
flask db upgrade
```

## Testing and Running Guide
- To activate the development server run:
```bash
flask run
```
At this point, the development server should be accessible at _http://localhost:5000/_

## Key Python Modules Used
* **Flask**: micro-framework for web application development which includes the following dependencies:
  * click: package for creating command-line interfaces (CLI)
  * itsdangerous: cryptographically sign data
  * Jinja2: templating engine
  * MarkupSafe: escapes characters so text is safe to use in HTML and XML
  * Werkzeug: set of utilities for creating a Python application that can talk to a WSGI server
* **Flask-SQLAlchemy** - ORM (Object Relational Mapper) for Flask
* **Flask-Migrate** - An extension that handles SQLAlchemy database migrations for Flask applications using Alembic.
* **Marshmallow** - A framework for Object/Model Validation, serialization and deserialization.
* **python-dotenv** - Read key-value pairs from a .env file and set them as environment variables

## Reference Resources
- [virtualenv](https://docs.python-guide.org/dev/virtualenvs/)
- [Flask](https://flask.palletsprojects.com/)
- [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/index.html)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/quickstart/)
- [Marshmallow](https://marshmallow.readthedocs.io/en/stable/)
- [python-dotenv](https://https://pypi.org/project/python-dotenv/)
