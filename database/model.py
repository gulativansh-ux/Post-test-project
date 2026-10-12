from sqlmodel import Field, SQLModel


# We use the config table=True to tell SQLModel that this is a table model, it represents a table.
# It's also possible to have models without table=True, those would be only data models, without a table in the database, they would not be table models.


class Client(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    password: str 
    email: str
    role_id: int


class Role(SQLModel, table=True):      
    id: int | None = Field(default=None, primary_key=True)
    name: str


class UserClient(SQLModel, table=True):
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    client_id: int | None = Field(default=None, foreign_key="client.id", primary_key=True)