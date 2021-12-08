# Periodic tasks | My Message In A Bottle

This is the source code of Message in a Bottle application, self project of *Advanced Software Engineering* course,
University of Pisa.

## Team info

- The *squad id* is **8**
- The *team leader* is **Carlo Leo**

#### Members

| Name and Surname | Email                            |
|------------------|----------------------------------|
| Eli Melucci      | e.melucci1@studenti.unipi.it     |
| **Carlo Leo**    | c.leo5@studenti.unipi.it         |
| Federico Ramacciotti | f.ramacciotti4@studenti.unipi.it |
| Gabriele Baschieri | g.baschieri1@studenti.unipi.it   |
| Kostantino Prifti | k.prifti@studenti.unipi.it       |


## Instructions
### Initialization
Set up a virtual environment in your preferred way, then install the dependencies.
As an example:
```
python -m venv ./venv
source ./venv/bin/activate
python -m pip install -r requirements.dev.txt
```

### Run the project

Simply run the `run.sh` script.

#### Application Environments

The available environments are:

- debug
- development
- testing
- production

The `run.sh` script defaults to a development environment.

**Note:** if you use `docker-compose up` you are going to startup a production ready microservice, hence postgres will be used as default database and gunicorn will serve your application.

### Run tests

To run all the tests, execute the following command:

`python -m pytest -v`

You can also specify one or more specific test files, in order to run only those specific tests.
In case you also want to see the overall coverage of the tests, execute the following command:

`python -m pytest -v --cov-report term-missing`

---
