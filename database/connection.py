from sqlmodel import Session, SQLModel, create_engine, select
from typing import Annotated
from fastapi import Depends
from database.model import Client, User, Role, UserClient
from security.passwordUtils import generatePassword


sqlite_url = "postgresql://postgres:vansh12345@localhost/new_test_db"

engine = create_engine(sqlite_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# Seed for Role Table:-
def insert_predefined_role_data(session):
    role_to_add = [
        Role(name="superadmin"),
        Role(name="recruiter")
    ]
    session.add_all(role_to_add)
    session.commit()


# Seed for Client Table:-
def insert_predefined_client_data(session):
    client_to_add = [
        Client(name="Exploratory"),
        Client(name="Testing Team QA"),
        Client(name="Company Tester 1"),
        Client(name="Testing Company QA2"),
        Client(name="Rise Work"),
        Client(name="Centerbase Work")
    ]
    session.add_all(client_to_add)
    session.commit()


# Seed for User Table:-
def insert_predefined_user_data(session):
    superadmin_role_id = session.exec(select(Role.id).where(Role.name=="superadmin")).first()
    recruiter_role_id = session.exec(select(Role.id).where(Role.name=="recruiter")).first()
    superadmin_password=generatePassword("Superadmin@123")
    recruiter__password=generatePassword("Recruiter@123")
    user_to_add = [
        User(name="Sunil Kumar",password=superadmin_password,email="sunil@thinksys.com",role_id=superadmin_role_id),
        User(name="Beatriz Torrengrosa",password=recruiter__password,email="beatriz@thinksys.com",role_id=recruiter_role_id),
        User(name="Mateen Ahmed",password=recruiter__password,email="mateen@thinksys.com",role_id=recruiter_role_id),
        User(name="Joe Doe",password=recruiter__password,email="joe@thinksys.com",role_id=recruiter_role_id),
    ]
    session.add_all(user_to_add)
    session.commit()


# Seed for User_Client Table:-
def insert_predefined_user_client_data(session):
    # Recruiter Id Fetch:-
    user_id_beatriz = session.exec(select(User.id).where(User.name=="Beatriz Torrengrosa")).first() # User-Id of First Recruiter that is Beatriz Torrengrosa.
    user_id_Mateen = session.exec(select(User.id).where(User.name=="Mateen Ahmed")).first() # User-Id of Second Recruiter that is Beatriz Torrengrosa
    # Client Id Fetch:-
    client_id_exploratory = session.exec(select(Client.id).where(Client.name=="Exploratory")).first() # Client-Id of Exploratory.
    client_id_testing_company = session.exec(select(Client.id).where(Client.name=="Testing Company QA2")).first() # Client-Id of Testing Company QA2.
    client_id_rise_work = session.exec(select(Client.id).where(Client.name=="Rise Work")).first() # Client-Id of Rise Work.
    client_id_centerbase_work = session.exec(select(Client.id).where(Client.name=="Centerbase Work")).first() # Client-Id of Centerbase Work.
    data_to_add = [
        UserClient(user_id=user_id_beatriz, client_id=client_id_exploratory),
        UserClient(user_id=user_id_beatriz, client_id=client_id_testing_company),
        UserClient(user_id=user_id_Mateen, client_id=client_id_rise_work),
        UserClient(user_id=user_id_Mateen, client_id=client_id_centerbase_work)
    ]
    session.add_all(data_to_add)
    session.commit()

        

def check_and_run_seed():
    with Session(engine) as session:
        # Below, we check if at least one row exists in the Role, Client, or User tables. If a record exists, the seeding function is skipped; if no records exist, the seeding function will run.
        check_Role_statement = session.exec(select(Role)).first()
        check_client_statement =  session.exec(select(Client)).first()
        check_user_statement =  session.exec(select(User)).first()
        check_userClient_statement =  session.exec(select(UserClient)).first()

        if not check_Role_statement:
            insert_predefined_role_data(session)

        if not check_client_statement:
            insert_predefined_client_data(session)

        if not check_user_statement:
            insert_predefined_user_data(session)

        if not check_userClient_statement:
            insert_predefined_user_client_data(session)

   
def get_session():
    with Session(engine) as session:
        yield session



SessionDep = Annotated[Session, Depends(get_session)]



