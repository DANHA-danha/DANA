import os
import base64
import tempfile
import streamlit as st
from report_generator import (
    extract_notebook_content,
    extract_chart_data,
    generate_report,
    setup_korean_font,
    export_docx,
    export_xlsx,
)

def get_logo_base64():
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "nice_logo.svg")
    with open(logo_path, "r") as f:
        return base64.b64encode(f.read().encode()).decode()

st.set_page_config(
    page_title="DANA - 데이터 분석 보고서 자동 생성",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

LOGO_B64 = get_logo_base64()

# ── CSS ──
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

    /* 전체 */
    .stApp { background: #F5F6FA; font-family: 'Pretendard', sans-serif; }
    .block-container { max-width: 1100px; padding-top: 0.5rem; padding-bottom: 2rem; }
    [data-testid="collapsedControl"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    header[data-testid="stHeader"] { display: none !important; }

    /* ── 헤더 ── */
    .top-bar {
        display: flex; justify-content: space-between; align-items: center;
        padding: 14px 0; border-bottom: 1px solid #E5E7EB; margin-bottom: 28px;
    }
    .top-bar-left { display: flex; align-items: center; gap: 14px; }
    .logo-text { font-size: 1.5rem; font-weight: 800; color: #111827; letter-spacing: -0.5px; }
    .logo-sub { font-size: 0.82rem; color: #9CA3AF; font-weight: 400; }
    .nice-logo { height: 38px; width: auto; }

    /* ── 히어로 ── */
    .hero {
        background: linear-gradient(135deg, #ECEEFB 0%, #F3F1FF 50%, #EDE9FE 100%);
        border-radius: 20px; padding: 44px 40px 36px; margin-bottom: 32px;
        display: flex; justify-content: space-between; align-items: flex-start; gap: 40px;
    }
    .hero-left { flex: 1; }
    .hero-right { flex: 0 0 320px; }
    .hero-badge {
        display: inline-block; background: white; border: 1px solid #C7D2FE;
        border-radius: 20px; padding: 5px 16px; font-size: 0.82rem;
        color: #6366F1; font-weight: 600; margin-bottom: 16px;
    }
    .hero-title { font-size: 1.9rem; font-weight: 800; color: #111827; line-height: 1.35; margin-bottom: 12px; }
    .hero-accent { color: #6366F1; }
    .hero-desc { font-size: 0.92rem; color: #6B7280; line-height: 1.7; margin-bottom: 24px; }

    /* 히어로 우측 목업 */
    .hero-mockup {
        background: white; border-radius: 16px; padding: 20px 22px;
        box-shadow: 0 4px 24px rgba(99,102,241,0.10); border: 1px solid #E0E0EF;
    }
    .mockup-badge {
        display: inline-block; background: #6366F1; color: white;
        font-size: 0.65rem; font-weight: 700; padding: 3px 10px;
        border-radius: 6px; margin-bottom: 8px;
    }
    .mockup-title { font-size: 0.85rem; font-weight: 700; color: #111827; margin-bottom: 14px; }
    .mockup-bars { display: flex; gap: 6px; align-items: flex-end; height: 48px; margin-bottom: 10px; }
    .mockup-bar { border-radius: 4px 4px 0 0; width: 18px; }
    .mockup-line { height: 36px; margin-bottom: 12px; position: relative; }
    .mockup-line svg { width: 100%; height: 100%; }
    .mockup-done {
        display: flex; align-items: center; gap: 8px;
        margin-top: 10px; padding-top: 10px; border-top: 1px solid #F3F4F6;
    }
    .mockup-done-icon {
        width: 22px; height: 22px; border-radius: 50%; background: #22C55E;
        display: flex; align-items: center; justify-content: center;
        color: white; font-size: 0.7rem; font-weight: 700;
    }
    .mockup-done-text { font-size: 0.78rem; color: #6B7280; font-weight: 600; }

    /* 기능 카드 */
    .feat-row { display: flex; gap: 14px; margin-top: 4px; }
    .feat-card {
        background: white; border-radius: 14px; padding: 18px 16px;
        flex: 1; border: 1px solid #E5E7EB;
    }
    .feat-icon {
        width: 40px; height: 40px; border-radius: 10px; background: #F3F4F6;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.2rem; margin-bottom: 10px;
    }
    .feat-title { font-weight: 700; font-size: 0.88rem; color: #111827; margin-bottom: 4px; }
    .feat-desc { font-size: 0.78rem; color: #9CA3AF; line-height: 1.45; }

    /* ── 사용 방법 ── */
    .section-hd { text-align: center; margin: 28px 0 18px; }
    .section-title { font-size: 1.25rem; font-weight: 800; color: #111827; }
    .section-sub { font-size: 0.85rem; color: #9CA3AF; margin-top: 4px; }
    .steps { display: flex; gap: 14px; margin-bottom: 32px; }
    .step {
        background: white; border-radius: 16px; padding: 22px 16px 18px;
        flex: 1; text-align: center; border: 1px solid #E5E7EB; position: relative;
    }
    .step-n {
        position: absolute; top: 10px; left: 10px;
        width: 24px; height: 24px; border-radius: 7px; background: #6366F1;
        color: white; font-weight: 700; font-size: 0.75rem;
        display: flex; align-items: center; justify-content: center;
    }
    .step-icon { font-size: 1.8rem; margin: 6px 0 8px; }
    .step-title { font-weight: 700; font-size: 0.88rem; color: #111827; margin-bottom: 4px; }
    .step-desc { font-size: 0.76rem; color: #9CA3AF; line-height: 1.4; }
    .step-arr {
        position: absolute; right: -14px; top: 50%; transform: translateY(-50%);
        color: #D1D5DB; font-size: 1.1rem; font-weight: 700;
    }

    /* ── 3컬럼 패널 (st.container border) ── */
    div[data-testid="stColumn"] {
        display: flex; flex-direction: column;
    }
    div[data-testid="stColumn"] > div {
        flex: 1; display: flex; flex-direction: column;
    }
    div[data-testid="stColumn"] > div > div {
        flex: 1; display: flex; flex-direction: column;
    }
    div[data-testid="stColumn"] > div > div > div[data-testid="stVerticalBlockBorderWrapper"] {
        background: white; border-radius: 16px !important;
        border: 1px solid #E5E7EB !important;
        flex: 1;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        padding: 20px 22px !important;
    }
    .panel-num {
        font-size: 0.95rem; font-weight: 700; color: #111827; margin-bottom: 10px;
    }

    /* 파일 업로더 */
    div[data-testid="stFileUploader"] label { font-size: 0px !important; height: 0; }
    .file-info-box {
        background: #F9FAFB; border-radius: 10px; padding: 12px 14px;
        margin-top: 14px; font-size: 0.8rem; color: #6B7280; line-height: 1.6;
    }

    /* 라디오 */
    .stRadio > label { font-size: 0px !important; height: 0; }
    .stRadio > div { gap: 0 !important; }
    .stRadio > div > label {
        padding: 12px 14px !important;
        border: 1px solid #E5E7EB !important; border-radius: 10px !important;
        margin-bottom: 7px !important; transition: all 0.15s;
    }
    .stRadio > div > label:hover { border-color: #A5B4FC !important; background: #F5F3FF !important; }
    .stRadio > div > label[data-checked="true"] { border-color: #6366F1 !important; background: #EEF2FF !important; }

    /* 체크박스 */
    .stCheckbox { margin-top: 2px; }
    .stCheckbox label span { font-size: 0.88rem !important; }

    /* 셀렉트박스 / 텍스트 입력 */
    .stTextInput > label, .stSelectbox > label {
        font-size: 0.82rem !important; font-weight: 600 !important; color: #374151 !important;
    }
    .stTextInput input { border-radius: 10px !important; }
    .stSelectbox > div > div { border-radius: 10px !important; }

    /* 생성 버튼 */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366F1, #7C3AED) !important;
        border: none !important; border-radius: 14px !important;
        padding: 16px 0 !important; font-size: 1.05rem !important;
        font-weight: 700 !important; letter-spacing: 0.5px;
    }
    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #4F46E5, #6D28D9) !important;
    }

    /* 결과 헤더 */
    .result-hd {
        background: linear-gradient(135deg, #6366F1, #8B5CF6);
        color: white; border-radius: 16px; padding: 20px 28px; margin: 12px 0;
    }
    .result-hd-title { font-size: 1.2rem; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════
# 헤더
# ════════════════════════════════════════
st.markdown("""
<div class="top-bar">
    <div class="top-bar-left">
        <span class="logo-text">DANA</span>
        <span class="logo-sub">Data Analysis NICE Automation</span>
    </div>
    <img src="data:image/svg+xml;base64,""" + LOGO_B64 + """" class="nice-logo"/>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════
# 히어로
# ════════════════════════════════════════
st.markdown("""
<div class="hero">
    <div class="hero-left">
        <span class="hero-badge">분석은 당신이, 보고서는 DANA가</span>
        <div class="hero-title">데이터 분석 결과를 <span class="hero-accent">AI 보고서로 자동 완성</span></div>
        <p class="hero-desc">
            .ipynb 파일을 업로드하면 분석 내용을 이해하고, 분석 보고서를 자동으로 생성해 드립니다.
        </p>
        <div class="feat-row">
            <div class="feat-card">
                <div class="feat-icon">🤖</div>
                <div class="feat-title">AI 기반 분석 이해</div>
                <div class="feat-desc">Notebook의 코드와 결과를<br>AI가 정확히 이해합니다.</div>
            </div>
            <div class="feat-card">
                <div class="feat-icon">📋</div>
                <div class="feat-title">맞춤형 보고서 생성</div>
                <div class="feat-desc">원하는 보고서 유형에 맞춰<br>구조화된 보고서를 생성합니다.</div>
            </div>
            <div class="feat-card">
                <div class="feat-icon">⬇️</div>
                <div class="feat-title">즉시 확인 & 다운로드</div>
                <div class="feat-desc">미리보기를 확인하고<br>다양한 형식으로 다운로드하세요.</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════
# 사용 방법
# ════════════════════════════════════════
st.markdown("""
<div class="section-hd">
    <div class="section-title">사용 방법</div>
</div>
<div class="steps">
    <div class="step">
        <div class="step-n">1</div>
        <div class="step-icon">📤</div>
        <div class="step-title">.ipynb 파일 업로드</div>
        <div class="step-desc">분석이 완료된 Jupyter Notebook<br>파일을 업로드하세요.</div>
        <div class="step-arr">›</div>
    </div>
    <div class="step">
        <div class="step-n">2</div>
        <div class="step-icon">📝</div>
        <div class="step-title">보고서 유형 선택</div>
        <div class="step-desc">원하는 보고서 유형과 포함할<br>항목을 선택하세요.</div>
        <div class="step-arr">›</div>
    </div>
    <div class="step">
        <div class="step-n">3</div>
        <div class="step-icon">✨</div>
        <div class="step-title">보고서 생성</div>
        <div class="step-desc">DANA가 분석 내용을 이해하고<br>보고서를 자동으로 생성합니다.</div>
        <div class="step-arr">›</div>
    </div>
    <div class="step">
        <div class="step-n">4</div>
        <div class="step-icon">👁️</div>
        <div class="step-title">미리보기 & 다운로드</div>
        <div class="step-desc">생성된 보고서를 미리 확인하고<br>원하는 형식으로 다운로드하세요.</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════
# 3컬럼 패널
# ════════════════════════════════════════
col1, col2, col3 = st.columns([1, 1, 1], gap="medium")

# ── 1. 파일 업로드 ──
with col1:
    with st.container(border=True):
        st.markdown('<div class="panel-num">1. .ipynb 파일 업로드</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("파일", type=["ipynb"], label_visibility="collapsed")
        if uploaded_file:
            size_kb = uploaded_file.size / 1024
            st.success(f"**{uploaded_file.name}**  ·  {size_kb:.1f} KB")
        st.markdown("""
        <div class="file-info-box">
            ✦ <b>지원 파일 형식</b><br>
            • Jupyter Notebook (.ipynb)<br>
            • 폴더 (Notebook이 포함된 폴더)<br>
            • 파일 크기 제한: 100MB
        </div>
        """, unsafe_allow_html=True)

# ── 2. 보고서 유형 선택 ──
with col2:
    with st.container(border=True):
        st.markdown('<div class="panel-num">2. 보고서 유형 선택</div>', unsafe_allow_html=True)
        report_type = st.radio(
            "유형",
            ["분석 요약 보고서", "경영진 보고서", "기술 분석 보고서"],
            captions=[
                "핵심 인사이트와 주요 결과를 간단명료하게 요약합니다.",
                "경영진을 위한 핵심 KPI와 전략적 제언을 중심으로 구성합니다.",
                "분석 방법, 모델, 기술적 세부사항을 상세히 설명합니다.",
            ],
            label_visibility="collapsed",
        )

# ── 3. 보고서 설정 ──
with col3:
    with st.container(border=True):
        st.markdown('<div class="panel-num">3. 보고서 설정</div>', unsafe_allow_html=True)
        report_title = st.text_input("보고서 제목", placeholder="2024년 1분기 매출 분석 결과 보고서")
        analysis_purpose = st.selectbox("분석 목적", [
            "매출 트렌드 파악 및 성장 전략 수립",
            "리스크 분석 및 대응 방안",
            "고객 행동 분석",
            "운영 효율성 검토",
            "직접 입력",
        ])
        target_audience = st.selectbox("대상 독자", ["경영진", "팀 내부", "타부서 담당자", "외부 파트너"])
        report_length = st.selectbox("보고서 길이", [
            "짧게 (1-2 페이지)",
            "중간 (3-5 페이지)",
            "상세 (5-10 페이지)",
        ])

# ════════════════════════════════════════
# 생성 버튼
# ════════════════════════════════════════
st.markdown("")
generate_clicked = st.button("✨  보고서 생성하기", type="primary", use_container_width=True)

# ════════════════════════════════════════
# 생성 로직
# ════════════════════════════════════════
TYPE_MAP = {
    "분석 요약 보고서": "분석요약",
    "기술 분석 보고서": "기술분석",
    "경영진 보고서": "경영진",
}

if generate_clicked:
    if not uploaded_file:
        st.error("📎 .ipynb 파일을 먼저 업로드해주세요.")
    else:
        with tempfile.NamedTemporaryFile(suffix=".ipynb", delete=False) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        try:
            mapped = TYPE_MAP[report_type]
            chart_figures = []
            datasets = []
            report_text = ""

            with st.status("DANA가 보고서를 생성하고 있습니다...", expanded=True) as status:
                st.write("📖 노트북 분석 중...")
                content = extract_notebook_content(tmp_path)
                st.write(f"✅ 노트북 읽기 완료 ({len(content):,}자)")

                st.write("📊 시각화 생성 중...")
                datasets = extract_chart_data(tmp_path)
                if datasets:
                    setup_korean_font()
                    import matplotlib.pyplot as plt
                    palette = ['#6366F1','#818CF8','#A5B4FC','#C7D2FE','#DDD6FE','#EDE9FE','#F5F3FF']
                    accent = ['#4338CA','#4F46E5','#6366F1','#818CF8','#A5B4FC','#C7D2FE','#DDD6FE']
                    for ds in datasets:
                        fig, ax = plt.subplots(figsize=(10, 5))
                        n = len(ds['labels'])
                        if ds['unit'] == '%':
                            bars = ax.barh(ds['labels'][::-1], ds['values'][::-1],
                                           color=accent[:n][::-1], height=0.6, edgecolor='white')
                            for bar, val in zip(bars, ds['values'][::-1]):
                                ax.text(bar.get_width()+0.1, bar.get_y()+bar.get_height()/2,
                                        f'{val}%', va='center', fontsize=11, fontweight='bold')
                            ax.set_xlabel('%', fontsize=11)
                        elif '월별' in ds['title'] or '추이' in ds['title']:
                            ax.plot(ds['labels'], ds['values'], marker='o', color='#6366F1',
                                    linewidth=2.5, markersize=8, markerfacecolor='white',
                                    markeredgecolor='#6366F1', markeredgewidth=2)
                            ax.fill_between(ds['labels'], ds['values'], alpha=0.08, color='#6366F1')
                            for x, y in zip(ds['labels'], ds['values']):
                                ax.text(x, y+max(ds['values'])*0.02, f'{y:,.0f}',
                                        ha='center', va='bottom', fontsize=10, fontweight='bold')
                            ax.set_ylabel('건', fontsize=11)
                        else:
                            bars = ax.bar(ds['labels'], ds['values'],
                                          color=palette[:n], width=0.6, edgecolor='white')
                            for bar, val in zip(bars, ds['values']):
                                ax.text(bar.get_x()+bar.get_width()/2,
                                        bar.get_height()+max(ds['values'])*0.01,
                                        f'{val:,.0f}{ds["unit"]}',
                                        ha='center', va='bottom', fontsize=10, fontweight='bold')
                        ax.set_title(ds['title'], fontsize=14, fontweight='bold', pad=15)
                        ax.spines[['top','right']].set_visible(False)
                        ax.tick_params(labelsize=10)
                        fig.tight_layout()
                        chart_figures.append(fig)
                    st.write(f"✅ 차트 {len(chart_figures)}개 완료")

                st.write(f"📝 {report_type} 작성 중...")
                report_text = generate_report(
                    content, mapped,
                    title=report_title,
                    purpose=analysis_purpose,
                    audience=target_audience,
                    length=report_length,
                )
                st.write("✅ 보고서 작성 완료")

                status.update(label="✅ 보고서 생성 완료!", state="complete", expanded=False)

            # ── 결과 ──
            title_display = report_title if report_title else uploaded_file.name.replace('.ipynb', '')
            st.markdown(f"""
            <div class="result-hd">
                <div class="result-hd-title">📄 {title_display} — {report_type}</div>
            </div>
            """, unsafe_allow_html=True)

            if chart_figures:
                st.subheader("📊 시각화 자료")
                for idx in range(0, len(chart_figures), 2):
                    cols = st.columns(2)
                    for j, col in enumerate(cols):
                        if idx + j < len(chart_figures):
                            with col:
                                st.pyplot(chart_figures[idx + j])
                st.divider()

            st.subheader("📄 보고서 본문")
            st.markdown(report_text)
            st.divider()

            st.write("📦 다운로드 파일 준비 중...")
            docx_data = export_docx(report_text, chart_figures=chart_figures)
            xlsx_data = export_xlsx(report_text, datasets=datasets if datasets else None)

            dl1, dl2 = st.columns(2)
            with dl1:
                st.download_button("⬇️  Word (.docx) 다운로드", docx_data,
                                   f"DANA_{mapped}_보고서.docx",
                                   "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                   use_container_width=True)
            with dl2:
                st.download_button("⬇️  Excel (.xlsx) 다운로드", xlsx_data,
                                   f"DANA_{mapped}_보고서.xlsx",
                                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                   use_container_width=True)

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
        finally:
            os.unlink(tmp_path)
