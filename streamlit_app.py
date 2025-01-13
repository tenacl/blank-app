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
    st.title("💰 학생 AI 재정・투자 상담")
    
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px;'>
        <h4>AI 재정・투자 상담 서비스</h4>
        <p>학생들의 재정 상태를 분석하고 맞춤형 재정 관리 및 투자 조언을 제공하는 서비스입니다.</p>
        <p style='color: #ff4b4b;'>※ 이 조언은 참고용이며, 전문적인 재정/투자 자문을 대체할 수 없습니다.</p>
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
        
        col1, col2 = st.columns(2)
        with col1:
            monthly_income = st.number_input("월 수입(용돈+알바 등)", min_value=0, value=50000, step=10000)
            savings = st.number_input("현재 보유 금액", min_value=0, value=100000, step=10000)
        
        with col2:
            monthly_expenses = st.number_input("월 평균 지출", min_value=0, value=30000, step=10000)
            target_amount = st.number_input("목표 금액", min_value=0, value=1000000, step=100000)

        financial_goal = st.text_area(
            "구체적인 재정 목표를 알려주세요",
            placeholder="예시:\n- 단기 목표: 3개월 내 에어팟 구매\n- 중기 목표: 1년 내 노트북 구매\n- 장기 목표: 졸업 전까지 300만원 모으기"
        )

        st.markdown("### 💡 투자 관심 분야")
        investment_interests = st.multiselect(
            "관심있는 투자 분야를 선택해주세요",
            ["주식", "펀드", "적금", "암호화폐", "P2P 투자", "기타"],
            default=["적금"]
        )

        risk_tolerance = st.select_slider(
            "투자 위험 감수 성향",
            options=["매우 보수적", "보수적", "중립적", "공격적", "매우 공격적"],
            value="보수적"
        )

    if st.button("🤖 AI 상담 받기", use_container_width=True):
        if not financial_goal.strip():
            st.warning("⚠️ 재정 목표를 입력해주세요.")
            return

        with st.spinner("🔄 AI가 분석 중입니다..."):
            user_info = f"""
재정 정보:
- 월 수입: {monthly_income:,}원
- 월 지출: {monthly_expenses:,}원
- 현재 보유 금액: {savings:,}원
- 목표 금액: {target_amount:,}원
- 재정 목표: {financial_goal}
- 관심 투자 분야: {', '.join(investment_interests)}
- 투자 성향: {risk_tolerance}
"""

            prompt = f"""다음 학생의 재정 상태와 투자 성향을 분석하고 실용적인 조언을 제공해주세요:

{user_info}

다음 항목들을 포함하여 마크다운 형식으로 응답해주세요:

### 재정 분석 결과

#### 1. 현재 재정 상태 분석
- 수입/지출 균형 분석
- 저축 가능 금액 추정
- 목표 달성 가능성 평가

#### 2. 맞춤형 재정 관리 전략
- 지출 관리 방안
- 저축 전략
- 용돈 관리 팁

#### 3. 투자 전략 제안
- 선택한 투자 분야별 리스크/기회 분석
- 투자 성향에 맞는 포트폴리오 제안
- 초보 투자자를 위한 주의사항

#### 4. 목표 달성 로드맵
- 단기 목표 (3개월 이내)
- 중기 목표 (3개월~1년)
- 장기 목표 (1년 이상)

### 실천 체크리스트
| 실천 항목 | 목표 기한 | 완료 여부 |
|---------|----------|----------|
| 예시 항목 | 1주일 내 | □ |

위 형식으로 구체적인 실천 항목을 최소 5개 제시해주세요.

### 투자 학습 리소스
무료로 이용할 수 있는 투자 학습 자료나 플랫폼도 2-3개 추천해주세요."""

            advice = call_claude(prompt, api_key)
            
            if advice:
                st.markdown("---")
                st.markdown("### 📊 AI 재정・투자 상담 결과")
                with st.container():
                    st.markdown(advice)

if __name__ == "__main__":
    main()
