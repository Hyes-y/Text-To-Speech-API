from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # 기본 필드 중 사용하지 않는 필드 제외
    first_name = None
    last_name = None
