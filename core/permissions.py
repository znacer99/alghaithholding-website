#core/permissions.py
class Permission:
    VIEW = 0b0001
    EDIT = 0b0010
    DELETE = 0b0100
    ADMIN = 0b1000

    # Simple permission matrix (role → permissions)
    ROLE_PERMISSIONS = {
        'it_manager': VIEW | EDIT | DELETE | ADMIN,
        'general_director': VIEW | EDIT | DELETE | ADMIN,
        'general_manager': VIEW | EDIT,
        'head_of_department': VIEW | EDIT,
        'manager': VIEW,
        'employee': VIEW
    }

    @classmethod
    def check(cls, role, permission):
        """Check if role has the requested permission"""
        return cls.ROLE_PERMISSIONS.get(role.lower(), 0) & permission == permission