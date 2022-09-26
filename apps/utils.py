# TODO: 프로젝트별 디렉터리 생성(os.makedir)
# TODO: 오디오 파일 삭제 기능 구현

import re
import os
from datetime import datetime
import uuid
from gtts import gTTS


def TTS(text, lang, speed=1.0):
    """
    TTS 모듈은 구글에서 제공하는 gTTS 사용(테스트)
    사용하고자 하는 함수로 대체 가능
    """
    return gTTS(text=text, lang=lang, slow=False)


def preprocess_data(text):
    """
    텍스트 전처리 함수
    - '.', '!', '?' 로 문장 구분
    - 빈 문장 삭제
    - 한글, 영어, 숫자, 물음표, 느낌표, 마침표, 따옴표, 공백를 제외하고 허용 x
    - 문장의 맨앞, 맨뒤에는 공백 x

    input: list (length=1)
    output: list
    """
    temp = re.sub(r"[^A-Za-z가-힣0-9?!.\"\'\s]", "", text)
    preprocessed = []
    for _ in re.split(r"[.?!]", temp):
        if not _:
            continue
        preprocessed.append(_.strip())

    return preprocessed


def convert_data(args, speed=1.0):
    """
    텍스트를 오디오로 변환하고 오디오 파일을 path에 저장하는 함수
    구글 TTS 사용(gTTS)
    input: list(list, path), float(default=1.0)
    output: list(instance=(id, text))
    """
    data, dir_path = args
    converted = []
    for i, text in enumerate(data):
        data_id = f"{datetime.now().strftime('%y%m%d%H%M%S')}{str(uuid.uuid4())[:3]}"
        tts = TTS(
            text=text,
            lang='ko',
        )
        file_path = os.path.join(dir_path, f'{data_id}.mp3')
        tts.save(file_path)
        converted.append((data_id, text))
    return converted



