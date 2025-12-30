from pydantic import BaseModel, EmailStr
from typing import List, Optional


class StudentBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    city: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None

    chapter: Optional[int] = 0
    paragraph: Optional[int] = 0
    section: Optional[int] = 0
    position: Optional[int] = 0
    task_number: Optional[int] = 0


class StudentCreate(StudentBase):
    scenario_ids: Optional[List[int]] = []


class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    city: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None

    chapter: Optional[int] = None
    paragraph: Optional[int] = None
    section: Optional[int] = None
    position: Optional[int] = None
    task_number: Optional[int] = None

    scenario_ids: Optional[List[int]] = None


class Student(StudentBase):
    id: int
    scenarios: List[Scenario] = []

    class Config:
        orm_mode = True


class ScenarioBase(BaseModel):
    name: str
    description: str


class ScenarioCreate(ScenarioBase):
    pass


class ScenarioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class Scenario(ScenarioBase):
    id: int

    class Config:
        orm_mode = True
