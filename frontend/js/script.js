document.addEventListener('DOMContentLoaded', () => {
    // DOM 요소 가져오기
    const originalTextInput = document.getElementById('original-text');
    const charCounter = document.getElementById('char-counter');
    const targetSelect = document.getElementById('target-select');
    const convertBtn = document.getElementById('convert-btn');
    const outputTextContainer = document.getElementById('output-text');
    const copyBtn = document.getElementById('copy-btn');

    const MAX_CHARS = 500;
    const API_URL = 'http://127.0.0.1:5001/api/convert';

    // 글자 수 카운터 업데이트 이벤트 리스너
    originalTextInput.addEventListener('input', () => {
        const currentChars = originalTextInput.value.length;
        charCounter.textContent = `${currentChars} / ${MAX_CHARS}`;
        
        if (currentChars > MAX_CHARS) {
            charCounter.style.color = 'var(--error-color)';
            convertBtn.disabled = true;
        } else {
            charCounter.style.color = 'var(--placeholder-color)';
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
        if (textToCopy && textToCopy !== '이곳에 변환 결과가 표시됩니다.') {
            navigator.clipboard.writeText(textToCopy).then(() => {
                alert('클립보드에 복사되었습니다!');
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
            convertBtn.innerHTML = '<span class="spinner"></span>변환 중...';
        } else {
            convertBtn.disabled = false;
            convertBtn.innerHTML = '변환하기';
        }
    }

    // 결과를 화면에 표시하는 함수
    function displayResult(text, isError = false) {
        outputTextContainer.innerHTML = ''; // 기존 내용 삭제
        const resultParagraph = document.createElement('p');
        resultParagraph.innerText = text;
        if (isError) {
            resultParagraph.style.color = 'var(--error-color)';
        }
        outputTextContainer.appendChild(resultParagraph);
        copyBtn.disabled = isError;
    }
});

