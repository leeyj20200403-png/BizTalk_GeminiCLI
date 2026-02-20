document.addEventListener('DOMContentLoaded', () => {
    // DOM 요소 가져오기
    const originalTextInput = document.getElementById('original-text');
    const charCounter = document.getElementById('char-counter');
    const targetSelect = document.getElementById('target-select');
    const convertBtn = document.getElementById('convert-btn');
    const outputTextContainer = document.getElementById('output-text');
    const copyBtn = document.getElementById('copy-btn');

    const MAX_CHARS = 500;
    const API_URL = '/api/convert'; // backend에서 serve하므로 상대 경로 사용 가능

    // 글자 수 카운터 업데이트 이벤트 리스너
    originalTextInput.addEventListener('input', () => {
        const currentChars = originalTextInput.value.length;
        charCounter.textContent = `${currentChars} / ${MAX_CHARS}`;
        
        if (currentChars > MAX_CHARS) {
            charCounter.classList.add('text-red-500');
            charCounter.classList.remove('text-gray-400');
            convertBtn.disabled = true;
        } else {
            charCounter.classList.remove('text-red-500');
            charCounter.classList.add('text-gray-400');
            convertBtn.disabled = false;
        }
    });

    // 변환하기 버튼 클릭 이벤트 리스너
    convertBtn.addEventListener('click', async () => {
        const text = originalTextInput.value.trim();
        const target = targetSelect.value;

        if (!text) {
            alert('변환할 내용을 입력해주세요.');
            return;
        }

        if (text.length > MAX_CHARS) {
            alert(`입력 내용은 ${MAX_CHARS}자를 초과할 수 없습니다.`);
            return;
        }

        // 로딩 상태 시작
        setLoadingState(true);

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text, target }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || '알 수 없는 오류가 발생했습니다.');
            }

            const data = await response.json();
            displayResult(data.converted_text);

        } catch (error) {
            console.error('Error:', error);
            displayResult(`오류가 발생했습니다: ${error.message}`, true);
        } finally {
            // 로딩 상태 종료
            setLoadingState(false);
        }
    });

    // 복사하기 버튼 클릭 이벤트 리스너
    copyBtn.addEventListener('click', () => {
        const textToCopy = outputTextContainer.innerText;
        // placeholder 텍스트인지 확인
        if (textToCopy && !outputTextContainer.querySelector('.italic')) {
            navigator.clipboard.writeText(textToCopy).then(() => {
                const originalText = copyBtn.innerText;
                copyBtn.innerText = '복사됨!';
                copyBtn.classList.add('bg-green-50', 'text-green-600', 'border-green-200');
                
                setTimeout(() => {
                    copyBtn.innerText = originalText;
                    copyBtn.classList.remove('bg-green-50', 'text-green-600', 'border-green-200');
                }, 2000);
            }).catch(err => {
                console.error('복사 실패:', err);
                alert('복사에 실패했습니다.');
            });
        }
    });

    // 로딩 상태를 설정하는 함수
    function setLoadingState(isLoading) {
        if (isLoading) {
            convertBtn.disabled = true;
            convertBtn.innerHTML = '<span class="spinner"></span> <span>변환 중...</span>';
            // 결과 영역 초기화
            outputTextContainer.innerHTML = '<p class="text-gray-400 italic animate-pulse">변환 중입니다. 잠시만 기다려주세요...</p>';
            copyBtn.disabled = true;
        } else {
            convertBtn.disabled = false;
            convertBtn.innerHTML = '<span>변환하기</span>';
        }
    }

    // 결과를 화면에 표시하는 함수
    function displayResult(text, isError = false) {
        outputTextContainer.innerHTML = ''; // 기존 내용 삭제
        const resultParagraph = document.createElement('p');
        resultParagraph.innerText = text;
        
        if (isError) {
            resultParagraph.className = 'text-red-500 font-medium';
            copyBtn.disabled = true;
        } else {
            resultParagraph.className = 'text-gray-800 leading-relaxed';
            copyBtn.disabled = false;
        }
        
        outputTextContainer.appendChild(resultParagraph);
    }
});
