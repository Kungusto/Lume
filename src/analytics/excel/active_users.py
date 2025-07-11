from io import BytesIO
import pandas as pd
from pydantic import BaseModel


# класс для табличек
class UsersDFExcelRepository:
    def __init__(self, table_name: str):
        self.table_name = table_name
        try:
            self.df = pd.read_excel(table_name)
        except (FileNotFoundError, ValueError):
            self.df = pd.DataFrame()

    def add_bulk(self, data: list[BaseModel]):
        new_row = pd.DataFrame([index.model_dump() for index in data])
        self.df = pd.concat([self.df, new_row], ignore_index=True)

    def get_filtered(self, **filter_by):
        if not filter_by:
            return
        result = self.df
        for col, val in filter_by.items():
            result = result[result[col] == val]
        return result

    def add(self, data: BaseModel):
        new_row = pd.DataFrame([data.model_dump()])
        self.df = pd.concat([self.df, new_row], ignore_index=True)

    def commit(self):
        self.df.to_excel(self.table_name, index=False)

    def to_bytes(self) -> bytes:
        buffer = BytesIO()
        self.df.to_excel(buffer, index=False)
        buffer.seek(0)
        return buffer.read()
