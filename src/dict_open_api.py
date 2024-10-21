from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo
import re
import requests
import xml.etree.ElementTree as eT

URL = 'https://krdict.korean.go.kr/api/search'
CONFIG = mw.addonManager.getConfig(__name__)
key_prompt_type = True

replacement_patterns = {
    1: [r'([가-힣]+|[▼←]+|[a-zA-Z]+)', '-'], # Replace each group of non-Hanja chars with hyphen
    2: [r'[가-힣]|[▼←]|[a-zA-z]', '-'], # Replace each non-Hanja char with hyphen
    3: [r'[가-힣]|[▼←]|[a-zA-z]', ''],  # Remove non-Hanja chars
    4: [r'(?!) ', '']
}
if type(CONFIG['replacement_char']) == int and CONFIG['replacement_char'] <=4:
    replacement_pattern_and_char = replacement_patterns.get(CONFIG['replacement_char'])
else:
    replacement_pattern_and_char = [r'(?!) ', '']

pos = {
    '명사': 'noun',
    '대명사': 'pronoun',
    '수사': 'numeral',
    '조사': 'particle',
    '동사': 'verb',
    '형용사': 'adjective',
    '관형사': 'determiner',
    '부사': 'adverb',
    '감탄사': 'interjection',
    '접사': 'affix',
    '의존 명사': 'dependent noun',
    '보조 동사': 'auxiliary verb',
    '보조 형용사': 'auxiliary adjective',
    '어미': 'suffix',
    '품사 없음': ''
}


class InputDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("User Input")
        self.setFixedSize(300, 300)

        layout = QVBoxLayout()
        if key_prompt_type:
            self.label = QLabel('No API key. Please enter one:'
                                '<a href="https://krdict.korean.go.kr/openApi/openApiRegister">Get API Key</a>')
        else:
            self.label = QLabel('Invalid API key. Please enter again:'
                                '<a href="https://krdict.korean.go.kr/openApi/openApiRegister">Get API Key</a>')

        self.label.setOpenExternalLinks(True)
        layout.addWidget(self.label)

        self.input_field = QLineEdit(self)
        layout.addWidget(self.input_field)

        self.submit_button = QPushButton('Ok', self)
        self.submit_button.clicked.connect(self.save_input)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def save_input(self):
        user_input = self.input_field.text()
        self.save_to_config(user_input)
        self.close()

    def save_to_config(self, user_input):
        CONFIG['api_key'] = user_input
        mw.addonManager.writeConfig(__name__, CONFIG)


def api_key_prompt():
    global key_prompt_type
    InputDialog().exec()


def check_for_api_key(func):
    def wrapper(self, *args, **kwargs):
        global key_prompt_type
        while not CONFIG.get('api_key'):
            key_prompt_type = True
            api_key_prompt()
        return func(self, *args, **kwargs)

    return wrapper


def get_text(result, tag, is_hanja=False):
    element = result.find(tag).text
    if element is not None:
        if is_hanja:
            if not bool(re.fullmatch(r'([가-힣]+|[▼←]+|[a-zA-Z]+|\s+)+', element)):
                element = re.sub(replacement_pattern_and_char[0], replacement_pattern_and_char[1], element)
            else:
                element = ''
        return element
    else:
        return ''


@check_for_api_key
def dictionary(word):
    global key_prompt_type
    parameters = {
        'key': CONFIG['api_key'],
        'q': word,
        'advanced': 'y',
    }

    try:
        response = requests.get(URL, params=parameters)
        response.raise_for_status()
    except requests.RequestException as e:
        showInfo(f'An error occurred while making the request: {e}')
        return '', None
    else:
        root = eT.fromstring(response.content)
        error = root.find('error_code')
        while error is not None:
            key_prompt_type = False
            api_key_prompt()

        results = root.findall('item')
        if not results:
            return '', None

        entries = []
        for result in results:
            entries.append({
                'target_code': get_text(result, 'target_code'),
                'hanja': get_text(result, 'origin', True),
                'pos': pos.get(get_text(result, 'pos'))
            })

        entries = sorted(entries, key=lambda x: x['target_code'])
        return entries[0]['hanja'], entries[0]['pos']
