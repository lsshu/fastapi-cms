from lsshu.internal.crud import CRUDTree
from lsshu.oauth.model import ModelOAuthPermissions


class CRUDOAuthPermission(CRUDTree):
    """权限表操作"""
    params_model = ModelOAuthPermissions
