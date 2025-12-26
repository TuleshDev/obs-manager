from sqlalchemy import Column, Integer, String, CheckConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)

    chapter = Column(Integer, nullable=False, default=0)
    paragraph = Column(Integer, nullable=False, default=0)
    section = Column(Integer, nullable=False, default=0)
    position = Column(Integer, nullable=False, default=0)
    task_number = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        CheckConstraint('chapter >= 0', name='check_chapter_nonnegative'),
        CheckConstraint('paragraph >= 0', name='check_paragraph_nonnegative'),
        CheckConstraint('section >= 0', name='check_section_nonnegative'),
        CheckConstraint('position >= 0', name='check_position_nonnegative'),
        CheckConstraint('task_number >= 0', name='check_task_number_nonnegative'),
    )
