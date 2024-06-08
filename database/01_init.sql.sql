-- Creating table for job roles
CREATE TABLE job_roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    description VARCHAR(500)
);

-- Creating table for departments
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    parent_id INTEGER REFERENCES departments(id) ON DELETE SET NULL
);

-- Creating table for projects
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    description VARCHAR(500)
);

-- Creating table for roles
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255)
);

-- Creating table for users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    full_name VARCHAR(255),
    username VARCHAR(255),
    password VARCHAR(255),
    password_reset_token VARCHAR(255),
    expiry TIMESTAMP,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    UNIQUE (username)
);

-- Creating table for countries
CREATE TABLE countries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255)
);

-- Creating table for employees
CREATE TABLE employees (
    id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    city VARCHAR(255),
    line VARCHAR(255),
    postal_code VARCHAR(255),
    region VARCHAR(255),
    date_of_birth DATE,
    monday_start TIME,
    monday_end TIME,
    tuesday_start TIME,
    tuesday_end TIME,
    wednesday_start TIME,
    wednesday_end TIME,
    thursday_start TIME,
    thursday_end TIME,
    friday_start TIME,
    friday_end TIME,
    saturday_start TIME,
    saturday_end TIME,
    sunday_start TIME,
    sunday_end TIME,
    mobile_number VARCHAR(255),
    profile_file_name VARCHAR(255),
    reference VARCHAR(255),
    service_start_day DATE,
    service_end_day DATE,
    country_id INTEGER REFERENCES countries(id) ON DELETE SET NULL,
    department_id INTEGER REFERENCES departments(id) ON DELETE SET NULL,
    job_role_id INTEGER REFERENCES job_roles(id) ON DELETE SET NULL,
    project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL,
    manager_id INTEGER REFERENCES employees(id) ON DELETE SET NULL
);

-- Creating table for company years
CREATE TABLE company_years (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    year_start DATE,
    year_end DATE
);

-- Creating table for absences
CREATE TABLE absences (
    id SERIAL PRIMARY KEY,
    authorized BOOLEAN,
    cancelled BOOLEAN,
    date_start DATE,
    date_end DATE,
    reason TEXT,
    unauthorize_reason VARCHAR(255),
    company_year_id INTEGER REFERENCES company_years(id) ON DELETE CASCADE,
    employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE
);

-- Creating table for attachments
CREATE TABLE attachments (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    file_name VARCHAR(255),
    absence_id INTEGER REFERENCES absences(id) ON DELETE CASCADE
);

-- Creating table for holiday entitlements
CREATE TABLE holiday_entitlements (
    id SERIAL PRIMARY KEY,
    holiday_entitlement_hours DECIMAL(8,4),
    company_year_id INTEGER REFERENCES company_years(id) ON DELETE CASCADE,
    employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
    UNIQUE (employee_id, company_year_id)
);

-- Creating table for holidays
CREATE TABLE holidays (
    id SERIAL PRIMARY KEY,
    approved BOOLEAN,
    cancelled BOOLEAN,
    disapproval_reason VARCHAR(255),
    name VARCHAR(255),
    company_year_id INTEGER REFERENCES company_years(id) ON DELETE CASCADE,
    employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE
);

-- Creating table for holiday_date
CREATE TABLE holiday_date (
    id SERIAL PRIMARY KEY,
    date_start DATE,
    date_end DATE,
    holiday_id INTEGER REFERENCES holidays(id) ON DELETE CASCADE
);

-- Creating table for privilege
CREATE TABLE privilege (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    spec_word VARCHAR(255)
);

-- Creating table for role_privileges
CREATE TABLE role_privileges (
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    privilege_id INTEGER REFERENCES privilege(id) ON DELETE CASCADE,
    UNIQUE (role_id, privilege_id)
);


-- Create trigger when create user then also automatically create employee
-- Создание функции триггера
CREATE OR REPLACE FUNCTION create_employee_for_user()
RETURNS TRIGGER AS $$
BEGIN
    -- Вставка пустой записи в таблицу employees
    -- Используется NEW для доступа к значениям только что вставленной записи в users
    INSERT INTO employees (id)
    VALUES (NEW.id);
    
    -- Возвращаем новую запись для успешного завершения триггера
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Создание триггера
CREATE TRIGGER trigger_create_employee
AFTER INSERT ON users
FOR EACH ROW
EXECUTE FUNCTION create_employee_for_user();

-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- ДВОИЧНАЯ СС ДЛЯ РОЛЕЙ, ПРИВИЛЕГЙИ И Т.Д.-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 

CREATE OR REPLACE FUNCTION replace_id_with_power_of_two() RETURNS TRIGGER AS $$
BEGIN
    -- Заменяем id на 2 в степени исходного id
    NEW.id := 2 ^ NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER before_insert_privilege
BEFORE INSERT ON privilege
FOR EACH ROW EXECUTE FUNCTION replace_id_with_power_of_two();

-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- КОНЕЦ-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 



-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- ОБНОВЛЕНИЕ ТОКЕНА ПРИ ВОССТАНОВЛЕНИИ ПАРОЛЯ-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
CREATE OR REPLACE PROCEDURE update_password_reset_token(user_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE users
    SET password_reset_token = md5(random()::text || clock_timestamp()::text)
    WHERE id = user_id;
END;
$$;
-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- КОНЕЦ-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 

