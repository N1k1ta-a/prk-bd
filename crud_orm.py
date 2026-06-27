from sqlalchemy.orm import Session
from models_orm import Employee, Developer, Manager, EmployeeHistory, Department
from schemas import EmployeeCreate, EmployeeUpdate
from typing import List, Dict, Optional

def create_employee_orm(db: Session, data: EmployeeCreate) -> int:
    emp = Employee(name=data.name, department_id=data.department_id)
    db.add(emp)
    db.flush()
    
    if data.employee_type == "developer":
        dev = Developer(employee_id=emp.id, programming_language=data.extra.get("programming_language", "Python"))
        db.add(dev)
    elif data.employee_type == "manager":
        mgr = Manager(employee_id=emp.id, team_size=data.extra.get("team_size", 1))
        db.add(mgr)
    
    db.commit()
    return emp.id

def get_employee_orm(db: Session, employee_id: int) -> Optional[Dict]:
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        return None
    
    result = {"id": emp.id, "name": emp.name, "department_id": emp.department_id}
    
    dev = db.query(Developer).filter(Developer.employee_id == employee_id).first()
    if dev:
        result["type"] = "developer"
        result["extra"] = {"programming_language": dev.programming_language}
    else:
        mgr = db.query(Manager).filter(Manager.employee_id == employee_id).first()
        if mgr:
            result["type"] = "manager"
            result["extra"] = {"team_size": mgr.team_size}
    
    return result

def update_employee_orm(db: Session, employee_id: int, data: EmployeeUpdate) -> bool:
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        return False
    
    if data.name:
        emp.name = data.name
    if data.department_id is not None:
        emp.department_id = data.department_id
    
    if data.extra:
        dev = db.query(Developer).filter(Developer.employee_id == employee_id).first()
        if dev and "programming_language" in data.extra:
            dev.programming_language = data.extra["programming_language"]
        else:
            mgr = db.query(Manager).filter(Manager.employee_id == employee_id).first()
            if mgr and "team_size" in data.extra:
                mgr.team_size = data.extra["team_size"]
    
    db.commit()
    return True

def delete_employee_orm(db: Session, employee_id: int) -> bool:
    emp = db.query(Employee).filter(Employee.id == employee_id).first()
    if not emp:
        return False
    
    # Удаляем связанные записи (ORM сам обработает каскадное удаление, если оно настроено)
    # Но для надёжности удаляем явно
    db.query(Developer).filter(Developer.employee_id == employee_id).delete()
    db.query(Manager).filter(Manager.employee_id == employee_id).delete()
    db.query(EmployeeHistory).filter(EmployeeHistory.employee_id == employee_id).delete()
    
    db.delete(emp)
    db.commit()
    return True

def get_history_orm(db: Session, employee_id: int) -> List[Dict]:
    history = db.query(EmployeeHistory).filter(
        EmployeeHistory.employee_id == employee_id
    ).order_by(EmployeeHistory.version).all()
    
    return [{"version_id": h.version_id, "version": h.version, "name": h.name, 
             "department_id": h.department_id, "is_current": h.is_current, 
             "changed_at": h.changed_at} for h in history]

def get_tree_orm(db: Session) -> List[Dict]:
    depts = db.query(Department).order_by(Department.id).all()
    items = [{"id": d.id, "name": d.name, "parent_id": d.parent_id} for d in depts]
    return build_tree(items)

def build_tree(items: List[Dict], parent_id: Optional[int] = None) -> List[Dict]:
    result = []
    for item in items:
        if item["parent_id"] == parent_id:
            result.append({
                "id": item["id"],
                "name": item["name"],
                "children": build_tree(items, item["id"])
            })
    return result

def list_employees_orm(db: Session, department_id: Optional[int] = None) -> List[Dict]:
    query = db.query(Employee)
    if department_id:
        query = query.filter(Employee.department_id == department_id)
    
    employees = query.all()
    result = []
    for emp in employees:
        emp_data = get_employee_orm(db, emp.id)
        if emp_data:
            result.append(emp_data)
    return result