from sqlalchemy import select, update, delete, insert

class BaseRepository : 
    model = None
    schema = None
    
    async def add(self, data) :
        query = insert(self.model).values(data.model_dump()).returning(self.model)
        return query
    
    async def edit(self, data, is_patch=False) : ...