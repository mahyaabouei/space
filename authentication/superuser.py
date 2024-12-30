from django.contrib.auth import get_user_model

def create_superuser_if_not_exists(username, email, password, birth_date):
    try:
        User = get_user_model()
        # Check if the user already exists
        if User.objects.filter(username=username).exists():
            return
        # Validate birth_date input
        if not birth_date:
            return
        # Create the superuser
        user = User(username=username, email=email, birth_date=birth_date)
        user.set_password(password)
        user.is_superuser = True  # Set superuser flag
        user.is_staff = True  # Set staff flag
        user.save()

    except :
        pass

