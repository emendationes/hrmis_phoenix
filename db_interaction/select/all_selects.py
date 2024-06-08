from sqlalchemy.sql import text
from datetime import datetime

# Функция 1 "Просмотр статистики на главной странице"
# Функция 1.1 "для получения количества использованных выходных" (Holiday Used)
def get_holiday_entitlement(employee_id, cursor):
    # Получаем общее количество выходных часов
    total_hours = cursor.execute(
        text(f"SELECT holiday_entitlement_hours FROM holiday_entitlements WHERE employee_id = {employee_id}")
    ).first()
    total_hours = 0 if total_hours is None else total_hours[0]

    # Получаем использованное количество выходных часов
    used_hours = cursor.execute(
        text(f"""
        SELECT COALESCE(SUM((hd.date_end - hd.date_start + 1) * 24), 0) as used_hours
        FROM holidays h
        JOIN holiday_date hd ON h.id = hd.holiday_id
        WHERE extract(year from hd.date_end) = extract(year from CURRENT_DATE) and h.employee_id = {employee_id} AND h.approved = TRUE
        """)
    ).first()

    return total_hours, used_hours

# Функция 1.2 "для получения названий предстоящих выходных" (Upcoming)
def get_upcoming_holidays(employee_id, cursor):
    result = cursor.execute(
        text(f"""
        SELECT h.name, hd.date_start
        FROM holidays h
        JOIN holiday_date hd ON h.id = hd.holiday_id
        WHERE h.employee_id = {employee_id} AND hd.date_start >= CURRENT_DATE
        ORDER BY hd.date_start ASC
        LIMIT 1
        """)
    ).first()
    return result if result else ("No upcoming holidays", None)

# Функция 1.3 "для получения исходящих запросов на выходные" (Requests)
def get_holiday_requests(employee_id, cursor):
    requests = cursor.execute(
        text(f"""
        SELECT name, approved, cancelled, disapproval_reason
        FROM holidays
        WHERE employee_id = {employee_id} 
        """)
    )
    return requests

# Функция 1.4 "для получения дней рождения всех сотрудников" (Anniversaries - Birthdays)
def get_birthdays(cursor):
    birthdays = cursor.execute(
        text("""SELECT users.full_name, employees.date_of_birth FROM employees
        JOIN users on employees.id = users.id""")
    ).all()
    return [{"full_name": row[0], "date_of_birth": row[1]} for row in birthdays]

# Функция 1.5 "для получения периодов работы всех сотрудников" (Anniversaries - Service)
def get_work_periods(cursor):
    periods = cursor.execute(
        text("""SELECT users.full_name, employees.service_start_day, employees.service_end_day FROM employees
        JOIN users on employees.id = users.id""")
    )
    return [{"full_name": row[0], "service_start_day": row[1], "service_end_day": row[2]} for row in periods]


# Функция 2 "Просмотр личной информации"
# Функция 2.1 "Просмотр общей информации"
def get_user_info(employee_id, cursor):
    result = cursor.execute(
        text(f"SELECT full_name, email, role_id, password_reset_token FROM users WHERE id = {employee_id}")
    ).first()
    return result if result else ("No data", "No data", "No data", "No data", employee_id)

# Функция 2.2 "Просмотр рабоче-профессиональной информации"
def get_professional_info(employee_id, cursor):
    result = cursor.execute(
        text(f"""
        SELECT 
            e.reference, 
            u.full_name AS manager_name,
            d.title AS department_title,
            jr.name AS job_role_name,
            e.date_of_birth,
            e.service_start_day,
            e.service_end_day,
            e.profile_file_name,
            p.name,
            p.id
        FROM employees e
        LEFT JOIN employees m ON e.manager_id = m.id
        LEFT JOIN projects p ON e.project_id = p.id
        LEFT JOIN users u ON m.id = u.id
        LEFT JOIN departments d ON e.department_id = d.id
        LEFT JOIN job_roles jr ON e.job_role_id = jr.id
        WHERE e.id = {employee_id}
        """)
    ).first()
    if result:
        return {
            "Reference": result[0],
            "Manager": result[1],
            "Department": result[2],
            "Job Role": result[3],
            "Date of Birth": result[4],
            "Service Start Day": result[5],
            "Service End Day": result[6],
            "Profile Image": result[7],
            "Project": result[8] if result[8] else "No project",
            "Project_ID": result[9] if result[9] else "No project"
        }
    else:
        return "No professional information available"
    
# Функция 2.3 "Просмотр контактной информации"
def get_contact_info(employee_id, cursor):
    result = cursor.execute(
        text(f"""
        SELECT 
            e.line, 
            e.city, 
            e.region, 
            e.postal_code,
            c.id as country_id, 
            c.name AS country_name, 
            e.mobile_number
        FROM employees e
        LEFT JOIN countries c ON e.country_id = c.id
        WHERE e.id = {employee_id}
        """)
    ).first()
    if result:
        return {
            "Address Line": result[0],
            "City": result[1],
            "Region/State/Province": result[2],
            "Postal/Zip Code": result[3],
            "Country_ID": result[4],
            "Country": result[5],
            "Mobile Phone": result[6]
        }
    else:
        return {
            "Address Line": "No address line",
            "City": "No city",
            "Region/State/Province": "No region/state/province",
            "Postal/Zip Code": "No postal/zip code",
            "Country_ID": -1,
            "Country": "No country",
            "Mobile Phone": "No mobile phone"
        }
    
# Функция 2.4 "Просмотр рабочих часов"
def get_working_hours(employee_id, cursor):
    result = cursor.execute(
        text(f"""
        SELECT 
            monday_start, monday_end,
            tuesday_start, tuesday_end,
            wednesday_start, wednesday_end,
            thursday_start, thursday_end,
            friday_start, friday_end,
            saturday_start, saturday_end,
            sunday_start, sunday_end
        FROM employees
        WHERE id = {employee_id}
        """)
    ).first()
    if result:
        return {
            "Monday": {"Start": result[0], "End": result[1]},
            "Tuesday": {"Start": result[2], "End": result[3]},
            "Wednesday": {"Start": result[4], "End": result[5]},
            "Thursday": {"Start": result[6], "End": result[7]},
            "Friday": {"Start": result[8], "End": result[9]},
            "Saturday": {"Start": result[10], "End": result[11]},
            "Sunday": {"Start": result[12], "End": result[13]}
        }
    else:
        return "No working hours information available"

# Функция 2.5 "Просмотр общего количества выходных"
def get_holiday_entitlements(employee_id, cursor):
    results = cursor.execute(
        text(f"""
        SELECT cy.id, cy.title, he.holiday_entitlement_hours
        FROM holiday_entitlements he
        JOIN company_years cy ON he.company_year_id = cy.id
        WHERE he.employee_id = {employee_id}
        ORDER BY cy.year_start
        """)
    )
    return [{"Financial Year_ID": row[0], "Financial Year": row[1], "Holiday Hours": row[2]} for row in results] if results else []

# Функция 3 "Просмотр общего списка сотрудников по отделам"
def get_employees_by_department(cursor):
    results = cursor.execute(
        text(f"""
        SELECT 
            d.title AS department,
            pd.title AS parent_department,
            u.full_name
        FROM departments d
        LEFT JOIN departments pd ON d.parent_id = pd.id
        LEFT JOIN employees e ON d.id = e.department_id
        LEFT JOIN users u ON e.id = u.id
        ORDER BY d.title, pd.title
        """)
    )
    return [{"Department": row[0], "Parent Department": row[1], "Employee Name": row[2]} for row in results]

# Функция 4 "Просмотр собственного списка пропусков"
def get_personal_absences(employee_id, cursor):
    results = cursor.execute(
        text(f"""
        SELECT 
            cy.title,
            a.date_start,
            a.date_end,
            a.authorized,
            a.cancelled,
            a.unauthorize_reason,
            a.id
        FROM absences a
        JOIN company_years cy ON a.company_year_id = cy.id
        WHERE a.employee_id = {employee_id}
        ORDER BY cy.year_start, a.date_start
        """)
    )
    return [{
        "Financial Year": row[0],
        "Start Date": row[1].strftime('%Y-%m-%d'),
        "End Date": row[2].strftime('%Y-%m-%d'),
        "Authorized": row[3],
        "Cancelled": row[4],
        "Unauthorize Reason": row[5] if row[4] else "N/A",  # Причина отказа показывается только если есть отказ
        "ID": row[6]
    } for row in results]

# Функция 5 "Просмотр собственного списка запросов на выходные"
def get_personal_holidays(employee_id, cursor):
    results = cursor.execute(
        text(f"""
        SELECT 
            h.name,
            cy.title,
            hd.date_start,
            hd.date_end,
            h.approved,
            h.cancelled,
            h.disapproval_reason
        FROM holidays h
        JOIN company_years cy ON h.company_year_id = cy.id
        JOIN holiday_date hd ON h.id = hd.holiday_id
        WHERE h.employee_id = {employee_id}
        ORDER BY cy.year_start, hd.date_start
        """)
    )
    return [{
        "Name": row[0],
        "Financial Year": row[1],
        "Start Date": row[2].strftime('%Y-%m-%d'),
        "End Date": row[3].strftime('%Y-%m-%d'),
        "Approved": row[4],
        "Cancelled": row[5],
        "Disapproval Reason": row[6] if row[5] else "N/A"  # Показываем причину отказа только если запрос отклонён
    } for row in results]

# Функция 6 "Просмотр списка запросов подчинённых на выходные"
def get_subordinate_holidays(manager_id, cursor):
    results = cursor.execute(
        text(f"""
        SELECT 
            u.full_name,
            cy.title,
            hd.id,
            hd.date_start,
            hd.date_end,
            h.approved,
            h.cancelled,
            h.disapproval_reason
        FROM employees m
        JOIN employees w ON w.manager_id = m.id
        JOIN holidays h ON w.id = h.employee_id
        JOIN company_years cy ON h.company_year_id = cy.id
        JOIN holiday_date hd ON h.id = hd.holiday_id
        JOIN users u ON u.id = w.id
        WHERE m.id = {manager_id}
        ORDER BY u.full_name, cy.year_start, hd.date_start
        """)
    )
    return [{
        "Employee Name": row[0],
        "Financial Year": row[1],
        "Holiday ID": row[2],
        "Start Date": row[3].strftime('%Y-%m-%d'),
        "End Date": row[4].strftime('%Y-%m-%d'),
        "Approved": row[5],
        "Cancelled": row[6],
        "Disapproval Reason": row[7] if row[6] else "N/A"  # Причина отказа показывается только если запрос отклонён
    } for row in results]

# Функция 7 "Просмотр списка запросов подчинённых на пропуски"
def get_subordinate_absences(manager_id, cursor):
    results = cursor.execute(
        text(f"""
        SELECT 
            u.full_name,
            cy.title,
            a.id,
            a.date_start,
            a.date_end,
            a.authorized,
            a.cancelled,
            a.unauthorize_reason,
            a.reason
        FROM employees m
        JOIN employees w ON w.manager_id = m.id
        JOIN absences a ON w.id = a.employee_id
        JOIN company_years cy ON a.company_year_id = cy.id
        JOIN users u ON u.id = w.id
        WHERE m.id = {manager_id}
        ORDER BY u.full_name, cy.year_start, a.date_start
        """)
    )
    return [{
        "Employee Name": row[0],
        "Financial Year": row[1],
        "ID": row[2],
        "Start Date": row[3].strftime('%Y-%m-%d'),
        "End Date": row[4].strftime('%Y-%m-%d'),
        "Authorized": row[5],
        "Cancelled": row[6],
        "Disapproval Reason": row[7] if row[6] else "N/A",
        "Reason": row[8],
    } for row in results]

def get_attachments_details_for_absence(abs_id,cursor):
    result = cursor.execute(text(f"SELECT id,title,file_name FROM attachments WHERE absence_id = {abs_id};")).all()
    return [{"id":row[0],"title":row[1],"path":row[2].split('/')[-1]}for row in result]

# Функция 8 "Просмотр списка рабочих должностей"
def get_projects(cursor):
    results = cursor.execute(
        text("SELECT name, description FROM projects ORDER BY name")
    )
    return [{"name": row[0], "description": row[1]} for row in results]

# Функция 9 "Просмотр списка отделов"
def get_departments(cursor):
    results = cursor.execute(
        text("SELECT a.title, b.title FROM departments a LEFT JOIN departments b ON b.id=a.parent_id ORDER BY a.title")
    )
    return [{"Department Name": row[0], "Parent Department": row[1]} for row in results]

# Функция 10 "Просмотр списка финансовых годов (лет)"
def get_financial_years(cursor):
    results = cursor.execute(
        text("SELECT title, year_start, year_end FROM company_years ORDER BY year_start")
    )
    return [{
        "title": row[0],
        "start_date": row[1].strftime('%Y-%m-%d'),
        "end_date": row[2].strftime('%Y-%m-%d')
    } for row in results]

# ПодФункции для выбора даты начала и даты конца по id года (для пропусков и выходных)
def get_financial_year_dates_for_holidays(cursor, id):
    results = cursor.execute(
        text(f"SELECT greatest(CURRENT_DATE, year_start), year_end FROM company_years WHERE id = { id }")
        ).first()
    return { "min": results[0].strftime('%Y-%m-%d'), "max": results[1].strftime('%Y-%m-%d'), "id":id}

def get_financial_years_for_absences(cursor, id):
    results = cursor.execute(
        text(f"SELECT year_start, least(CURRENT_DATE, year_end) FROM company_years WHERE id = { id }")
        ).first()
    return { "min": results[0].strftime('%Y-%m-%d'), "max": results[1].strftime('%Y-%m-%d'), "id":id}


# Функция 11 "Просмотр списка рабочих должностей"
def get_job_roles(cursor):
    results = cursor.execute(
        text("SELECT name, description FROM job_roles ORDER BY name")
    )
    return [{"name": row[0], "description": row[1]} for row in results]

# Функция 12 "Просмотр списка рабочих должностей"
def get_projects(cursor):
    results = cursor.execute(
        text("SELECT name, description FROM projects ORDER BY name")
    )
    return [{"name": row[0], "description": row[1]} for row in results]


# Функция 13 "Просмотр списка сотрудников"
def get_employees(cursor):
    results = cursor.execute(
        text("""
        SELECT
            u.id, 
            u.full_name,
            r.name AS role_name,
            c.name AS country_name,
            d.title AS department_title,
            p.name AS project_name
        FROM employees e
        JOIN users u ON e.id = u.id
        LEFT JOIN projects p ON p.id = e.project_id
        LEFT JOIN roles r ON u.role_id = r.id
        LEFT JOIN countries c ON e.country_id = c.id
        LEFT JOIN departments d ON e.department_id = d.id
        GROUP BY u.id, u.full_name, r.name, c.name, d.title, p.name
        ORDER BY u.full_name
        """)
    )
    return [{
        "id": row[0],
        "Full Name": row[1],
        "Role": row[2] or "No role assigned",
        "Country": row[3] or "No country assigned",
        "Department": row[4] or "No department assigned",
        "Project": row[5] or "No project assigned"
    } for row in results]


# Функция 14 "Просмотр профиля со страницы иерархии"
def get_user_general_data(employee_id, cursor):
    result = cursor.execute(
        text(f"""SELECT 
            e.profile_file_name,   -- Файл профиля сотрудника
            u.full_name,           -- Полное имя пользователя
            jr.name AS job_role_name,  -- Название должности
            u.email,               -- Электронная почта пользователя
            e.mobile_number        -- Мобильный номер сотрудника
        FROM employees e
        JOIN users u ON e.id = u.id
        LEFT JOIN job_roles jr ON e.job_role_id = jr.id
        WHERE e.id = { employee_id }
    """)
    ).first()
    return {
            "Profile File Name": result[0],
            "Full Name": result[1],
            "Job Role": result[2],
            "Email": result[3],
            "Mobile Number": result[4]
        }


# Мини-функция 13 "Просмотреть список менеджеров"
def get_all_user_names(cursor):
    results = cursor.execute(
        text("SELECT id, full_name FROM users ORDER BY full_name")
    )
    return [{"id": row[0], "name": row[1]} for row in results]

# Мини-функция 14 "Просмотреть список отделов"
def get_department_names(cursor):
    results = cursor.execute(
        text("SELECT id, title FROM departments ORDER BY title")
    )
    return [{"id": row[0], "title": row[1]} for row in results]

# Мини-функция 15 "Просмотреть список должностей"
def get_job_role_names(cursor):
    results = cursor.execute(
        text("SELECT id, name FROM job_roles ORDER BY id")
    )
    return [{"id": row[0], "name": row[1]} for row in results]

# Мини-функция 16 "Просмотреть список проектов"
def get_project_names(cursor):
    results = cursor.execute(
        text("SELECT id, name FROM projects ORDER BY name")
    )
    return [{"id": row[0], "name": row[1]} for row in results]

# Мини-функция 17 "Просмотреть список стран"
def get_country_names(cursor):
    results = cursor.execute(
        text("SELECT id, name FROM countries ORDER BY name")
    )
    return [{"id": row[0], "name": row[1]} for row in results]

# Мини-функция 18 "Просмотреть список годов (лет)"
def get_financial_year_titles(cursor):
    results = cursor.execute(
        text("SELECT id, title FROM company_years ORDER BY year_start")
    )
    return [{"id": row[0], "title": row[1]} for row in results]

# Мини-функция 19 "Просмотреть список ролей"
def get_role_names(cursor):
    results = cursor.execute(
        text("SELECT id, name FROM roles ORDER BY name")
    )
    return [{"id": row[0], "name": row[1]} for row in results]

# Мини функция для приема дат и возвращения company_year для этой даты
def get_date(date, cursor):
    results = cursor.execute(
        text(f"SELECT id FROM company_years WHERE TO_DATE('{date}', 'YYYY-MM-DD') >= year_start AND TO_DATE('{date}', 'YYYY-MM-DD') <= year_end")
    ).first()
    return results[0]

# # 
def get_department_and_employees_united(cursor):
    depart_data = cursor.execute(text(f"SELECT id, title, parent_id from departments")).all()
    employee_data = cursor.execute(text(f"SELECT users.id, full_name, department_id from users JOIN employees on employees.id = users.id")).all()
    return parse_query(depart_data, employee_data)

def parse_query(db_data:list,employee_info:list):
    data = {}
    for i,db_item in enumerate(db_data):
        data[db_item[0]] = {'id':db_item[0],'title':db_item,'parent_id':db_item[2] if db_item[2] is not None else -1,'children':[],'employees':[]}
    for i,fill_item in enumerate(db_data):
        if fill_item[2] is not None:
            data[fill_item[2]]['children'].append(fill_item[0])
    for emp in employee_info:
        if emp[2] is not None:
            data[emp[2]]['employees'].append({'emp_id':emp[0],'emp_name':emp[1]})
    return data
  
# # 
def validate_times(times):
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    for day in days:
        start_time = times.get(f'{day}_start')
        end_time = times.get(f'{day}_end')
        if start_time and end_time:
            start = datetime.strptime(start_time, ('%H:%M' if start_time.count(':')==1 else '%H:%M:%S')).time()
            end = datetime.strptime(end_time, ('%H:%M' if end_time.count(':')==1 else '%H:%M:%S')).time()
            if start >= end:
                return False
    return True

# Мини функция, которая принимает епмлое ид и возвращает список лет из бд
def get_financial_year_titles_for_empl_entitlement(cursor, employee_id):
    # Формируем SQL-запрос с учетом id сотрудника
    result = cursor.execute(text(f"""
        (SELECT id, title 
         FROM company_years 
         WHERE year_end > CURRENT_DATE)
        EXCEPT
        (SELECT cy.id, cy.title 
         FROM holiday_entitlements he 
         JOIN company_years cy ON cy.id = he.company_year_id
         WHERE he.employee_id = { employee_id })
        ORDER BY id
    """))

    return [{"id": row[0], "title": row[1]} for row in result]

def get_privileges(cursor):
    result = cursor.execute(text(f"SELECT p.id, p.spec_word FROM privilege p ")).all()
    res = {}
    for row in result:
        res[row[1]] = row[0]
    return res

def get_words_for_roles(cursor):
    result = cursor.execute(text(f"""SELECT r.id , COALESCE(SUM(rp.privilege_id), 0) from roles r 
                                 LEFT JOIN role_privileges rp ON rp.role_id = r.id
                                 GROUP BY r.id;""")).all()
    res = {}
    for row in result:
        res[row[0]] = row[1]
    return res