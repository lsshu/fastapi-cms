from fastapi import APIRouter

from lsshu.oauth.user.main import router as router_user
from lsshu.oauth.role.main import router as router_role
from lsshu.oauth.permission.main import router as router_permission
from lsshu.oauth.annex.main import router as router_annex

from config import OAUTH_OAUTH_ROUTER

router = APIRouter(**OAUTH_OAUTH_ROUTER)

router.include_router(router_user)
router.include_router(router_role)
router.include_router(router_permission)
router.include_router(router_annex)
