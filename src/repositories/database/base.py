from sqlalchemy import select, update, delete, insert
from pydantic import BaseModel
from src.database import Base
from sqlalchemy.exc import NoResultFound
from src.exceptions.exceptions import ObjectNotFoundException

class BaseRepository : 
    model: Base = None
    schema: BaseModel = None

    def __init__(self, session) :
        self.session = session

    async def get_filtered(self, *filter, **filter_by) : 
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self.schema.model_validate(model, from_attributes=True) for model in models]

    async def add(self, data) :
        add_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        result = await self.session.execute(add_stmt)
        model = result.scalars().first()
        return self.schema.model_validate(model, from_attributes=True)
    
    async def add_bulk(self, data) :
        add_stmt = insert(self.model).values([item.model_dump() for item in data])
        await self.session.execute(add_stmt)

    async def edit(self, data, is_patch=False, *filter, **filter_by) : 
        edit_stmt = (
            update(self.model)
            .filter(*filter)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=is_patch))
            .returning(self.model)
        )
        result = await self.session.execute(edit_stmt)
        models = result.scalars().all()
        return [self.schema.model_validate(model, from_attributes=True) for model in models]

    async def get_one(self, *filter, **filter_by) : 
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        model = await self.session.execute(query)
        try :
            result = model.scalar_one()
        except NoResultFound as ex:
            raise ObjectNotFoundException from ex
        return self.schema.model_validate(result, from_attributes=True)

    async def delete(self, *filter, **filter_by) :
        delete_stmt = delete(self.model).filter(*filter).filter_by(**filter_by)
        await self.session.execute(delete_stmt)
    
    async def delete_bulk_by_ids(self, ids_to_delete: list[int], **filter_by) :
        delete_stmt = (
            delete(self.model)
            .filter(self.model.id.in_(ids_to_delete))
            .filter_by(**filter_by)
        )
        await self.session.execute(delete_stmt)
