import streamlit as st
import anthropic
import os

# Claude API 설정
DEFAULT_MODEL = "claude-3-sonnet-20240229"

def load_api_key():
    try:
        return st.secrets["CLAUDE_API_KEY"]
    except Exception as e:
        st.error("API 키를 secrets에서 찾을 수 없습니다.")
        return None

def call_claude(prompt, api_key):
    try:
        client = anthropic.Anthropic(api_key=api_key)
        
        message = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ],
            system="""당신은 학생들의 재정 상태를 분석하고 실용적인 조언을 제공하는 AI 상담사입니다. 
            응답은 반드시 마크다운 형식으로 작성하되, 마크다운 코드가 그대로 보이지 않도록 해주세요.
            항상 ### 수준의 헤딩을 사용하고, 마지막에는 실천 체크리스트를 표 형식으로 제공해주세요."""
        )
        
        return message.content[0].text
    except anthropic.APIError as e:
        st.error(f"API 오류: {str(e)}")
        return None
    except Exception as e:
        st.error(f"예상치 못한 오류: {str(e)}")
        return None

def main():
    st.title("💰 학생 AI 재정 상담")
    
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px;'>
        <h4>AI 재정 상담 서비스</h4>
        <p>학생들의 재정 상태를 분석하고 맞춤형 조언을 제공하는 서비스입니다.</p>
        <p style='color: #ff4b4b;'>※ 이 조언은 참고용이며, 전문적인 재정 자문을 대체할 수 없습니다.</p>
    </div>
    """, unsafe_allow_html=True)

    # API 키 자동 로드
    api_key = load_api_key()
    if not api_key:
        st.error("API 키를 찾을 수 없습니다.")
        return

    # 사용자 정보 입력
    with st.container():
        st.markdown("### 📝 재정 정보 입력")
        user_money_info = st.text_area(
            "현재 재정 상태와 목표를 알려주세요",
            placeholder="예시:\n- 월 용돈: 5만원\n- 현재 보유 금액: 10만원\n- 목표: 노트북 구매",
            height=150
        )

    if st.button("🤖 AI 상담 받기", use_container_width=True):
        if not user_money_info.strip():
            st.warning("⚠️ 재정 상태와 목표를 입력해주세요.")
            return

        with st.spinner("🔄 AI가 분석 중입니다..."):
            prompt = f"""다음 학생의 재정 상태를 분석하고 실용적인 조언을 제공해주세요:

학생 정보:
{user_money_info}

다음 항목들을 포함하여 마크다운 형식으로 응답해주세요:

### 재정 상담 결과

#### 1. 현재 재정 상태 분석

#### 2. 용돈 관리 전략

#### 3. 저축 및 지출 계획

#### 4. 목표 달성을 위한 구체적인 단계

### 실천 체크리스트
아래와 같은 형식으로 실천 체크리스트를 작성해주세요:

| 실천 항목 | 목표 기한 | 완료 여부 |
|---------|----------|----------|
| 예시 항목 | 1주일 내 | □ |

위 형식을 참고하여 최소 5개의 구체적인 실천 항목을 제시해주세요."""

            advice = call_claude(prompt, api_key)
            
            if advice:
                st.markdown("---")
                st.markdown("### 📊 AI 재정 상담 결과")
                # 결과를 카드 형태의 컨테이너에 표시
                with st.container():
                    st.markdown(advice)  # 직접 마크다운으로 표시

if __name__ == "__main__":
    main()
