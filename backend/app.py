import os
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Flask 앱 초기화
app = Flask(__name__, static_folder=None)
CORS(app)

# Groq API 클라이언트 초기화
groq_client = None
try:
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        logger.warning("GROQ_API_KEY 환경 변수가 설정되지 않았습니다.")
    else:
        groq_client = Groq(api_key=groq_api_key)
except Exception as e:
    logger.error(f"Groq 클라이언트 초기화 오류: {e}")

# 대상별 시스템 프롬프트 정의 (키값은 영문 사용)
SYSTEM_PROMPTS = {
    "Upward": (
        "당신은 비즈니스 커뮤니케이션 전문가입니다. "
        "사용자가 입력한 일상적인 문장을 상사에게 보고하기 위한 '격식 있고 정중한 비즈니스 말투'로 변환해 주세요. "
        "반드시 '하십시오체' 또는 '해요체'를 적절히 섞어 예의를 갖추되, 보고의 핵심 내용이 명확히 전달되도록 구성해야 합니다. "
        "불필요한 미사여구는 줄이고, 전문성이 느껴지는 단어를 선택해 주세요."
    ),
    "Lateral": (
        "당신은 비즈니스 커뮤니케이션 전문가입니다. "
        "사용자가 입력한 일상적인 문장을 동료나 타 부서 협업 담당자에게 전달하기 위한 '전문적이면서도 유연한 업무 말투'로 변환해 주세요. "
        "상호 존중의 태도를 유지하면서, 요청 사항이나 마감 기한 등을 명확하고 정중하게 표현해야 합니다. "
        "지나치게 딱딱하지 않으면서도 신뢰감을 주는 어조를 사용하세요."
    ),
    "External": (
        "당신은 비즈니스 커뮤니케이션 전문가입니다. "
        "사용자가 입력한 문장을 고객사나 외부 파트너에게 전달하기 위한 '매우 공식적이고 신뢰감 있는 비즈니스 어투'로 변환해 주세요. "
        "최대한의 예의(극존칭 포함)를 갖추며, 서비스 마인드가 느껴지는 친절하고 명확한 안내 형식을 취해야 합니다. "
        "회사나 개인의 전문성을 높여줄 수 있는 세련된 문장으로 구성해 주세요."
    )
}

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/convert', methods=['POST'])
def convert_tone():
    """
    사용자로부터 텍스트와 변환 대상을 받아 말투를 변환합니다.
    PRD에 따라 moonshotai/kimi-k2-instruct-0905 모델을 사용합니다.
    """
    if not request.is_json:
        return jsonify({"error": "요청 형식이 JSON이 아닙니다."}), 400

    data = request.get_json()
    original_text = data.get('text', '').strip()
    target = data.get('target')

    if not original_text or not target:
        return jsonify({"error": "필수 파라미터(text, target)가 누락되었습니다."}), 400

    if target not in SYSTEM_PROMPTS:
        return jsonify({"error": f"유효하지 않은 변환 대상입니다: {target}"}), 400
    
    if not groq_client:
        return jsonify({"error": "AI 서비스가 초기화되지 않았습니다. API 키를 확인해주세요."}), 500

    logger.info(f"변환 요청 접수 - 대상: {target}, 텍스트 길이: {len(original_text)}")

    try:
        # PRD 명시 모델: moonshotai/kimi-k2-instruct-0905
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPTS[target],
                },
                {
                    "role": "user",
                    "content": original_text,
                }
            ],
            model="moonshotai/kimi-k2-instruct-0905",
            temperature=0.3, # 비즈니스 말투이므로 변동성을 낮춤
            max_tokens=1000,
        )
        converted_text = chat_completion.choices[0].message.content.strip()
        
        logger.info("변환 성공")
        return jsonify({
            "original_text": original_text,
            "converted_text": converted_text,
            "target": target
        })
    except Exception as e:
        logger.error(f"Groq API 호출 중 오류 발생: {e}")
        return jsonify({"error": f"AI 변환 서비스 오류: {str(e)}"}), 500

# 정적 파일 서빙 (기존 로직 유지)
@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    if ".." in path:
        return "Path traversal attempt detected", 400
    return send_from_directory('../frontend', path)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
