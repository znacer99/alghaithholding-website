# pyright: reportMissingImports=false
# pyright: reportMissingModuleSource=false
from core.models import User, Department, Employee, ActivityLog, db
from sqlalchemy import func

# ------------------------
# Director Dashboard Data
# ------------------------
def get_director_dashboard_data():
    """
    Returns data for General Director dashboard
    - Users = admin staff (IT, Director…)
    - Employees = company employees
    """
    total_users = User.query.count()  # admin users only
    active_users = User.query.filter_by(is_active=True).count()
    inactive_users = total_users - active_users
    total_employees = Employee.query.count()  # all employees
    departments_count = Department.query.count()

    # Recent activity logs (Users only)
    recent_activities = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(10).all()

    # Employee counts per department
    departments = (
        db.session.query(
            Department,
            func.count(Employee.id).label('employee_count')  # count employees only
        )
        .outerjoin(Employee)
        .group_by(Department.id)
        .all()
    )

    return {
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'total_employees': total_employees,
        'departments_count': departments_count,
        'recent_activities': recent_activities,
        'departments': departments
    }


# ------------------------
# Manager Dashboard Data
# ------------------------
def get_manager_dashboard_data(user):
    """
    Returns data for a department manager
    - department_employee_count: Employees in their department
    - department_activities: Recent User activity (staff only)
    """
    department_employee_count = Employee.query.count()  # all employees
    department_activities = ActivityLog.query.filter_by(user_id=user.id)\
        .order_by(ActivityLog.timestamp.desc())\
        .limit(10).all()

    return {
        'department_employee_count': department_employee_count,
        'department_activities': department_activities
    }


# ------------------------
# Department Stats
# ------------------------
def get_department_stats():
    """
    Returns list of departments with employee counts
    """
    return db.session.query(
        Department.name,
        func.count(Employee.id).label('employee_count')
    ).outerjoin(Employee)\
     .group_by(Department.id)\
     .all()
