from lsshu.oauth.model import ModelOAuthAnnexes as Models
from lsshu.internal.crud import BaseCRUD


class CRUD(BaseCRUD):
    """表操作"""
    params_model = Models
