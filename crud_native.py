from database import get_native_conn, get_native_cursor
from typing import List, Dict, Optional

def create_employee_native(data: Dict) -> int:
    conn = get_native_conn()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO employees (name, department_id) 
            VALUES (%s, %s) RETURNING id
        """, (data["name"], data["department_id"]))
        emp_id = cur.fetchone()[0]
        
        if data["employee_type"] == "developer":
            cur.execute("""
                INSERT INTO developers (employee_id, programming_language) 
                VALUES (%s, %s)
            """, (emp_id, data["extra"].get("programming_language", "Python")))
        elif data["employee_type"] == "manager":
            cur.execute("""
                INSERT INTO managers (employee_id, team_size) 
                VALUES (%s, %s)
            """, (emp_id, data["extra"].get("team_size", 1)))
        
        conn.commit()
        return emp_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def get_employee_native(employee_id: int) -> Optional[Dict]:
    conn, cur = get_native_cursor()
    
    try:
        cur.execute("SELECT id, name, department_id FROM employees WHERE id = %s", (employee_id,))
        emp = cur.fetchone()
        
        if not emp:
            return None
        
        result = dict(emp)
        
        cur.execute("SELECT programming_language FROM developers WHERE employee_id = %s", (employee_id,))
        dev = cur.fetchone()
        if dev:
            result["type"] = "developer"
            result["extra"] = {"programming_language": dev["programming_language"]}
        else:
            cur.execute("SELECT team_size FROM managers WHERE employee_id = %s", (employee_id,))
            mgr = cur.fetchone()
            if mgr:
                result["type"] = "manager"
                result["extra"] = {"team_size": mgr["team_size"]}
        
        return result
    finally:
        cur.close()
        conn.close()

def update_employee_native(employee_id: int, data: Dict) -> bool:
    conn = get_native_conn()
    cur = conn.cursor()
    
    try:
        # Проверяем существование сотрудника
        cur.execute("SELECT id FROM employees WHERE id = %s", (employee_id,))
        if not cur.fetchone():
            return False
        
        updates = []
        params = []
        if data.get("name"):
            updates.append("name = %s")
            params.append(data["name"])
        if data.get("department_id") is not None:
            updates.append("department_id = %s")
            params.append(data["department_id"])
        
        if updates:
            query = f"UPDATE employees SET {', '.join(updates)} WHERE id = %s"
            params.append(employee_id)
            cur.execute(query, params)
        
        if data.get("extra"):
            cur.execute("SELECT 1 FROM developers WHERE employee_id = %s", (employee_id,))
            if cur.fetchone():
                if "programming_language" in data["extra"]:
                    cur.execute("""
                        UPDATE developers SET programming_language = %s WHERE employee_id = %s
                    """, (data["extra"]["programming_language"], employee_id))
            else:
                cur.execute("SELECT 1 FROM managers WHERE employee_id = %s", (employee_id,))
                if cur.fetchone():
                    if "team_size" in data["extra"]:
                        cur.execute("""
                            UPDATE managers SET team_size = %s WHERE employee_id = %s
                        """, (data["extra"]["team_size"], employee_id))
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def delete_employee_native(employee_id: int) -> bool:
    conn = get_native_conn()
    cur = conn.cursor()
    
    try:
        # Сначала проверяем существование сотрудника
        cur.execute("SELECT id FROM employees WHERE id = %s", (employee_id,))
        if not cur.fetchone():
            return False
        
        # Удаляем записи в связанных таблицах
        # При ON DELETE CASCADE это не обязательно, но для порядка
        cur.execute("DELETE FROM developers WHERE employee_id = %s", (employee_id,))
        cur.execute("DELETE FROM managers WHERE employee_id = %s", (employee_id,))
        
        # Удаляем историю версий
        cur.execute("DELETE FROM employees_history WHERE employee_id = %s", (employee_id,))
        
        # Удаляем самого сотрудника
        cur.execute("DELETE FROM employees WHERE id = %s", (employee_id,))
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def get_history_native(employee_id: int) -> List[Dict]:
    conn, cur = get_native_cursor()
    
    try:
        # Сначала проверяем, существует ли сотрудник
        cur.execute("SELECT id FROM employees WHERE id = %s", (employee_id,))
        if not cur.fetchone():
            # Проверяем, есть ли история для этого сотрудника (даже если удалён)
            cur.execute("""
                SELECT version_id, version, name, department_id, is_current, changed_at
                FROM employees_history
                WHERE employee_id = %s
                ORDER BY version
            """, (employee_id,))
            rows = cur.fetchall()
            if rows:
                return [dict(row) for row in rows]
            return []
        
        cur.execute("""
            SELECT version_id, version, name, department_id, is_current, changed_at
            FROM employees_history
            WHERE employee_id = %s
            ORDER BY version
        """, (employee_id,))
        
        rows = cur.fetchall()
        return [dict(row) for row in rows]
    finally:
        cur.close()
        conn.close()

def get_tree_native() -> List[Dict]:
    conn, cur = get_native_cursor()
    
    try:
        cur.execute("SELECT id, name, parent_id FROM departments ORDER BY id")
        rows = cur.fetchall()
        
        items = [dict(row) for row in rows]
        return build_tree_native(items)
    finally:
        cur.close()
        conn.close()

def build_tree_native(items: List[Dict], parent_id: Optional[int] = None) -> List[Dict]:
    result = []
    for item in items:
        if item.get("parent_id") == parent_id:
            result.append({
                "id": item["id"],
                "name": item["name"],
                "children": build_tree_native(items, item["id"])
            })
    return result

def list_employees_native(department_id: Optional[int] = None) -> List[Dict]:
    conn, cur = get_native_cursor()
    
    try:
        if department_id:
            cur.execute("SELECT id FROM employees WHERE department_id = %s", (department_id,))
        else:
            cur.execute("SELECT id FROM employees")
        
        emp_ids = [row["id"] for row in cur.fetchall()]
        cur.close()
        conn.close()
        
        result = []
        for emp_id in emp_ids:
            emp = get_employee_native(emp_id)
            if emp:
                result.append(emp)
        return result
    finally:
        cur.close()
        conn.close()