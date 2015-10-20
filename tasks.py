from invoke import task as invoke_task
from invoke import run


@invoke_task
def install():
    print ("Installing requirements.txt")
    run("pip install --quiet --upgrade -r requirements.txt")

@invoke_task
def tests():
    print ("Testing...")
    run("nosetests taxcloud/")