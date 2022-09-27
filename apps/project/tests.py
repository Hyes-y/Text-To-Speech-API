import os
import uuid
import shutil

from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.project.models import Project, TTSData
from apps.utils import convert_data, preprocess_data


class TTSAPITest(APITestCase):
    """
    프로젝트 및 텍스트 데이터 CRUD 테스트
    """
    def setUp(self):
        """ test 를 위한 mock 데이터 추가 """
        if not os.path.exists(settings.MEDIA_ROOT):
            os.mkdir(settings.MEDIA_ROOT)

        self.project_url = "/api/v1/projects/"

        User = get_user_model()

        self.user = User.objects.create(
            username='test_user',
            password=make_password('test1234')
        )

        self.another_user = User.objects.create(
            username='test_another_user',
            password=make_password('test1234')
        )

        self.project = Project.objects.create(
            user=self.user,
            project_id=f"project{str(self.user.id).zfill(6)}{str(uuid.uuid4())[:4]}",
            title='test_project',
        )

        self.another_project = Project.objects.create(
            user=self.another_user,
            project_id=f"project{str(self.another_user.id).zfill(6)}{str(uuid.uuid4())[:4]}",
            title='test_project',
        )

        data = convert_data([preprocess_data("초기 데이터입니다."), settings.MEDIA_ROOT], 1.0)[0]
        self.data = TTSData.objects.create(
            project=self.project,
            text=data[1],
            speed=1.0,
            order=1,
            data_id=data[0],
            path=os.path.join(settings.MEDIA_ROOT, self.project.project_id, f'{data[0]}.mp3')
        )

        self.refresh = RefreshToken.for_user(self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')

    def tearDown(self) -> None:
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

        super().tearDown()

    def test_project_create_success(self):
        """ 프로젝트 생성 성공 테스트 """

        data = {
            'title': "test_project_title",
            'text': "이것은 테스트입니다. 테스트를 함께 해주셔서 감사합니다.",
            'speed': 1.0,
        }
        request_url = self.project_url
        response = self.client.post(request_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_project_get_success(self):
        """ 프로젝트 조회 성공 테스트 """
        request_url = self.project_url
        response = self.client.get(request_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_project_get_fail_due_to_authorization(self):
        """ 프로젝트 조회 실패 테스트 - 권한 """
        request_url = f"{self.project_url}{self.another_project.project_id}/"
        response = self.client.get(request_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_tts_data_create_success(self):
        """ TTS 데이터 생성 성공 테스트 """

        data = {
            'text': "데이터 생성 테스트입니다.",
            'speed': 1.0,
            'order': None,
        }
        request_url = f"{self.project_url}{self.project.project_id}/data/"
        response = self.client.post(request_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_tts_data_create_fail_due_to_multiple_sentences(self):
        """ TTS 데이터 생성 실패 테스트 - 입력 문장이 여러개인 경우 """

        data = {
            'text': "데이터 생성 테스트입니다. 실패했을까요?",
            'speed': 1.0,
            'order': None,
        }
        request_url = f"{self.project_url}{self.project.project_id}/data/"
        response = self.client.post(request_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tts_data_create_fail_due_to_invalid_order(self):
        """ TTS 데이터 생성 실패 테스트 - 입력 순서가 유효하지 않은 경우 """

        data = {
            'text': "데이터 유효성 테스트입니다.",
            'speed': 1.0,
            'order': 100,
        }
        request_url = f"{self.project_url}{self.project.project_id}/data/"
        response = self.client.post(request_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tts_data_update_success(self):
        """ TTS 데이터 수정 성공 테스트 """

        data = {
            'text': "초기 데이터입니다.",
            'speed': 2.0,
        }
        request_url = f"{self.project_url}{self.project.project_id}/data/{self.data.data_id}/"
        response = self.client.put(request_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_tts_data_update_fail_due_to_empty_text(self):
        """ TTS 데이터 수정 실패 테스트 - 입력 문장이 없는 경우 """

        data = {
            'text': "",
            'speed': 1.0,
        }
        request_url = f"{self.project_url}{self.project.project_id}/data/{self.data.data_id}/"
        response = self.client.put(request_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tts_data_delete_success(self):
        """ TTS 데이터 삭제 성공 테스트 """
        request_url = f"{self.project_url}{self.project.project_id}/data/{self.data.data_id}/"
        response = self.client.delete(request_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
