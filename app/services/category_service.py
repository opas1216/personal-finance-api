from sqlalchemy.orm import Session
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.exceptions import NotFoundException, ForbiddenException


def create_category(db: Session, user_id: int, data: CategoryCreate) -> Category:
    # 1. 把 schema 轉成 model
    category = Category(**data.model_dump(), user_id=user_id)

    # 2. db.add() → db.commit() → db.refresh()
    db.add(category)
    db.commit()
    db.refresh(category)

    # 3. return category
    return category


def get_category(db: Session, category_id: int, user_id: int) -> Category:
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        raise NotFoundException("Category not found")

    if category.user_id != user_id:
        raise ForbiddenException("You do not have permission to access this category")

    return category


def get_categories(db: Session, user_id: int) -> list[Category]:
    return db.query(Category).filter(Category.user_id == user_id).all()


def update_category(db: Session, category_id: int, user_id: int, data: CategoryUpdate) -> Category:
    category = get_category(db, category_id, user_id)

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)

    return category


def delete_category(db: Session, category_id: int, user_id: int) -> None:
    category = get_category(db, category_id, user_id)

    db.delete(category)
    db.commit()




