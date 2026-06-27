from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey("departments.id"))
    created_at = Column(TIMESTAMP)
    
    children = relationship("Department", remote_side=[id])

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    created_at = Column(TIMESTAMP)

class Developer(Base):
    __tablename__ = "developers"
    employee_id = Column(Integer, ForeignKey("employees.id"), primary_key=True)
    programming_language = Column(String, nullable=False)

class Manager(Base):
    __tablename__ = "managers"
    employee_id = Column(Integer, ForeignKey("employees.id"), primary_key=True)
    team_size = Column(Integer, nullable=False)

class EmployeeHistory(Base):
    __tablename__ = "employees_history"
    version_id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, nullable=False)
    version = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    department_id = Column(Integer)
    is_current = Column(Boolean)
    changed_at = Column(TIMESTAMP)
