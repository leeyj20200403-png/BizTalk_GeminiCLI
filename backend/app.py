import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# Flask 앱 초기화
# static_folder를 명시적으로 None으로 설정하여 Flask의 기본 정적 파일 서빙을 비활성화하고 수동으로 처리
app = Flask(__name__, static_folder=None)
# 모든 도메인에서 오는 요청을 허용하도록 CORS 설정 (개발 목적으로 모든 오리진 허용)
CORS(app)

# Groq API 클라이언트 초기화
# API 키는 환경 변수 'GROQ_API_KEY'에서 자동으로 읽어옵니다.
groq_client = None
try:
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        print("경고: GROQ_API_KEY 환경 변수가 설정되지 않았습니다. Groq API 호출이 실패할 수 있습니다.")
    else:
        groq_client = Groq(api_key=groq_api_key)
except Exception as e:
    print(f"Groq 클라이언트 초기화 오류: {e}")
    groq_client = None

# 대상별 시스템 프롬프트 정의
SYSTEM_PROMPTS = {
    "상사": "당신은 한국어 비즈니스 커뮤니케이션 전문가입니다. 다음 문장을 상사에게 보고하기에 적합한 매우 정중하고 격식 있는 존댓말과 경어를 사용하여 변환해주세요. 간결하고 명확하게 보고하는 형식으로 작성하며, 존경의 의미를 담아주세요.",
    "타팀 동료": "당신은 한국어 비즈니스 커뮤니케이션 전문가입니다. 다음 문장을 타팀 동료에게 협업을 요청하거나 정보를 공유하기에 적합한 중립적이지만 예의바른 업무 말투로 변환해주세요. 친근하면서도 전문적인 어조를 유지하며, 요청 사항을 명확히 전달해 주세요.",
    "고객": "당신은 한국어 비즈니스 커뮤니케이션 전문가입니다. 다음 문장을 고객에게 전달하기에 적합한 매우 공식적이고 정중한 비즈니스 어투로 변환해주세요. 최대한의 존중과 신뢰를 표현하며, 명확하고 친절하게 안내하는 형식으로 작성해 주세요."
}

# 서비스 상태 확인을 위한 엔드포인트
@app.route('/health', methods=['GET'])
def health_check():
    """서비스가 정상적으로 실행 중인지 확인합니다."""
    return jsonify({"status": "healthy"}), 200

# 말투 변환을 위한 API 엔드포인트
@app.route('/api/convert', methods=['POST'])
def convert_tone():
    """
    사용자로부터 텍스트와 변환 대상을 받아 말투를 변환합니다.
    """
    if not request.is_json:
        return jsonify({"error": "요청 형식이 JSON이 아닙니다."}), 400

    data = request.get_json()
    original_text = data.get('text')
    target = data.get('target')

    if not original_text or not target:
        return jsonify({"error": "필수 파라미터(text, target)가 누락되었습니다."}), 400

    if target not in SYSTEM_PROMPTS:
        return jsonify({"error": "유효하지 않은 변환 대상입니다."}), 400
    
    if not groq_client:
        return jsonify({"error": "AI 서비스가 초기화되지 않았습니다. API 키를 확인해주세요."}), 500

    system_prompt = SYSTEM_PROMPTS[target]
    
    print(f"입력 텍스트: {original_text[:50]}...") # 긴 텍스트의 경우 일부만 출력
    print(f"변환 대상: {target}")
    print(f"적용 프롬프트: {system_prompt[:50]}...") # 긴 프롬프트의 경우 일부만 출력

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": original_text,
                }
            ],
            model="llama3-8b-8192", # 필요에 따라 다른 Groq 모델 사용 가능
            temperature=0.7, # 창의성 조절 (0.0: 보수적, 1.0: 창의적)
            max_tokens=500, # 응답 최대 길이
        )
        converted_text = chat_completion.choices[0].message.content
        print(f"Groq API 응답: {converted_text[:50]}...") # 응답 일부 출력
        
        return jsonify({
            "original_text": original_text,
            "converted_text": converted_text,
            "target": target
        })
    except Exception as e:
        print(f"Groq API 호출 중 오류 발생: {e}")
        return jsonify({"error": f"AI 변환 서비스 오류: {str(e)}"}), 500

# 정적 파일 서빙: 루트 URL (http://127.0.0.1:5000/) 요청 시 index.html 반환
@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

# 정적 파일 서빙: frontend 디렉토리 내의 다른 파일들 (css, js 등) 처리
@app.route('/<path:path>')
def serve_static_files(path):
    # 보안을 위해 '..'와 같은 경로 조작 방지
    if ".." in path:
        return "Path traversal attempt detected", 400
    return send_from_directory('../frontend', path)

# 이 파일이 직접 실행될 때 Flask 개발 서버를 시작합니다.
if __name__ == '__main__':
    # 디버그 모드로 실행, 포트는 5000으로 설정
    app.run(debug=True, port=5001)
