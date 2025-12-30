from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, CheckConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

student_scenario = Table(
    "student_scenario",
    Base.metadata,
    Column("student_id", Integer, ForeignKey("students.id"), primary_key=True),
    Column("scenario_id", Integer, ForeignKey("scenarios.id"), primary_key=True),
)

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    city = Column(String(100), nullable=True)
    address = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)

    chapter = Column(Integer, nullable=False, default=0)
    paragraph = Column(Integer, nullable=False, default=0)
    section = Column(Integer, nullable=False, default=0)
    position = Column(Integer, nullable=False, default=0)
    task_number = Column(Integer, nullable=False, default=0)

    scenarios = relationship("Scenario", secondary=student_scenario, back_populates="students")

    __table_args__ = (
        CheckConstraint('chapter >= 0', name='check_chapter_nonnegative'),
        CheckConstraint('paragraph >= 0', name='check_paragraph_nonnegative'),
        CheckConstraint('section >= 0', name='check_section_nonnegative'),
        CheckConstraint('position >= 0', name='check_position_nonnegative'),
        CheckConstraint('task_number >= 0', name='check_task_number_nonnegative'),
    )


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)

    students = relationship("Student", secondary=student_scenario, back_populates="scenarios")
