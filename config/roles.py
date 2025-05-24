#from rest_framework_roles.roles import is_user, is_anon, is_admin


def is_seller(request, view):
    return is_user(request, view) and request.user.role == 'Продавец'

def is_manager(request, view):
    return is_user(request, view) and request.user.role == 'Администратор'

def owns_store(request, view):
    obj = view.get_object()
    return request.user == obj.owner

def belongs_to_store(request, view):
    obj = view.get_object()
    return request.user == obj.store

ROLES = {
#    'admin': is_admin,
 #   'user': is_user,
 #   'anon': is_anon,
    'manager': is_manager,
    'seller': is_seller,
}
