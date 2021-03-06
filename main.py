from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from lsshu.oauth.main import router as router_oauth

app = FastAPI(
    title='Base API Docs',
    description='Base API接口文档',
    version='1.0.0'
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router_oauth, prefix="/api")
if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
