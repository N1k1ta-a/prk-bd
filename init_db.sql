-- Создание базы данных (выполнить в psql: CREATE DATABASE practice;)
-- \c practice;

-- Иерархия: отделы (предок-потомок)
CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    parent_id INTEGER REFERENCES departments(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Наследование (Table per Type)
-- Базовая сущность: сотрудник
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Наследник: разработчик
CREATE TABLE IF NOT EXISTS developers (
    employee_id INTEGER PRIMARY KEY REFERENCES employees(id) ON DELETE CASCADE,
    programming_language TEXT NOT NULL
);

-- Наследник: менеджер
CREATE TABLE IF NOT EXISTS managers (
    employee_id INTEGER PRIMARY KEY REFERENCES employees(id) ON DELETE CASCADE,
    team_size INTEGER NOT NULL CHECK (team_size >= 0)
);

-- Версионирование (для сотрудников)
CREATE TABLE IF NOT EXISTS employees_history (
    version_id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL,
    version INTEGER NOT NULL,
    name TEXT NOT NULL,
    department_id INTEGER,
    is_current BOOLEAN DEFAULT TRUE,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для производительности
CREATE INDEX IF NOT EXISTS idx_departments_parent ON departments(parent_id);
CREATE INDEX IF NOT EXISTS idx_employees_department ON employees(department_id);
CREATE INDEX IF NOT EXISTS idx_employees_history_employee ON employees_history(employee_id);
CREATE INDEX IF NOT EXISTS idx_employees_history_current ON employees_history(employee_id, is_current);

-- Функция для первой версии (при INSERT)
CREATE OR REPLACE FUNCTION first_version_employee()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO employees_history (employee_id, version, name, department_id, is_current)
    VALUES (NEW.id, 1, NEW.name, NEW.department_id, TRUE);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Функция для новой версии (при UPDATE)
CREATE OR REPLACE FUNCTION version_employee()
RETURNS TRIGGER AS $$
DECLARE
    next_version INTEGER;
BEGIN
    SELECT COALESCE(MAX(version), 0) + 1 INTO next_version
    FROM employees_history
    WHERE employee_id = NEW.id;
    
    UPDATE employees_history 
    SET is_current = FALSE 
    WHERE employee_id = NEW.id AND is_current = TRUE;
    
    INSERT INTO employees_history (employee_id, version, name, department_id, is_current)
    VALUES (NEW.id, next_version, NEW.name, NEW.department_id, TRUE);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггеры
DROP TRIGGER IF EXISTS trg_first_version_employee ON employees;
CREATE TRIGGER trg_first_version_employee
AFTER INSERT ON employees
FOR EACH ROW
EXECUTE FUNCTION first_version_employee();

DROP TRIGGER IF EXISTS trg_version_employee ON employees;
CREATE TRIGGER trg_version_employee
AFTER UPDATE ON employees
FOR EACH ROW
EXECUTE FUNCTION version_employee();

-- Начальные данные (отделы)
INSERT INTO departments (name, parent_id) VALUES
    ('ИТ', NULL),
    ('Разработка', 1),
    ('Тестирование', 1),
    ('Управление', NULL),
    ('HR', 4)
ON CONFLICT DO NOTHING;
