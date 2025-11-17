from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ...db.database import get_db
from ...models.user import User
from ...models.module import Module
from ...schemas.module import Module as ModuleSchema, ModuleCreate, ModuleUpdate, ModuleWithCards
from ...core.deps import get_current_active_user

router = APIRouter()


@router.get("/{search_string}", response_model=List[ModuleSchema])
async def get_user_modules(
    search_string: str,
    skip: int = 0,
    take: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all modules owned by current user"""
    modules = db.query(Module).filter(Module.owner_id == current_user.id, search_string in Module.name).all()
    if len(modules) < skip:
        return []
    return modules[skip:min(len(modules), skip + take)]


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
        owner_id=current_user.id,
        edit_access = module.EditAccess,
        view_access= module.ViewAccess,
        password_hash = module.PasswordHash
    )
    
    db.add(db_module)
    db.commit()
    db.refresh(db_module)
    
    return db_module


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
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    for field, value in module_update.dict(exclude_unset=True).items():
        setattr(module, field, value)
    
    db.commit()
    db.refresh(module)
    
    return module


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
