from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class DepartmentCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None

class EmployeeCreate(BaseModel):
    name: str
    department_id: int
    employee_type: str  # "developer" or "manager"
    extra: Dict[str, Any]

class EmployeeResponse(BaseModel):
    id: int
    name: str
    department_id: int
    type: Optional[str] = None
    extra: Optional[Dict] = None

class EmployeeHistoryResponse(BaseModel):
    version_id: int
    employee_id: int
    version: int
    name: str
    department_id: Optional[int]
    is_current: bool
    changed_at: datetime

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    department_id: Optional[int] = None
    extra: Optional[Dict] = None
