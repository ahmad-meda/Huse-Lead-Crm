from sqlalchemy import Column, Integer, String, Date, Text, Boolean, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship   
import os


# Create engine
engine = create_engine(os.getenv("DATABASE_URL", "postgresql://postgres:ias12345@localhost:5432/postgres"))
# Create declarative base
Base = declarative_base()
# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Member(Base):
    __tablename__ = "members"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_legal_name = Column(String, nullable=False)
    preferred_nickname = Column(String, nullable=False)
    date_of_birth = Column(String, nullable=False)
    nationality = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    email_address = Column(String, nullable=False, unique=True)
    suggested_membership_tier = Column(String, nullable=False)
    residential_address = Column(String, nullable=False)
    passport_number = Column(String, nullable=True)
    id_number = Column(String, nullable=True)
    occupation = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    linkedin_or_website = Column(String, nullable=True)
    education_background = Column(String, nullable=True)
    notable_affiliations = Column(String, nullable=True)
    agent_id = Column(String, nullable=False)
    lead_status = Column(String(50), nullable=True)
    lead_comments = Column(Text, nullable=True)
    status = Column(String, nullable=True)
    conversion_status = Column(String, nullable=True)
    approval_status = Column(String, nullable=False, default="Pending")
    company = Column(String, nullable=True)
    crm_backend_id = Column(String, nullable=True)


    def __repr__(self):
        return f"<Member(id={self.id}, name='{self.full_legal_name}', email='{self.email_address}')>"
    
class Employee(Base):
    __tablename__ = "employees"  # Make sure this matches your actual table name
    
    # Primary key - matches your DB column
    database_id = Column(Integer, primary_key=True, autoincrement=True)
    employeeid = Column(String, nullable=False)  
    
    # Personal Information - corrected column names based on your DB
    name = Column(String(255), nullable=False)
    contactno = Column(String(20))  
    first_name = Column(String(100)) 
    middle_name = Column(String(100))  
    last_name = Column(String(100))   
    emailid = Column(String(255), unique=True, index=True)  
    
    # Employment Details - corrected column names
    designation = Column(String(100))
    dateofjoining = Column(Date)  
    dateofbirth = Column(Date)   
    gender = Column(String(10))
    
    # Location and Policy - corrected column names
    office_location_id = Column(Integer)  
    work_policy_id = Column(Integer)      
    
    # Address Information - corrected column names
    home_latitude = Column(String(50))   
    home_longitude = Column(String(50))  
    
    # Company and Management - corrected column names
    company_id = Column(Integer)           
    group_id = Column(Integer)             
    reporting_manager_id = Column(Integer) 
    
    # Role and Department - corrected column names
    role_id = Column(Integer)       
    department_id = Column(Integer) 
    
    # Status fields - corrected column names
    deleted = Column(Boolean, default=False)    
    def __repr__(self):
        return f"<Employee(id={self.employeeid}, name='{self.name}', email='{self.emailid}')>"
    

class Approval(Base):
    __tablename__ = "approvals"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("employees.database_id", ondelete="CASCADE"), nullable=False)
    status = Column(Integer, nullable=False, default=3)
    

    def __repr__(self):
        return f"<Approval(id={self.id}, user_id={self.user_id}, status={self.status})>"
    
class SalesTeam(Base):
    __tablename__ = "sales_team"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.database_id"), nullable=False)
    crm_token = Column(String(255), nullable=False)
    employee = relationship("Employee", backref="sales_team_members")

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()