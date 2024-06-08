from sqlalchemy.sql import text
from dec import custom_error_handler

# Функция 1 "Создать запрос на выходные" (в самой форме будут поля "Название", "Финансовый период (можно только выбрать из уже существующих), "дата начала" и "дата конца")
@custom_error_handler
def create_holiday(name, company_year_id, start_date, end_date, employee_id, cursor):
    # Вставка в holidays
    holiday_id = cursor.execute(
        text(f"INSERT INTO holidays (name, approved, cancelled, company_year_id, employee_id) VALUES ('{name}', {False}, {False}, {company_year_id}, {employee_id}) RETURNING id")
        ).first()[0]

    # Вставка в holiday_date
    cursor.execute(
        text(f"INSERT INTO holiday_date (date_start, date_end, holiday_id) VALUES (TO_DATE('{start_date}','YYYY-MM-DD'), TO_DATE('{end_date}','YYYY-MM-DD'), {holiday_id})")
    )

# Функция 2 "Создать запрос на пропуск" (в самой форме будут поля "Причина", "Продолжительность, "Attachment")
@custom_error_handler
def create_absence(reason, start_date, end_date, company_year_id, employee_id, cursor):
    # Вставка в absences
    absence_id = cursor.execute(
        text(f"INSERT INTO absences (authorized, cancelled, date_start, date_end, reason, company_year_id, employee_id) VALUES ({False}, {False}, TO_DATE('{start_date}','YYYY-MM-DD'), TO_DATE('{end_date}','YYYY-MM-DD'), '{reason}', {company_year_id}, {employee_id}) RETURNING id")
    ).first()[0]

    return absence_id

@custom_error_handler
def create_attachments_for_abs_note(note_id,attachment_vocab,cursor):
    req = "INSERT INTO attachments (title,file_name,absence_id) VALUES "
    max_ind = len(list(attachment_vocab.items()))-1
    for i,(title,(file_name,*f)) in enumerate(attachment_vocab.items()):
        req += f"('{title}','{file_name}',{note_id})"+("," if i !=max_ind else " ")
    req += "RETURNING id"
    res = len(list(cursor.execute(text(req)).all()))
    return res

# Функция 3 "Создать новый проект"
@custom_error_handler
def create_project(name, description, cursor):
    cursor.execute(
        text(f"INSERT INTO projects (name, description) VALUES ('{name}', '{description}')")
    )


# Функция 4 "Создать новый отдел"
@custom_error_handler
def create_department(title, cursor, parent_id = ""):
    if parent_id is not "":  # Если есть старший отдел
        cursor.execute(
            text(f"INSERT INTO departments (title, parent_id) VALUES ('{title}', {parent_id})")
        )
    else:  # Если старший отдел не указан
        cursor.execute(
            text(f"INSERT INTO departments (title) VALUES ('{title}')")
        )


# Функция 5 "Создать новый рабочий/финансовый год"
@custom_error_handler
def create_company_year(user_title, year, cursor):
    year_start = f"{year}-01-01"  # Первый день года
    year_end = f"{year}-12-31"    # Последний день года

    cursor.execute(
        text(f"INSERT INTO company_years (title, year_start, year_end) VALUES ('{user_title}', TO_DATE('{year_start}', 'YYYY-MM-DD'), TO_DATE('{year_end}', 'YYYY-MM-DD'))")
    )

# Функция 6 "Создать новую должность"
@custom_error_handler
def create_job_role(name, description, cursor):
    cursor.execute(
        text(f"INSERT INTO job_roles (name, description) VALUES ('{name}', '{description}')")
    )

# Функция 7 "Создать нового пользователя"
@custom_error_handler
def create_user(email, full_name, username, roles, cursor):
    user_id = cursor.execute(
        text(f"INSERT INTO users (email, full_name, username, password, password_reset_token, expiry, role_id) VALUES ('{email}', '{full_name}', '{username}', '$2b$12$hjgCihf19pzQZX5oqK2VUub3Rl/gjkebk/K6kfmdldRBMhpA1cJgC', 'reset_pass_{username}', NULL, {roles}) RETURNING id")
    ).first()[0]

# Функция 8 "Создать общее количество выходных"
@custom_error_handler
def add_holiday_entitlements(employee_id, new_year_id, new_hours, cursor):
    cursor.execute(
        text(f"""
        INSERT INTO holiday_entitlements (holiday_entitlement_hours, employee_id, company_year_id)
        VALUES ({ new_hours }, { employee_id }, { new_year_id })
        """)
    )


@custom_error_handler
def create_attachment(filename,cursor):
    result = cursor.execute(text(f"INSERT"))
    return result[0]