from fastapi import FastAPI

from dundie.routes.user import router as user_router


app = FastAPI(
    title="dundie",
    version="0.1.1",
    description='dundie is a reward API',
)

app.include_router(user_router, prefix="/user", tags=["user"])

# @app.get("/", response_model=UserResponse)
# def hello(session: Session = ActiveSession):
#     return session.exec(select(User)).first()