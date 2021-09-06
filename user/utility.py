from .models import Credentials, Staff_Member, Roles
from validate_email import validate_email


def build_user_context(request, credential_list):

    is_superuser = (request.POST.get('is_superuser')=='Yes')
    credential_id = request.POST.get("credentials")
    the_credential=None

    if not(credential_id==None):
        the_credential = Credentials.objects.get(pk=credential_id)


    the_fname = request.POST.get('fname')
    the_lname = request.POST.get('lname')
    the_username = request.POST.get('username').lower()
    the_email = request.POST.get('email')
    bad_email = not(validate_email(the_email))
    duplicate_email = (len(Staff_Member.objects.filter(email=the_email))>0)
    duplicate_username = (len(Staff_Member.objects.filter(username=the_username))>0)

    the_phonenumber_str = request.POST.get('phonenumber')
    this_user = ({
        'username': the_username,
        'phonenumber': the_phonenumber_str,
        'fname': the_fname,
        'lname': the_lname,
        'credential': the_credential,
        'is_superuser': is_superuser,
        'credential_list': credential_list,
        'email': the_email,
        'bad_email': bad_email,
        'duplicate_username': duplicate_username,
        'duplicate_email': duplicate_email,
        'new_user':'False',
    })
    return this_user

def build_user_context_blank(credential_list):
    this_user = ({
        'username': '',
        'phonenumber': '503-555-1212',
        'fname': '',
        'lname': '',
        'credential': '',
        'is_superuser': False,
        'credential_list': credential_list,
        'bad_email': False,            
        'duplicate_username': False,
        'duplicate_email': False,
        'new_user':'True',
    })
    return this_user


def build_user_context_from_DB(one_member, credential_list):

    this_user = ({
        'username': one_member.username,
        'phonenumber': one_member.phone_number,
        'fname': one_member.first_name,
        'lname': one_member.last_name,
        'credential':  one_member.credential,
        'is_superuser': one_member.is_superuser,
        'credential_list': credential_list,
        'email': one_member.email,
        'bad_email': False,
        'duplicate_username': False,
        'duplicate_email': False,
        'new_user':False,
    })
    return this_user    