from datetime import timedelta
import datetime

from flask import Flask, request, redirect, render_template, url_for,flash,send_from_directory
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os
import traceback


from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine,select


from time import time

from db_interaction.create.all_inserts import *
from db_interaction.delete.all_deletes import *
from db_interaction.select.all_selects import *
from db_interaction.update.all_updates import *
from files.fille_scripts.file_essentials import *

app = Flask(import_name = __name__)
flask_bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = '08bc7ba9534e9c4be71bfc18520fc754abe17e0f2c6d7e739a83b69ae349e8c1'

app.config['ABSENCE_FOLDER'] = "/app/files/attachments/absence"
ALLOWED_ATTACHMENT_EXTENSIONS = {"txt","docx","doc","pdf"}

app.config['PROFILE_FOLDER'] = "/app/static/profile_pics"
ALLOWED_PIC_EXTENSIONS = {"png","jpg","jpeg","gif"}

login_manager = LoginManager()
login_manager.init_app(app)

Base = automap_base()
engine = create_engine('postgresql://root:root@postgres-container:5432/phoenix_db')

class User(Base,UserMixin):
    __tablename__ = 'users'

Base.prepare(autoload_with = engine)


session = Session(engine)

privilege_vocab = get_privileges(session)
roles_vocab = get_words_for_roles(session)

def check_if_admin(u_role,r_v):
    return (r_v[u_role]&62)>0

def get_permissions_vocab(u_role,r_v,p_v):
    permission_vocab = {}
    for p,check in p_v.items():
        var = (r_v[u_role]&check)>0
        permission_vocab[p] = var
    return permission_vocab

def check_permission_for_route(u_role:int,pass_word:str,r_v:dict,p_v:dict)->bool:
    return ( r_v[u_role] & p_v[pass_word] )<=0

def permissions_violation_check(privilege_name,exit_route):
    def decorator(function):
        def wrapped_f(*args,**kwargs):
            if check_permission_for_route(current_user.role_id,privilege_name,roles_vocab,privilege_vocab):
                return redirect(url_for('error_display',msg = "Privilege violation", data = f"You have no access to this part of functionality, contact your admin for more details", comeback_url = exit_route))
            return function(*args,**kwargs)
        wrapped_f.__name__ = function.__name__
        return wrapped_f
    return decorator

@app.errorhandler(Exception)
def error_handler_decorator(e):
    tb_msg = traceback.format_exception(None,e,e.__traceback__)
    tb_data = "\n".join(tb_msg)
    return render_template("ExceptionHandler.html",error = f"{e}",traceback = f"{tb_data}")

def try_parse_int(in_str:str):
    try:
        return int(in_str)
    except Exception:
        return None

@login_manager.user_loader
def load_user(user_id):
    return session.execute(select(User).where(User.id==int(user_id))).first().User


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=(try_parse_int(os.environ.get('SESSION_LIFETIME_MINS')) or 10))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        row = session.execute(select(User).where(User.username == request.form.get("username"))).first()
        if row is None:
            return redirect(url_for('error_display',msg = "Log-in error", data = f"You have provided not-existing username", comeback_url = "login"))
        if flask_bcrypt.check_password_hash(row.User.password.encode(),request.form.get("password")):
            login_user(row.User)
            return redirect(url_for("dashboard"))
    return render_template("Login.html",reset_me = os.environ.get('SESSION_LIFETIME_MINS'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/restore_password', methods=['GET', 'POST'])
def restore_pass():
    if request.method == "POST":
        restore_password(request.form.get("login"), request.form.get("token"), flask_bcrypt.generate_password_hash(request.form.get("password")).decode(), session)
        session.commit()
        return redirect("/login")
        
    return render_template('UserRestorePassword.html'
    )


@app.route('/dashboard')
@login_required
def dashboard():
    total,used = get_holiday_entitlement(current_user.id, session)
    return render_template('Dashboard.html',
                           total_hours = float(total), 
                           used_hours  = used,
                           holidays = get_upcoming_holidays(current_user.id, session),
                           requests = get_holiday_requests(current_user.id, session),
                           birthdays = get_birthdays(session),
                           work_periods = get_work_periods(session),
                           p_v=get_permissions_vocab(current_user.role_id,roles_vocab,privilege_vocab)
                           )


@app.route('/absences')
@login_required
def absences():
    absences = get_personal_absences(current_user.id, session)
    for i,v in enumerate(absences):
        absences[i]["Attachments"] = get_attachments_details_for_absence(v['ID'],session)
    return render_template('MyAbsence.html',
                            absences = absences,
                            p_v=get_permissions_vocab(current_user.role_id,roles_vocab,privilege_vocab)
    )


@app.route('/get_attachment/<f_name>', methods = ['GET','POST'])
def get_attachment(f_name):
    try:
        return send_from_directory(app.config['ABSENCE_FOLDER'],f_name,as_attachment = True)
    except Exception:
        return redirect('/absences')
        

@app.route('/add_absence', methods=['GET', 'POST'])
@login_required
def add_absence():
    if request.method == "POST":
        return redirect(f"/add_absence/{request.form.get('year_select')}")
        
    return render_template('CreateNewRequestAbsence.html', 
                           company_years = get_financial_year_titles(session),
                           p_v=get_permissions_vocab(current_user.role_id,roles_vocab,privilege_vocab)
    )


@app.route('/add_absence/<cy>', methods=['GET', 'POST'])
@login_required
def add_absence_fin(cy):
    if request.method == "POST":
        if datetime.strptime(request.form.get('start_date'),'%Y-%m-%d')>datetime.strptime(request.form.get('end_date'),'%Y-%m-%d'):
            return redirect('/absences')
        created_id = create_absence(request.form.get("reason"), request.form.get("start_date"), request.form.get("end_date"), cy, current_user.id, session)
        session.commit()
        if "attachments" not in request.files:
            flash('No file was selected')
            return redirect("/absences")
        files = request.files.getlist('attachments')
        data_vocab = {}
        for file in files:
            if file.filename == '':
                flash('No selected file')
                return redirect("/absences")
            if file and file_allowed(file.filename,ALLOWED_ATTACHMENT_EXTENSIONS):
                filename = secure_filename(file.filename)
                call_filename = f"{int(time()*10**7)}_{filename}"
                data_vocab[filename] = (os.path.join(app.config['ABSENCE_FOLDER'],call_filename),file,call_filename)
        created = create_attachments_for_abs_note(created_id,data_vocab,session)
        if created != len(data_vocab.items()):
            flash('Error occured while writing data')
        session.commit()
        for file,(file_name,file_obj,call_filename) in data_vocab.items():
            file_obj.save(os.path.join(app.config['ABSENCE_FOLDER'],call_filename))
        return redirect("/absences")
        
    return render_template('CreateNewRequestAbsence.html',
                           company_year = get_financial_years_for_absences(session, cy),
                           p_v=get_permissions_vocab(current_user.role_id,roles_vocab,privilege_vocab)
    )


@app.route('/holidays')
@login_required
def holidays():
    return render_template('MyHolidays.html',
                            holidays = get_personal_holidays(current_user.id, session),p_v=get_permissions_vocab(current_user.role_id,roles_vocab,privilege_vocab)
    )


@app.route('/add_holiday', methods=['GET', 'POST'])
@login_required
def add_holiday():
    if request.method == "POST":
        return redirect(f"/add_holiday/{request.form.get('year_select')}")
    return render_template('CreateNewRequestHoliday.html', company_years = get_financial_year_titles(session),p_v=get_permissions_vocab(current_user.role_id,roles_vocab,privilege_vocab)
    )


@app.route('/add_holiday/<cy>', methods=['GET', 'POST'])
@login_required
def add_holiday_fin(cy):
    if request.method == "POST":
        if datetime.strptime(request.form.get('start_date'),'%Y-%m-%d')>datetime.strptime(request.form.get('end_date'),'%Y-%m-%d'):
            return redirect('/holidays')
        create_holiday(request.form.get("name"), cy, request.form.get("start_date"), request.form.get("end_date"), current_user.id, session)
        session.commit()
        return redirect("/holidays")
        
    return render_template('CreateNewRequestHoliday.html', company_year = get_financial_year_dates_for_holidays(session, cy),p_v=get_permissions_vocab(current_user.role_id,roles_vocab,privilege_vocab)
    )


@app.route('/projects')
@login_required
@permissions_violation_check('project','dashboard')
def projects():
    return render_template('AdminProjects.html',
                            projects = get_projects(session),p_v=get_permissions_vocab(current_user.role_id,roles_vocab,privilege_vocab)
    )


@app.route('/add_project', methods=['GET', 'POST'])
@login_required
@permissions_violation_check('project','dashboard')
def add_project():
    if request.method == "POST":
       
        create_project(request.form.get("name"), request.form.get("description"), session)
        session.commit()
        return redirect("/projects")
        
    return render_template('AdminProject_CreateNew.html',p_v=get_permissions_vocab(current_user.role_id,roles_vocab,privilege_vocab)
    )


@app.route('/departments')
@login_required
@permissions_violation_check('department','dashboard')
def departments():
    return render_template('AdminDepartments.html',
                            departments = get_departments(session),p_v=get_permissions_vocab(current_user.role_id,roles_vocab,privilege_vocab)
    )


@app.route('/add_department', methods=['GET', 'POST'])
@login_required
@permissions_violation_check('department','dashboard')
def add_department():
    if request.method == "POST":
       
        create_department(request.form.get("title"), session, request.form.get("parent_id"))
        session.commit()
        return redirect("/departments")
        
    return render_template('AdminDepartments_CreateNew.html', departments = get_department_names(session),p_v=get_permissions_vocab(current_user.role_id,roles_vocab,privilege_vocab)
    )


@app.route('/company_years')
@login_required
@permissions_violation_check('year','dashboard')
def company_years():
    return render_template('AdminYear.html',
                            company_years = get_financial_years(session),p_v=get_permissions_vocab(current_user.role_id,roles_vocab,privilege_vocab)
    )


@app.route('/add_company_year', methods=['GET', 'POST'])
@login_required
@permissions_violation_check('year','dashboard')
def add_company_year():
    if request.method == "POST":
       
        create_company_year(request.form.get("year_title"), request.form.get("year"), session)
        session.commit()
        return redirect("/company_years")
        
    return render_template('AdminYear_CreateNew.html',p_v=get_permissions_vocab(current_user.role_id,roles_vocab,privilege_vocab)
    )


@app.route('/job_roles')
@login_required
@permissions_violation_check('jobroles','dashboard')
def job_roles():
    return render_template('AdminJobRoles.html',
                            job_roles = get_job_roles(session),p_v=get_permissions_vocab(current_user.role_id,roles_vocab,privilege_vocab)
    )


@app.route('/add_job_role', methods=['GET', 'POST'])
@login_required
@permissions_violation_check('jobroles','dashboard')
def add_job_role():
    if request.method == "POST":
       
        create_job_role(request.form.get("name"), request.form.get("description"), session)
        session.commit()
        return redirect("/job_roles")
        
    return render_template('AdminJobRoles_CreateNew.html',p_v=get_permissions_vocab(current_user.role_id,roles_vocab,privilege_vocab)
    )


@app.route('/users')
@login_required
@permissions_violation_check('users','dashboard')
def users():
    return render_template('AdminUser.html',
                            employees = get_employees(session),
                            p_v=get_permissions_vocab(current_user.role_id,roles_vocab,privilege_vocab)
    )


@app.route('/delete_user/<u_id>', methods=['GET'])
@login_required
@permissions_violation_check('users','dashboard')
def delete_user_info(u_id):
    delete_user(u_id, session)
    session.commit()
    return redirect("/users")


@app.route('/add_user', methods=['GET', 'POST'])
@login_required
@permissions_violation_check('users','dashboard')
def add_user():
    if request.method == "POST":
        create_user(request.form.get("email"), request.form.get("full_name"), request.form.get("username"), request.form.get("role"), session)
        session.commit()
        return redirect("/users")
        
    return render_template('AdminUser_CreateNew.html', roles = get_role_names(session),p_v=get_permissions_vocab(current_user.role_id,roles_vocab,privilege_vocab)
    )


@app.route('/update/<u_id>', methods=['GET'])
@login_required
@permissions_violation_check('users','dashboard')
def view_update_user(u_id):
    p_info = get_professional_info(u_id, session)
    if p_info['Profile Image'] is not None:
        p_info['Profile Image'] = url_for('static',filename = f"profile_pics/{p_info['Profile Image']}")
    return render_template('AdminProfileUpdateInformation.html', id = u_id, 
                           user_info = get_user_info(u_id, session), 
                           roles = get_role_names(session), 
                           professional_info = p_info, 
                           managers = get_all_user_names(session), 
                           departments = get_department_names(session),
                           job_roles = get_job_role_names(session),
                           projects = get_project_names(session),
                           countries = get_country_names(session),
                           contact_info = get_contact_info(u_id, session),
                           working_hours = get_working_hours(u_id, session),
                           entitlements = get_holiday_entitlements(u_id, session),
                           p_v=get_permissions_vocab(current_user.role_id,roles_vocab,privilege_vocab)
    )


@app.route('/update_general_info/<u_id>', methods=['POST'])
@login_required
@permissions_violation_check('users','dashboard')
def update_general_info(u_id):
    update_user_info(u_id, request.form.get("full_name"), request.form.get("email"), request.form.get("role"), session)
    session.commit()
    return redirect(f"/update/{ u_id }")


@app.route('/token_gen_req/<u_id>', methods=['POST'])
@login_required
@permissions_violation_check('users','dashboard')
def token_gen_req(u_id):
    gen_token_for_user(u_id, session)
    session.commit()
    return redirect(f"/update/{ u_id }")
            

@app.route('/update_professional_info/<u_id>', methods=['POST'])
@login_required
@permissions_violation_check('users','dashboard')
def update_prof_info(u_id):
    if 'profile_image' in request.files and request.files['profile_image'].filename != '':
        to_download = request.files['profile_image']
        f_name = None
        if to_download and file_allowed(to_download.filename,ALLOWED_PIC_EXTENSIONS):
            f_name = f"user_{u_id}_profile.png"
        to_download.save(os.path.join(app.config['PROFILE_FOLDER'],f_name))
        update_professional_info_w_pic(u_id, request.form.get("reference"), request.form.get("manager"), request.form.get("department"), request.form.get("job_role"), request.form.get("project"), request.form.get("date_of_birth"), request.form.get("service_start"), f_name, session)
        session.commit()
    else:
        update_professional_info_no_pic(u_id, request.form.get("reference"), request.form.get("manager"), request.form.get("department"), request.form.get("job_role"), request.form.get("project"), request.form.get("date_of_birth"), request.form.get("service_start"), session)
        session.commit()
    return redirect(f"/update/{ u_id }")


@app.route('/fire_employee/<u_id>', methods=['POST'])
@login_required
@permissions_violation_check('users','dashboard')
def fire_emp(u_id):
    fire_employee(u_id, session)
    session.commit()
    return redirect(f"/update/{ u_id }")


@app.route('/update_contact_info/<u_id>', methods=['POST'])
@login_required
@permissions_violation_check('users','dashboard')
def update_cont_info(u_id):
    update_contact_info(u_id, request.form.get("address_line"), request.form.get("city"), request.form.get("region"), request.form.get("postal_code"), request.form.get("country"), request.form.get("mobile_phone"), session)
    session.commit()
    return redirect(f"/update/{ u_id }")


@app.route('/update_working_hours/<u_id>', methods=['POST'])
@login_required
@permissions_violation_check('users','dashboard')
def update_work_hours(u_id):
    vocab = {'monday_start': request.form.get("monday_start") if request.form.get("monday_start") != '' else None, 
             'monday_end': request.form.get("monday_end") if request.form.get("monday_end") != '' else None, 
             'tuesday_start': request.form.get("tuesday_start") if request.form.get("tuesday_start") != '' else None, 
             'tuesday_end': request.form.get("tuesday_end") if request.form.get("tuesday_end") != '' else None, 
             'wednesday_start': request.form.get("wednesday_start") if request.form.get("wednesday_start") != '' else None, 
             'wednesday_end': request.form.get("wednesday_end") if request.form.get("wednesday_end") != '' else None, 
             'thursday_start': request.form.get("thursday_start") if request.form.get("thursday_start") != '' else None, 
             'thursday_end': request.form.get("thursday_end") if request.form.get("thursday_end") != '' else None, 
             'friday_start': request.form.get("friday_start") if request.form.get("friday_start") != '' else None, 
             'friday_end': request.form.get("friday_end") if request.form.get("friday_end") != '' else None, 
             'saturday_start': request.form.get("saturday_start") if request.form.get("saturday_start") != '' else None, 
             'saturday_end': request.form.get("saturday_end") if request.form.get("saturday_end") != '' else None, 
             'sunday_start': request.form.get("sunday_start") if request.form.get("sunday_start") != '' else None, 
             'sunday_end': request.form.get("sunday_end") if request.form.get("sunday_end") != '' else None, 
             }
    if not validate_times(vocab):
        return redirect(f"/update/{ u_id }")
    update_working_hours(u_id, vocab, session)
    session.commit()
    return redirect(f"/update/{ u_id }")


@app.route('/update_holiday_entitlements/<u_id>', methods=['POST'])
@login_required
@permissions_violation_check('users','dashboard')
def update_hol_ent(u_id):
    update_holiday_entitlements(u_id, [k for k in list(request.form.keys()) if k!="time"][0], request.form.get("time"), session)
    session.commit()
    return redirect(f"/update/{ u_id }")


@app.route('/add_holiday_entitlement/<u_id>', methods=['GET', 'POST'])
@login_required
@permissions_violation_check('users','dashboard')
def add_holiday_entitlement(u_id):
    if request.method == "POST":
        add_holiday_entitlements(u_id, request.form.get("year_select"), request.form.get("holiday_entitlement_hours"), session)
        session.commit()
        return redirect(f"/update/{ u_id }")
        
    return render_template('AdminHolidayEntitlement_CreateNew.html', 
                           company_years = get_financial_year_titles_for_empl_entitlement(session, u_id), 
                           id = u_id,
                           p_v=get_permissions_vocab(current_user.role_id,roles_vocab,privilege_vocab)
    )


@app.route('/absence_approves')
@login_required
def absence_approves():
    absences = get_subordinate_absences(current_user.id, session)
    for i,v in enumerate(absences):
        absences[i]['Attachments'] = get_attachments_details_for_absence(v['ID'],session)
    return render_template('AbsencesSubordinateEmployees.html',
                            absences = absences,
                            p_v=get_permissions_vocab(current_user.role_id,roles_vocab,privilege_vocab)
    )


@app.route('/approve_absence/<ab_id>', methods=['POST'])
@login_required
def approve_absences(ab_id):
    approve_absence(ab_id, session)
    session.commit()
    return redirect("/absence_approves")


@app.route('/reject_absence/<ab_id>', methods=['POST'])
@login_required
def reject_absences(ab_id):
    reject_absence(ab_id, request.form.get("reason"), session)
    session.commit()
    return redirect("/absence_approves")


@app.route('/delete_absence/<ab_id>', methods=['POST'])
@login_required
def delete_absences(ab_id):
    delete_absence_request(ab_id, session)
    session.commit()
    return redirect("/absence_approves")


@app.route('/holiday_approves')
@login_required
def holiday_approves():
    return render_template('HolidaySubordinateEmployees.html',
                            holidays = get_subordinate_holidays(current_user.id, session),
                            p_v=get_permissions_vocab(current_user.role_id,roles_vocab,privilege_vocab)
    )


@app.route('/approve_holiday/<hol_id>', methods=['POST'])
@login_required
def approve_holidays(hol_id):
    approve_holiday(hol_id, session)
    session.commit()
    return redirect("/holiday_approves")


@app.route('/reject_holiday/<hol_id>', methods=['POST'])
@login_required
def reject_holidays(hol_id):
    reject_holiday(hol_id, request.form.get("reason"), session)
    session.commit()
    return redirect("/holiday_approves")


@app.route('/delete_holiday/<hol_id>', methods=['POST'])
@login_required
def delete_holidays(hol_id):
    delete_holiday_request(hol_id, session)
    session.commit()
    return redirect("/holiday_approves")


@app.route('/search_and_tree', methods=['GET', 'POST'])
@login_required
def search_and_tree():
    return render_template('EmployeeListAndSearch.html', 
                           data = get_department_and_employees_united(session),
                           p_v=get_permissions_vocab(current_user.role_id,roles_vocab,privilege_vocab)
    )


@app.route('/search_and_tree/<u_id>', methods=['GET', 'POST'])
@login_required
def search_and_tree_w_profile(u_id):
    return render_template('EmployeeListAndSearch.html', 
                           data = get_department_and_employees_united(session), 
                           emp_data = get_user_general_data(u_id, session),
                           p_v=get_permissions_vocab(current_user.role_id,roles_vocab,privilege_vocab)
    )


@app.route('/profile_view', methods=['GET'])
@login_required
def profile_view():
    p_info = get_professional_info(current_user.id, session)
    p_info['Profile Image'] = url_for('static',filename = f"/profile_pics/{p_info['Profile Image']}")
    return render_template('Profile.html', 
                           user_info = get_user_info(current_user.id, session), 
                           professional_info = p_info,
                           contact_info = get_contact_info(current_user.id, session), 
                           working_hours = get_working_hours(current_user.id, session), 
                           entitlements = get_holiday_entitlements(current_user.id, session),
                           p_v=get_permissions_vocab(current_user.role_id,roles_vocab,privilege_vocab)
    )


@app.route('/<msg>/<data>/<comeback_url>')
def error_display(msg,data,comeback_url):
    return render_template('DebugError.html',msg=msg,data=data,comeback_url = comeback_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)