from sqlalchemy.orm import Session

from lsshu.internal.crud import CRUDTree
from lsshu.internal.helpers import token_get_password_hash
from lsshu.oauth.model import ModelOAuthUsers, ModelOAuthPermissions, ModelOAuthRoles
from lsshu.oauth.user.schema import SchemasOAuthUserStoreUpdate


class CRUDOAuthUser(CRUDTree):
    """用户表操作"""
    params_model = ModelOAuthUsers
    params_relationship = {
        "permissions": ModelOAuthPermissions,
        "roles": ModelOAuthRoles
    }

    @classmethod
    def store(cls, db: Session, item: SchemasOAuthUserStoreUpdate, **kwargs):
        if hasattr(item, "password") and item.password:
            item.password = token_get_password_hash(item.password)
        return super(CRUDOAuthUser, cls).store(db=db, item=item, **kwargs)

    @classmethod
    def update(cls, db: Session, pk: int, item: SchemasOAuthUserStoreUpdate, **kwargs):
        if hasattr(item, "password") and item.password:
            item.password = token_get_password_hash(item.password)
        else:
            if hasattr(item, "password"):
                delattr(item, "password")

        return super(CRUDOAuthUser, cls).update(db=db, pk=pk, item=item, **kwargs)

    @classmethod
    def all(cls, **kwargs):
        kwargs.update({
            "order": [("sort", "asc")]
        })
        return super().all(**kwargs)
