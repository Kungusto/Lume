from sqlalchemy import select, update, delete, insert
from pydantic import BaseModel

class BaseRepository : 
    model = None
    schema : BaseModel = None
    
    async def add(self, data) :
        add_stmt = insert(self.model).values(data.model_dump()).returning(self.model)
        query = await self.session.execute(add_stmt)
        return self.schema.model_validate(query, from_attributes=True)
    
    async def edit(self, data, is_patch=False) : ...