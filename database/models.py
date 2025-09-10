from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Department(Base):
    __tablename__ = 'departments'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    faculty = relationship("Faculty", back_populates="department")

class Faculty(Base):
    __tablename__ = 'faculty'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    department_id = Column(Integer, ForeignKey('departments.id'))
    department = relationship("Department", back_populates="faculty")
    publications = relationship("Publication", back_populates="faculty")
    last_updated = Column(DateTime, default=datetime.utcnow)

class Publication(Base):
    __tablename__ = 'publications'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500))
    journal = Column(String(200))
    year = Column(Integer)
    citations = Column(Integer, default=0)
    doi = Column(String(100), unique=True)
    faculty_id = Column(Integer, ForeignKey('faculty.id'))
    faculty = relationship("Faculty", back_populates="publications")
    is_disambiguated = Column(Boolean, default=False)
    last_updated = Column(DateTime, default=datetime.utcnow)
