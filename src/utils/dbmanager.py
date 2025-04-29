from src.repositories.users import UsersRepository

class DBManager : 
    def __init__(self, session_factory) :
        self.session_factory = session_factory
        
    async def __aenter__(self) : 
        self.session = self.session_factory
        
        self.users =  UsersRepository(self.session)
        
    async def __aexit__(self) :
        self.session.rollback()
        self.session.close()
        
    async def commit(self) :
        self.session.commit()
        