from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional
import os

from database import SessionLocal
from schemas import EmployeeCreate, EmployeeUpdate
from crud_orm import (
    create_employee_orm, get_employee_orm, update_employee_orm, 
    delete_employee_orm, get_history_orm, get_tree_orm, list_employees_orm
)
from crud_native import (
    create_employee_native, get_employee_native, update_employee_native,
    delete_employee_native, get_history_native, get_tree_native, list_employees_native
)

app = FastAPI(title="Учебная практика", description="ORM + Native SQL")

# Static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== ORM ENDPOINTS ====================
@app.post("/api/orm/employees")
def orm_create_employee(data: EmployeeCreate, db: Session = Depends(get_db)):
    emp_id = create_employee_orm(db, data)
    return {"id": emp_id, "message": "Employee created (ORM)"}

@app.get("/api/orm/employees/{employee_id}")
def orm_get_employee(employee_id: int, db: Session = Depends(get_db)):
    emp = get_employee_orm(db, employee_id)
    if not emp:
        raise HTTPException(404, "Employee not found")
    return emp

@app.get("/api/orm/employees")
def orm_list_employees(department_id: Optional[int] = None, db: Session = Depends(get_db)):
    return list_employees_orm(db, department_id)

@app.put("/api/orm/employees/{employee_id}")
def orm_update_employee(employee_id: int, data: EmployeeUpdate, db: Session = Depends(get_db)):
    if update_employee_orm(db, employee_id, data):
        return {"message": "Updated (ORM)"}
    raise HTTPException(404, "Employee not found")

@app.delete("/api/orm/employees/{employee_id}")
def orm_delete_employee(employee_id: int, db: Session = Depends(get_db)):
    if delete_employee_orm(db, employee_id):
        return {"message": "Deleted (ORM)"}
    raise HTTPException(404, "Employee not found")

@app.get("/api/orm/employees/{employee_id}/history")
def orm_get_history(employee_id: int, db: Session = Depends(get_db)):
    history = get_history_orm(db, employee_id)
    if not history:
        raise HTTPException(404, "History not found")
    return history

@app.get("/api/orm/tree")
def orm_get_tree(db: Session = Depends(get_db)):
    return get_tree_orm(db)

# ==================== NATIVE SQL ENDPOINTS ====================
@app.post("/api/native/employees")
def native_create_employee(data: EmployeeCreate):
    emp_id = create_employee_native(data.dict())
    return {"id": emp_id, "message": "Employee created (Native SQL)"}

@app.get("/api/native/employees/{employee_id}")
def native_get_employee(employee_id: int):
    emp = get_employee_native(employee_id)
    if not emp:
        raise HTTPException(404, "Employee not found")
    return emp

@app.get("/api/native/employees")
def native_list_employees(department_id: Optional[int] = None):
    return list_employees_native(department_id)

@app.put("/api/native/employees/{employee_id}")
def native_update_employee(employee_id: int, data: EmployeeUpdate):
    if update_employee_native(employee_id, data.dict(exclude_none=True)):
        return {"message": "Updated (Native SQL)"}
    raise HTTPException(404, "Employee not found")

@app.delete("/api/native/employees/{employee_id}")
def native_delete_employee(employee_id: int):
    if delete_employee_native(employee_id):
        return {"message": "Deleted (Native SQL)"}
    raise HTTPException(404, "Employee not found")

@app.get("/api/native/employees/{employee_id}/history")
def native_get_history(employee_id: int):
    history = get_history_native(employee_id)
    if not history:
        raise HTTPException(404, "History not found")
    return history

@app.get("/api/native/tree")
def native_get_tree():
    return get_tree_native()

# ==================== UI ====================
@app.get("/", response_class=HTMLResponse)
def serve_ui():
    html_path = os.path.join(static_dir, "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Index.html not found</h1>"
