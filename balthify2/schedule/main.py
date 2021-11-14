from fastapi import FastAPI

from balthify2 import schedule


app = FastAPI()
app.include_router(schedule.router, prefix='/schedule')


@app.get('/')
def root():
    return {'message': 'Hello from balthify2 schedule'}
