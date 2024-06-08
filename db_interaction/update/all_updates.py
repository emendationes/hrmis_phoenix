from sqlalchemy.sql import text
from dec import custom_error_handler

# Функция 1.1 "Отказать в пропуске" 
@custom_error_handler
def reject_absence(absence_id, reason, cursor):
    cursor.execute(
        text(f"UPDATE absences SET cancelled = TRUE, unauthorize_reason = '{reason}' WHERE id = {absence_id}")
    )

# Функция 1.2 "Согласовать пропуск" 
@custom_error_handler
def approve_absence(absence_id, cursor):
    cursor.execute(
        text(f"UPDATE absences SET authorized = TRUE WHERE id = {absence_id}")
    )


# Функция 2.1 "Отказать в выходных" 
@custom_error_handler
def reject_holiday(holiday_id, reason, cursor):
    cursor.execute(
        text(f"UPDATE holidays SET cancelled = TRUE, disapproval_reason = '{reason}' WHERE id = {holiday_id}")
    )

# Функция 2.2 "Согласовать выходные" 
@custom_error_handler
def approve_holiday(holiday_id, cursor):
    cursor.execute(
        text(f"UPDATE holidays SET approved = TRUE WHERE id = {holiday_id}")
    )

# Функция 3 "Изменение личной информации"
# Функция 3.1 "Изменение общей информации"
@custom_error_handler
def update_user_info(employee_id, new_full_name, new_email, new_role, cursor):
    # Обновление основной информации пользователя
    cursor.execute(
        text(f"UPDATE users SET role_id = { new_role }, full_name = '{ new_full_name }', email = '{ new_email }' WHERE id = { employee_id }")
    )


# Функция 3.2 "Изменение рабоче-профессиональной информации"
@custom_error_handler
def update_professional_info_w_pic(employee_id, new_reference, new_manager_id, new_department_id, new_job_role_id, new_project_id, new_date_of_birth, new_service_start, new_profile_file, cursor):
    cursor.execute(
        text(f"""
        UPDATE employees 
        SET reference = '{ new_reference }', 
        manager_id = { new_manager_id if new_manager_id != -1 else 'NULL' }, 
        department_id = { new_department_id if new_department_id != -1 else 'NULL' }, 
        job_role_id = { new_job_role_id if new_job_role_id != -1 else 'NULL' }, 
        project_id = { new_project_id if new_project_id != -1 else 'NULL'},
        date_of_birth = TO_DATE('{ new_date_of_birth }','YYYY-MM-DD'), 
        service_start_day = TO_DATE('{ new_service_start }','YYYY-MM-DD'), 
        profile_file_name = '{ new_profile_file }'
        WHERE id = { employee_id }
        """)
    )

@custom_error_handler
def update_professional_info_no_pic(employee_id, new_reference, new_manager_id, new_department_id, new_job_role_id, new_project_id, new_date_of_birth, new_service_start, cursor):
    cursor.execute(
        text(f"""
        UPDATE employees 
        SET reference = '{ new_reference }', 
        manager_id = { new_manager_id if new_manager_id != -1 else 'NULL' }, 
        department_id = { new_department_id if new_department_id != -1 else 'NULL' }, 
        job_role_id = { new_job_role_id if new_job_role_id != -1 else 'NULL' }, 
        project_id = { new_project_id if new_project_id != -1 else 'NULL'},
        date_of_birth = { f"TO_DATE('{ new_date_of_birth }','YYYY-MM-DD')" if new_date_of_birth != 'NULL' else 'NULL'}, 
        service_start_day = { f"TO_DATE('{ new_service_start }','YYYY-MM-DD')" if new_service_start != 'NULL' else 'NULL'}
        WHERE id = { employee_id }
        """)
    )

    # Подфункция "Уволить сотрудника (По нажатию на кнопку дата увольнения становится "сегодняшний день")"
@custom_error_handler
def fire_employee(employee_id, cursor):
        cursor.execute(
        text(f"""
        UPDATE employees 
        SET service_end_day = CURRENT_DATE
        WHERE id = { employee_id }
        """)
    )
    
# Функция 3.3 "Изменение контактной информации"
@custom_error_handler
def update_contact_info(employee_id, new_line, new_city, new_region, new_postal_code, new_country_id, new_mobile_number, cursor):
    cursor.execute(
        text(f"""
        UPDATE employees 
        SET line = '{ new_line }',
        city = '{ new_city }', 
        region = '{ new_region }', 
        postal_code = '{ new_postal_code }', 
        country_id = { new_country_id }, 
        mobile_number = '{ new_mobile_number }'
        WHERE id = { employee_id }
        """)
    )
    
# Функция 3.4 "Изменение рабочих часов"
@custom_error_handler
def update_working_hours(employee_id, new_schedule, cursor):
    query = text(f"""
        UPDATE employees 
        SET monday_start = {f"'{new_schedule['monday_start']}'::time" if new_schedule['monday_start'] is not None else 'NULL'}, 
            monday_end = {f"'{new_schedule['monday_end']}'::time" if new_schedule['monday_end'] is not None else 'NULL'}, 
            tuesday_start = {f"'{new_schedule['tuesday_start']}'::time" if new_schedule['tuesday_start'] is not None else 'NULL'}, 
            tuesday_end = {f"'{new_schedule['tuesday_end']}'::time" if new_schedule['tuesday_end'] is not None else 'NULL'}, 
            wednesday_start = {f"'{new_schedule['wednesday_start']}'::time" if new_schedule['wednesday_start'] is not None else 'NULL'}, 
            wednesday_end = {f"'{new_schedule['wednesday_end']}'::time" if new_schedule['wednesday_end'] is not None else 'NULL'}, 
            thursday_start = {f"'{new_schedule['thursday_start']}'::time" if new_schedule['thursday_start'] is not None else 'NULL'}, 
            thursday_end = {f"'{new_schedule['thursday_end']}'::time" if new_schedule['thursday_end'] is not None else 'NULL'}, 
            friday_start = {f"'{new_schedule['friday_start']}'::time" if new_schedule['friday_start'] is not None else 'NULL'}, 
            friday_end = {f"'{new_schedule['friday_end']}'::time" if new_schedule['friday_end'] is not None else 'NULL'}, 
            saturday_start = {f"'{new_schedule['saturday_start']}'::time" if new_schedule['saturday_start'] is not None else 'NULL'}, 
            saturday_end = {f"'{new_schedule['saturday_end']}'::time" if new_schedule['saturday_end'] is not None else 'NULL'}, 
            sunday_start = {f"'{new_schedule['sunday_start']}'::time" if new_schedule['sunday_start'] is not None else 'NULL'}, 
            sunday_end = {f"'{new_schedule['sunday_end']}'::time" if new_schedule['sunday_end'] is not None else 'NULL'}
        WHERE id = {employee_id}
    """)
    cursor.execute(query)

# Функция 3.5 "Изменение общего количества выходных"
@custom_error_handler
def update_holiday_entitlements(employee_id, new_year_id, new_hours, cursor):
    cursor.execute(
        text(f"""
        UPDATE holiday_entitlements
        SET holiday_entitlement_hours = { new_hours }
        WHERE employee_id = { employee_id } AND company_year_id = { new_year_id }
        """)
    )

# Функция 4 "Восстановление пароля"
@custom_error_handler
def restore_password(username, token, new_password, cursor):
    result = cursor.execute(
        text(f"""
        UPDATE users
        SET password = '{ new_password }'
        WHERE username = '{ username }' AND password_reset_token IS NOT NULL AND password_reset_token = '{ token }'
        returning username
        """)
    ).first()
    if result is not None:
        cursor.execute(text(f"UPDATE users set password_reset_token = NULL WHERE username = '{username}'"))
    return result is not None

# Функция для генерации токена для обновления пароля
@custom_error_handler
def gen_token_for_user(user_id, cursor):
    cursor.execute(
        text(f"CALL update_password_reset_token({ user_id })")
    )