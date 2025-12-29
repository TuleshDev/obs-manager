from pydantic import BaseModel, EmailStr
from typing import Optional

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
    pass


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


class Student(StudentBase):
    id: int

    class Config:
        orm_mode = True
