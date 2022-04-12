from fastapi import APIRouter
from app.demo.project import router as router_project, permission as permission_project

router = APIRouter()
router.include_router(router_project)

name = __name__.capitalize()
APP_PERMISSION = {
    "name": "demo", "scope": name, "children": [
        permission_project
    ]
}
