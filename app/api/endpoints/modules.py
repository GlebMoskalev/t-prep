from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ...db.database import get_db
from ...models.user import User
from ...models.module import Module
from ...models.module_access import ModuleAccess, AccessLevel as AL
from ...schemas.module import Module as ModuleSchema, ModuleCreate, ModuleUpdate, ModuleWithCards, GetModulesResponse, AccessLevel as SchemaAccessLevel
from ...core.deps import get_current_active_user

router = APIRouter()


@router.get("/", response_model=GetModulesResponse)
async def get_user_modules(
    skip: int = 0,
    take: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    modules = db.query(Module).filter(
        Module.owner_id == current_user.id
    ).all()
    
    if len(modules) < skip:
        return GetModulesResponse(items=[], total_count=len(modules))

    return GetModulesResponse(
        items=[CreateModuleScema(module, GetModuleAccessByUserId(module, current_user.id)) for module in modules[skip:min(len(modules), skip + take)]], 
        total_count=len(modules)
    )

def GetModuleAccessByUserId(module: Module, user_id: int):
    for access in module.access:
        if access.owner_id == user_id:
            return access
    raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module with same access not found"
        )


@router.post("/", response_model=ModuleSchema)
async def create_module(
    module: ModuleCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new module"""
    db_module = Module(
        name=module.name,
        description=module.description,
        owner_id=current_user.id
    )
    
    db.add(db_module)
    db.commit()
    db.refresh(db_module)
    
    # Принудительно преобразуем к строке, если нужно
    module_with_access = ModuleAccess(
        module_id=db_module.id,
        owner_id=current_user.id,
        view_access=module.ViewAccess.value,
        edit_access=module.EditAccess.value,
        password_hash=module.PasswordHash
    )

    db.add(module_with_access)
    db.commit()
    db.refresh(module_with_access)

    return CreateModuleScema(db_module, module_with_access)

def CreateModuleScema(bd_model: Module, access_model: ModuleAccess):
    return ModuleSchema(
        name=bd_model.name,
        description=bd_model.description,
        id=bd_model.id,
        owner_id=bd_model.owner_id,
        created_at=bd_model.created_at,
        updated_at=bd_model.updated_at,
        ViewAccess=access_model.view_access,
        EditAccess=access_model.edit_access,
        PasswordHash=access_model.password_hash
    )


@router.patch("/{module_id}", response_model=ModuleSchema)
async def update_module(
    module_id: int,
    module_update: ModuleUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    module = db.query(Module).filter(
        Module.id == module_id,
        Module.owner_id == current_user.id
    ).first()

    module_access = db.query(ModuleAccess).filter(
        ModuleAccess.module_id == module_id,
        ModuleAccess.owner_id == current_user.id
    ).first()

    if not module_access:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )

    for field, value in module_update.dict(exclude_unset=True).items():
        setattr(module, field, value)
    
    if module_update.EditAccess != None:
        module_access.edit_access = module_update.EditAccess.value
        
    if module_update.ViewAccess != None:
        module_access.view_access = module_update.ViewAccess.value

    db.commit()
    db.refresh(module_access)
    db.refresh(module)

    return CreateModuleScema(module, module_access)


@router.delete("/{module_id}")
async def delete_module(
    module_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    module = db.query(Module).filter(
        Module.id == module_id,
        Module.owner_id == current_user.id
    ).first()
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    db.delete(module)
    db.commit()
    
    return {"message": "Module deleted successfully"}
