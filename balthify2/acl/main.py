from fastapi import FastAPI

from balthify2 import acl


app = FastAPI()
app.include_router(acl.router, prefix='/acl')


@app.get('/')
def root():
    return {'message': 'Hello from balthify2 acl'}
