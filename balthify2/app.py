from fastapi import FastAPI

from balthify2 import acl, schedule


app = FastAPI()
app.include_router(acl.router, prefix='/acl')
app.include_router(schedule.router, prefix='/schedule')


@app.get('/')
async def root():
    return {'message': 'Hello from balthify2 bundle'}
