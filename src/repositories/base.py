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
    
    async def edit(self, data, is_patch=False) : ...

    async def get_one(self, *filter, **filter_by) : 
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        model = await self.session.execute(query)
        try :
            result = model.scalar_one()
        except NoResultFound as ex:
            raise ObjectNotFoundException from ex
        return self.schema.model_validate(result, from_attributes=True)