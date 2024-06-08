from sqlalchemy.sql import text

# Функция 1 "Удалить запрос на выходные"
def delete_holiday_request(holiday_id, cursor):
    cursor.execute(
        text(f"DELETE FROM holidays WHERE id = {holiday_id}")
    )
    # из-за того, что данные в holiday_date связаны с holidays каскадно (ON DELETE CASCADE), то они автоматически удалятся, когда удалится соответствующая запись из holidays

# Функция 2 "Удалить запрос на пропуск"
def delete_absence_request(absence_id, cursor):
    cursor.execute(
        text(f"DELETE FROM absences WHERE id = {absence_id}")
    )
    # аналогично, из-за каскадности также удалятся данные из attachments и absence_attachments

# Функция 2 "Удалить сотрудника-юзера"
def delete_user(user_id, cursor):
    cursor.execute(
        text(f"DELETE FROM users WHERE id = { user_id } ")
    )