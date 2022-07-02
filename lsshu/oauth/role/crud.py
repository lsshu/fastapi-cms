from sqlalchemy.orm import Session

from lsshu.internal.crud import CRUDTree
from lsshu.oauth.model import ModelOAuthRoles, ModelOAuthPermissions
from lsshu.oauth.role.schema import SchemasOAuthRoleStoreUpdate


class CRUDOAuthRole(CRUDTree):
    """用户表操作"""
    params_model = ModelOAuthRoles
    params_relationship = {
        "permissions": ModelOAuthPermissions
    }

    @classmethod
    def store(cls, db: Session, item: SchemasOAuthRoleStoreUpdate, **kwargs):
        if item.permissions:
            from lsshu.internal.crud import BaseCRUD
            _relation = BaseCRUD.all(db=db, model=ModelOAuthPermissions, where=("id", 'in_', item.permissions))
            item.scopes = " ".join([relation.scope for relation in _relation])
        return super(CRUDOAuthRole, cls).store(db=db, item=item, **kwargs)

    @classmethod
    def update(cls, db: Session, pk: int, item: SchemasOAuthRoleStoreUpdate, **kwargs):
        if item.permissions:
            from lsshu.internal.crud import BaseCRUD
            _relation = BaseCRUD.all(db=db, model=ModelOAuthPermissions, where=("id", 'in_', item.permissions))
            item.scopes = " ".join([relation.scope for relation in _relation])
        return super(CRUDOAuthRole, cls).update(db=db, pk=pk, item=item, **kwargs)
