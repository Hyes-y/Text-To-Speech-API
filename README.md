# TTS(Text to Speech) REST-API


## 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [개발 기간](#개발-기간)
3. [프로젝트 기술 스택](#프로젝트-기술-스택)
4. [과제 요구사항 분석](#과제-요구사항-분석)
5. [ERD](#erd)
6. [API 명세](#api-명세)
7. [프로젝트 시작 방법](#프로젝트-시작-방법)


<br>


## 프로젝트 개요


Django Rest Framework 를 이용한 REST API 서버로

- TTS 프로젝트 생성, 조회, 수정, 삭제 기능
- TTS 프로젝트 내 TTS 데이터 생성, 조회, 수정, 삭제 기능
- TTS 데이터 다운로드
- 인증 / 인가
- 테스트

위 기능을 제공합니다.

### ⭐ TTS(Text to Speech) 란?
- 텍스트를 음성으로 변환하는 기술
- 입력 받은 텍스트를 음성 파일로 변환


<br>

## 개발 기간
- 2022/09/22~2022/09/27 (4일)


<br>

## 프로젝트 기술 스택

### Backend
<section>
<img src="https://img.shields.io/badge/Django-092E20?logo=Django&logoColor=white"/>
<img src="https://img.shields.io/badge/Django%20REST%20Framework-092E20?logo=Django&logoColor=white"/>
</section>

### DB
<section>
<img src="https://img.shields.io/badge/MySQL-4479A1?logo=MySQL&logoColor=white"/>
</section>

### Tools
<section>
<img src="https://img.shields.io/badge/GitHub-181717?logo=GitHub&logoColor=white"/>
<img src="https://img.shields.io/badge/Discord-5865F2?logo=Discord&logoColor=white">
<img src="https://img.shields.io/badge/Postman-FF6C37?logo=Postman&logoColor=white">
</section>

<br>

## 과제 요구사항 분석
✅ 로그인한 유저만 접근 가능합니다.


### 0. TTS 변환 관련
- `apps/utils.py`
- Google에서 제공하는 `gTTS` 모듈을 사용
- 입력 데이터 전처리 함수 구현(`preprocess_data`)
  - 한글, 영어, 숫자, 물음표, 느낌표, 마침표, 따옴표, 공백을 제외하고 허용 x
  - 빈 문장 허용 x
  - 마침표(.), 물음표(?), 느낌표(!) 로 문장 구분
- 전처리 데이터 → 음성 파일 변환 함수 구현(`convert_data`)
  - `gTTS` 함수를 사용해서 음성 파일로 변환 뒤 지정 위치에 저장
  - 음성 파일 생성시 식별자 발급(`data_id`)
- 오디오 생성 위치 및 파일명
  - `/audio/{project_id}/{data_id}.mp3`

### 1. 프로젝트 관련

#### 1-1) 프로젝트 생성

- 프로젝트 생성시 
  1) 여러 문장으로 이루어진 긴 문자열을 입력받고 
  2) 해당 문자열을 문장 단위로 분리하여 TTS 변환(음성 파일 생성)
  3) 생성된 음성파일 관련 데이터는 TTSData 모델에 저장

  
#### 1-2) 프로젝트 수정
- 프로젝트명 수정 가능

#### 1-3) 프로젝트 조회
- 본인의 프로젝트 조회 가능

#### 1-4) 프로젝트 삭제

### 2. TTS 데이터 관련
#### 2-1) TTS 데이터 생성
- TTS 데이터 생성시 
  1) 입력 받은 문자열을 전처리 하고 음성 파일로 변환한 후
  2) 발급받은 식별자(data_id) 및 전처리한 텍스트, 속도 및 기타 데이터 저장

<br>

- 생성시 문장의 위치 설정 가능
  1) 입력으로 `order: n` 을 받게 되면
  2) n번째 (1 ≤ n ≤ 프로젝트 내 tts 데이터 개수 + 1) 위치에 문장을 저장한다는 의미
  3) 기존에 저장돼있던 n ~ 끝번까지 `order = order + 1` 처리
  4) 조회시 `order` 필드로 정렬
  - 해당 작업은 동시에 실행할 경우 데이터 정합성이 깨질 우려가 있으므로 `@transaction.atomic()` 사용

<br>


#### 2-2) TTS 데이터 수정
- `text`, `speed` 변경 가능 (위치 수정 불가능 → 추후 수정할 예정)
- `text` 변경시 생성 과정(문장 위치 설정 제외) 다시 반복
  - 기존 데이터의 `data_id`, `text`, `path` 변경


#### 2-3) TTS 데이터 조회
- `order` 필드 오름차순으로 정렬
- 한 번에 10개씩 볼 수 있도록 Pagination 구현


#### 2-4) TTS 데이터 삭제

- 삭제시 해당 오디오 파일도 같이 삭제


### 3. TTS 데이터 다운로드
- 데이터 다운로드 가능
- `.mp3`, `.wav` 확장자 파일 전송을 위해 django의 `HTTPResponse` 이용
- `Content-Type`: `audio/mpeg`
- 해당 url로 접근시 바로 다운로드
  - 바로 다운로드 되지 않고 유저에게 확인 절차를 거칠 수 있는지 고민중
    
### 4. 인증 / 인가
- `simpleJWT`를 이용한 토큰 인증 방식 구현
- 현재는 django admin 사이트에서 (혹은 db에 직접) 유저 생성 
  - 회원가입은 추후 구현할 예정


### 5. 테스트
- `rest_framework`의 `APITestCase` 이용

<br>

- 프로젝트 생성 테스트 <br>
    - 성공

- 프로젝트 조회 테스트 <br>
    - 성공
    - 실패: 다른 유저의 프로젝트를 요청한 경우(권한)
  
<br>

- 데이터 생성 테스트 <br>
    - 성공
    - 실패: 입력 문장이 여러 개인 경우
    - 실패: 입력 순서가 유효하지 않은 경우

- 데이터 수정 테스트 <br>
    - 성공
    - 실패: 입력 문장이 없는 경우

- 데이터 삭제 테스트 <br>
    - 성공

<br>


<br>

### 기능 목록

| 버전  | 기능    | 세부 기능   | 설명                   | 상태  |
|-----|-------|---------|----------------------|-----|
| v1  | 프로젝트  | 생성      | 프로젝트 및 TTS데이터 생성     | ✅   |
| -   | -     | 조회      | 프로젝트 조회              | ✅   |
| -   | -     | 수정      | 프로젝트 수정              | ✅   | 
| -   | -     | 삭제      | 프로젝트 삭제              | ✅   |
| -   | 데이터   | 생성      | TTS 데이터 생성           | ✅   |
| -   | -     | 조회      | TTS 데이터 조회 (메타데이터)   | ✅   |
| -   | -     | 수정      | TTS 데이터 (텍스트, 속도) 수정 | ✅   | 
| -   | -     | 삭제      | TTS 데이터 및 오디오 파일 삭제  | ✅   |
| -   | -     | 조회      | 쿠폰 사용 내역 통계          | ✅   |
| -   | -     | 다운로드    | TTS 데이터 파일 다운로드      | ✅   |
| -   | 유저    | 인증 / 인가 | 로그인 기능 및 권한 설정       | ✅   |
| -   | 테스트   | 테스트     | 기능, 전체 테스트           | ✅   |

🔥 추가 기능 구현시 업데이트 예정

<br>

## ERD
ERD 

- User model
  - User 모델은 Django의 `AbstractUser`를 overriding 
- Project model
  - URL 접근시 DB PK 대신 `project_id`(unique) 사용
  - USER ↔ PROJECT (1:N)
- TTSData model
  - URL 접근시 DB PK 대신 `data_id`(unique) 사용
  - PROJECT ↔ TTSDATA (1:N)
  - 프로젝트별로 문장 순서 정렬(`order_by='order'`)


<br>


## API 명세

### [프로젝트]
### 1. 프로젝트 생성
- URL: `POST /api/v1/projects/`
- Request
```json
{
    "title": "프로젝트 명",
    "text": "음성 파일로 변환할 문장. 여러 문장을 입력으로 받을 수 있음.",
    "speed": 1.0
}
```
- Response
- status: `201 Created`
```json
{
    "project_id": "프로젝트 id",
    "title": "프로젝트 명",
    "created_at": "2022-09-27T03:07:23.394805",
    "updated_at": "2022-09-27T03:07:23.394805",
    "user": "유저 id"
}
```

<br>

### 2. 프로젝트 수정
- URL: `PUT /api/v1/projects/:project_id/`
- Request
```json
{
    "title": "프로젝트 명 수정",
}
```
- Response
- status: `200 OK`
```json
{
    "project_id": "프로젝트 id",
    "title": "프로젝트 명 수정",
    "created_at": "2022-09-27T03:07:23.394805",
    "updated_at": "2022-09-27T03:07:23.394805",
    "user": "유저 id"
}
```

<br>

### 3. 프로젝트 조회
#### 3-1. 전체 조회
- URL: `GET /api/v1/projects/`

- Response
- status: `200 OK`
```json
[
  {
      "project_id": "프로젝트 id",
      "title": "프로젝트 명 수정",
      "created_at": "2022-09-27T03:07:23.394805",
      "updated_at": "2022-09-27T03:07:23.394805",
      "user": "유저 id"
  },
  ...
]
```

<br>

#### 3-2. 상세 조회
- URL: `GET /api/v1/projects/:project_id/`

- Response
- status: `200 OK`
```json
{
    "project_id": "프로젝트 id",
    "title": "프로젝트 명 수정",
    "created_at": "2022-09-27T03:07:23.394805",
    "updated_at": "2022-09-27T03:07:23.394805",
    "user": "유저 id"
}
```

<br>

### 4. 프로젝트 삭제
- URL: `DELETE /api/v1/projects/:project_id/`

- Response
- status: `204 NO CONTENT`


<br>

### [TTS 데이터]
### 1. 데이터 생성
- URL: `POST /api/v1/projects/:project_id/data/`
- Request
```json
{
    "text": "데이터 테스트입니다.",
    "speed": 1.0,
    "order": 1
}
```
- Response
- status: `201 Created`
```json
{
    "text": "데이터 테스트입니다",
    "speed": 1.0,
    "order": 1
}
```

<br>

### 2. 데이터 수정
- URL: `PUT /api/v1/projects/:project_id/data/:data_id/`
- Request
```json
{
    "text": "데이터 명 수정!",
    "speed": 1.0
}
```
- Response
- status: `200 OK`
```json
{
    "text": "데이터 명 수정",
    "speed": 1.0,
    "order": 1
}
```

<br>

### 3. 데이터 조회
#### 3-1. 전체 조회
- URL: `GET /api/v1/projects/:project_id/data/?pages=`

- Response
- status: `200 OK`
```json
{
    "count": 6,
    "next": "다음 페이지 URL",
    "previous": "이전 페이지 URL",
    "results": [
        {
            "project_id": "000002468b",
            "data_id": "220927211620779",
            "text": "안녕하세요",
            "speed": 1.0,
            "order": 1,
            "created_at": "2022-09-27T21:16:22.501291",
            "updated_at": "2022-09-27T21:16:22.502292"
        },
        {
            "project_id": "000002468b",
            "data_id": "22092721162058e",
            "text": "반갑습니다",
            "speed": 1.0,
            "order": 2,
            "created_at": "2022-09-27T21:16:22.502292",
            "updated_at": "2022-09-27T21:16:22.502292"
        },
        {
            "project_id": "000002468b",
            "data_id": "22092721174670f",
            "text": "오늘은 9월 28일 수요일 입니다",
            "speed": 1.0,
            "order": 3,
            "created_at": "2022-09-27T21:16:22.502292",
            "updated_at": "2022-09-27T21:17:47.060966"
        },
        {
            "project_id": "000002468b",
            "data_id": "220927211621ae2",
            "text": "좋은 하루 되세요",
            "speed": 1.0,
            "order": 4,
            "created_at": "2022-09-27T21:16:22.502292",
            "updated_at": "2022-09-27T21:16:22.502292"
        },
        ...
    ]
}
```

<br>

#### 3-2. 상세 조회
- URL: `GET /api/v1/projects/:project_id/data/:data_id/`

- Response
- status: `200 OK`
```json
{
    "project_id": "000002468b",
    "data_id": "22092721174670f",
    "text": "오늘은 9월 28일 수요일 입니다",
    "speed": 1.0,
    "order": 3,
    "created_at": "2022-09-27T21:16:22.502292",
    "updated_at": "2022-09-27T21:17:47.060966"
}
```

<br>

### 4. 데이터 삭제
- URL: `DELETE /api/v1/projects/:project_id/data/:data_id/`

- Response
- status: `204 NO CONTENT`


<br>

### 5. 데이터 다운로드
- URL: `GET /api/v1/projects/:project_id/data/:data_id/download/`

- Response(HTTP Response)
- status: `200 OK`
- response.body에 파일 첨부

<br>

## 프로젝트 시작 방법
1. 로컬에서 실행할 경우
```bash
# 프로젝트 clone(로컬로 내려받기)
git clone -b develop --single-branch ${github 주소}
cd ${디렉터리 명}

# 가상환경 설정
python -m venv ${가상환경명}
source ${가상환경명}/bin/activate
# window (2 ways) 
# 1> ${가상환경명}/Scripts/activate
# 2> activate

# 라이브러리 설치
pip install -r requirements.txt
# 실행
python manage.py runserver
```

<br>
