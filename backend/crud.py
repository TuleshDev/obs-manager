import os
from sqlalchemy.orm import Session
from . import models, schemas


def get_students(db: Session):
    return db.query(models.Student).all()

def get_student(db: Session, student_id: int):
    return db.query(models.Student).filter(models.Student.id == student_id).first()

def create_student(db: Session, student: schemas.StudentCreate):
    data = student.dict(exclude={"scenario_ids"})
    db_student = models.Student(**data)

    if student.scenario_ids:
        scenarios = db.query(models.Scenario).filter(
            models.Scenario.id.in_(student.scenario_ids)
        ).all()
        db_student.scenarios = scenarios

    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

def update_student(db: Session, student_id: int, student: schemas.StudentUpdate):
    db_student = get_student(db, student_id)
    if db_student:
        data = student.dict(exclude_unset=True, exclude={"scenario_ids"})
        for key, value in data.items():
            setattr(db_student, key, value)

        if student.scenario_ids is not None:
            scenarios = db.query(models.Scenario).filter(
                models.Scenario.id.in_(student.scenario_ids)
            ).all()
            db_student.scenarios = scenarios

        db.commit()
        db.refresh(db_student)
    return db_student

def delete_student(db: Session, student_id: int):
    db_student = get_student(db, student_id)
    if db_student:
        db.delete(db_student)
        db.commit()
    return db_student


def get_scenarios(db: Session):
    return db.query(models.Scenario).all()

def get_scenario(db: Session, scenario_id: int):
    scenario = db.query(models.Scenario).filter(models.Scenario.id == scenario_id).first()
    if scenario:
        scenario_path = os.path.join("backend", "scenarios", scenario.name)
        if not os.path.exists(scenario_path):
            raise ValueError("Сценарий не реализован")
    return scenario

def create_scenario(db: Session, scenario: schemas.ScenarioCreate):
    db_scenario = models.Scenario(**scenario.dict())
    db.add(db_scenario)
    db.commit()
    db.refresh(db_scenario)
    return db_scenario

def update_scenario(db: Session, scenario_id: int, scenario: schemas.ScenarioUpdate):
    db_scenario = get_scenario(db, scenario_id)
    if db_scenario:
        for key, value in scenario.dict(exclude_unset=True).items():
            setattr(db_scenario, key, value)
        db.commit()
        db.refresh(db_scenario)
    return db_scenario

def delete_scenario(db: Session, scenario_id: int):
    db_scenario = db.query(models.Scenario).filter(models.Scenario.id == scenario_id).first()
    if db_scenario:
        scenario_path = os.path.join("backend", "scenarios", db_scenario.name)
        if os.path.exists(scenario_path):
            raise ValueError("Нельзя удалить сценарий: существует папка с реализацией")
        db.delete(db_scenario)
        db.commit()
    return db_scenario
