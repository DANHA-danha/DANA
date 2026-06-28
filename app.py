import os
import base64
import tempfile
import streamlit as st
from report_generator import (
    extract_notebook_content,
    extract_csv_content,
    extract_excel_content,
    extract_csv_chart_data,
    extract_chart_data,
    generate_charts_figures,
    generate_report,
    export_docx,
    export_xlsx,
    export_pptx,
)

def get_logo_base64():
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "nice_logo.svg")
    try:
        with open(logo_path, "r") as f:
            return base64.b64encode(f.read().encode()).decode()
    except FileNotFoundError:
        return ""

st.set_page_config(page_title="DANA", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")
LOGO_B64 = get_logo_base64()

st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
*{font-family:'Pretendard',sans-serif;}
.stApp{background:#F4F6FA;}
.block-container{max-width:1320px;padding:0 1rem 2rem;margin-left:60px;}
[data-testid="collapsedControl"],[data-testid="stToolbar"],[data-testid="stDecoration"],
header[data-testid="stHeader"]{display:none!important;}

/* ── 왼쪽 사이드바 ── */
.sidebar-nav{position:fixed;top:0;left:0;width:52px;height:100vh;background:#1E293B;
  display:flex;flex-direction:column;align-items:center;padding-top:12px;z-index:9999;}
.sidebar-nav .nav-logo{width:32px;height:32px;background:#001489;border-radius:8px;
  display:flex;align-items:center;justify-content:center;margin-bottom:20px;
  font-weight:900;color:white;font-size:14px;}
.sidebar-nav a{text-decoration:none;}
.sidebar-nav .nav-icon{width:36px;height:36px;border-radius:8px;display:flex;
  align-items:center;justify-content:center;margin-bottom:6px;cursor:pointer;
  transition:all .15s;}
.sidebar-nav .nav-icon:hover{background:#334155;}
.sidebar-nav .nav-icon.active{background:#334155;}
.sidebar-nav .nav-icon svg{width:20px;height:20px;}
.sidebar-nav .nav-bottom{margin-top:auto;margin-bottom:16px;}

/* ── 헤더 ── */
.top-hdr{display:flex;justify-content:space-between;align-items:center;
  padding:10px 0;border-bottom:1px solid #E2E8F0;margin-bottom:18px;}
.top-hdr-l{display:flex;align-items:center;gap:16px;}
.top-hdr-logo{font-size:1.5rem;font-weight:900;color:#111827;letter-spacing:-1px;}
.top-hdr-txt{display:flex;flex-direction:column;border-left:1px solid #D1D5DB;padding-left:14px;}
.top-hdr-txt span:first-child{font-size:0.78rem;color:#374151;font-weight:600;}
.top-hdr-txt span:last-child{font-size:0.68rem;color:#9CA3AF;}
.top-hdr-r{display:flex;align-items:center;gap:14px;}
.nice-logo{height:34px;}
.top-icon{width:30px;height:30px;border-radius:50%;background:#F1F5F9;display:flex;
  align-items:center;justify-content:center;font-size:14px;color:#64748B;cursor:pointer;}

/* ── 히어로 ── */
.hero{background:linear-gradient(135deg,#EFF6FF 0%,#DBEAFE 40%,#E0E7FF 100%);
  border-radius:16px;padding:32px 32px 24px;margin-bottom:20px;
  display:flex;justify-content:space-between;align-items:center;gap:24px;position:relative;overflow:hidden;}
.hero::after{content:'';position:absolute;top:-40px;right:-40px;width:300px;height:300px;
  background:radial-gradient(circle,rgba(0,20,137,0.04) 0%,transparent 70%);border-radius:50%;}
.hero-l{flex:1;z-index:1;}
.hero-badge{color:#001489;font-size:0.78rem;font-weight:700;margin-bottom:8px;}
.hero-title{font-size:1.8rem;font-weight:900;color:#111827;line-height:1.3;margin-bottom:8px;}
.hero-accent{color:#001489;}
.hero-desc{font-size:0.82rem;color:#64748B;line-height:1.6;}
.hero-r{flex:0 0 380px;z-index:1;position:relative;}

/* 노트북 목업 */
.laptop{background:#1E293B;border-radius:10px;padding:14px 16px;color:#CBD5E1;
  font-family:'JetBrains Mono','Fira Code',monospace;font-size:0.62rem;line-height:1.5;
  box-shadow:0 8px 24px rgba(0,20,137,0.1);}
.laptop-bar{display:flex;gap:4px;margin-bottom:8px;}
.laptop-dot{width:7px;height:7px;border-radius:50%;}
.kw{color:#93C5FD;}.fn{color:#60A5FA;}.st{color:#86EFAC;}.cm{color:#64748B;}
.chart-pop{position:absolute;top:14px;right:-24px;width:190px;background:white;
  border-radius:10px;padding:12px;box-shadow:0 4px 16px rgba(0,0,0,0.08);border:1px solid #E2E8F0;}
.chart-pop-title{font-size:0.65rem;font-weight:700;color:#111827;margin-bottom:6px;}
.chart-pop svg{width:100%;height:60px;}

/* ── 3컬럼 균등 높이 ── */
div[data-testid="stHorizontalBlock"]{align-items:stretch!important;}
div[data-testid="stColumn"]{flex:1!important;}
div[data-testid="stColumn"]>div,
div[data-testid="stColumn"]>div>div{display:flex!important;flex-direction:column!important;flex:1!important;}
div[data-testid="stColumn"]>div>div>div[data-testid="stVerticalBlockBorderWrapper"]{
  background:white;border-radius:12px!important;border:1px solid #E2E8F0!important;
  flex:1!important;display:flex!important;flex-direction:column!important;}
div[data-testid="stVerticalBlockBorderWrapper"]>div{padding:20px!important;flex:1!important;
  display:flex!important;flex-direction:column!important;}
div[data-testid="stVerticalBlockBorderWrapper"]>div>div[data-testid="stVerticalBlock"]{
  flex:1!important;display:flex!important;flex-direction:column!important;}

.ptitle{font-size:0.85rem;font-weight:700;color:#111827;margin-bottom:8px;display:flex;align-items:center;gap:6px;}
.pnum{background:#001489;color:white;font-size:0.65rem;font-weight:700;
  width:18px;height:18px;border-radius:5px;display:inline-flex;align-items:center;justify-content:center;}

/* 업로더 */
div[data-testid="stFileUploader"] label{font-size:0!important;height:0;}

.file-info{background:#F8FAFC;border-radius:8px;padding:8px 10px;margin-top:8px;margin-bottom:16px;
  font-size:0.72rem;color:#64748B;line-height:1.5;}

/* 라디오 카드 동일 높이 */
.stRadio>div[role="radiogroup"]{gap:8px!important;}
.stRadio>div[role="radiogroup"]>label{
  padding:14px!important;border:1px solid #E2E8F0!important;
  border-radius:10px!important;margin:0!important;transition:all .12s;
  min-height:70px!important;max-height:70px!important;height:70px!important;
  box-sizing:border-box!important;overflow:hidden!important;
  display:flex!important;align-items:center!important;}
.stRadio>div[role="radiogroup"]>label:hover{border-color:#93C5FD!important;background:#EFF6FF!important;}
.stRadio>div[role="radiogroup"]>label[data-checked="true"]{border-color:#001489!important;background:#DBEAFE!important;}

/* 입력 */
.stTextInput>label,.stSelectbox>label{font-size:0.75rem!important;font-weight:600!important;color:#374151!important;}
.stTextInput input{border-radius:8px!important;font-size:0.82rem!important;}
.stSelectbox>div>div{border-radius:8px!important;}

/* 버튼 */
div.stButton>button[kind="primary"]{background:#001489!important;border:none!important;
  border-radius:10px!important;padding:16px 0!important;font-size:1rem!important;font-weight:700!important;}
div.stButton>button[kind="primary"]:hover{background:#001066!important;}
.gen-note{text-align:center;font-size:0.72rem;color:#94A3B8;margin-top:6px;}
.pv-dl{display:flex;align-items:center;justify-content:center;gap:6px;
  border:1px solid #E2E8F0;border-radius:8px;padding:8px;margin-top:10px;
  font-size:0.75rem;font-weight:600;color:#374151;cursor:pointer;}

/* 결과 */
.result-hd{background:#001489;color:white;border-radius:12px;padding:14px 22px;margin:10px 0;}
.result-hd-title{font-size:1.05rem;font-weight:700;}
</style>
""", unsafe_allow_html=True)

import json
import glob

HISTORY_DIR = os.path.join(os.path.dirname(__file__), "history")
os.makedirs(HISTORY_DIR, exist_ok=True)

def save_report_to_disk(title, rtype, text, docx_data, xlsx_data, pptx_data):
    from datetime import datetime as _dt
    ts = _dt.now().strftime('%Y%m%d_%H%M%S')
    base = os.path.join(HISTORY_DIR, ts)
    meta = {'title': title, 'type': rtype, 'time': _dt.now().strftime('%m/%d %H:%M'), 'ts': ts}
    with open(f"{base}_meta.json", 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False)
    with open(f"{base}_report.md", 'w', encoding='utf-8') as f:
        f.write(text)
    with open(f"{base}.docx", 'wb') as f:
        f.write(docx_data)
    with open(f"{base}.xlsx", 'wb') as f:
        f.write(xlsx_data)
    with open(f"{base}.pptx", 'wb') as f:
        f.write(pptx_data)

def load_history():
    metas = sorted(glob.glob(os.path.join(HISTORY_DIR, "*_meta.json")), reverse=True)
    results = []
    for mp in metas:
        with open(mp, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        base = mp.replace('_meta.json', '')
        md_path = f"{base}_report.md"
        if os.path.exists(md_path):
            with open(md_path, 'r', encoding='utf-8') as f:
                meta['text'] = f.read()
        meta['docx_path'] = f"{base}.docx"
        meta['xlsx_path'] = f"{base}.xlsx"
        meta['pptx_path'] = f"{base}.pptx"
        results.append(meta)
    return results

# ── 페이지 라우팅 ──
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'download_history' not in st.session_state:
    st.session_state.download_history = []

page = st.query_params.get("page", "home")
if page in ["home", "history"]:
    st.session_state.page = page

home_active = "active" if st.session_state.page == "home" else ""
hist_active = "active" if st.session_state.page == "history" else ""

st.markdown(f"""
<div class="sidebar-nav">
    <div class="nav-logo">D</div>
    <a href="?page=home">
        <div class="nav-icon {home_active}">
            <svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
        </div>
    </a>
    <a href="?page=history">
        <div class="nav-icon {hist_active}">
            <svg viewBox="0 0 24 24" fill="none" stroke="#94A3B8" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
        </div>
    </a>
</div>
""", unsafe_allow_html=True)

# ── 헤더 ──
st.markdown("""
<div class="top-hdr">
    <div class="top-hdr-l">
        <span class="top-hdr-logo">DANA</span>
        <div class="top-hdr-txt">
            <span>DANA - Data Analysis NICE Automation</span>
            <span>AI 기반 데이터 분석 보고서 자동 생성 플랫폼</span>
        </div>
    </div>
    <div class="top-hdr-r">
        <img src="data:image/svg+xml;base64,""" + LOGO_B64 + """" class="nice-logo"/>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# 히스토리 페이지
# ══════════════════════════════════════════
if st.session_state.page == "history":
    st.markdown('<div style="font-size:1.3rem;font-weight:800;color:#111827;margin-bottom:16px;">📄 보고서 히스토리</div>', unsafe_allow_html=True)
    history = load_history()
    if history:
        for i, rpt in enumerate(history):
            with st.expander(f"📄 {rpt['title']} — {rpt['type']} ({rpt['time']})", expanded=False):
                st.markdown(rpt.get('text', ''))
                d1, d2, d3 = st.columns(3)
                with d1:
                    if os.path.exists(rpt['docx_path']):
                        with open(rpt['docx_path'], 'rb') as f:
                            st.download_button("⬇️ Word", f.read(), os.path.basename(rpt['docx_path']),
                                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                use_container_width=True, key=f"h_docx_{i}")
                with d2:
                    if os.path.exists(rpt['xlsx_path']):
                        with open(rpt['xlsx_path'], 'rb') as f:
                            st.download_button("⬇️ Excel", f.read(), os.path.basename(rpt['xlsx_path']),
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True, key=f"h_xlsx_{i}")
                with d3:
                    if os.path.exists(rpt['pptx_path']):
                        with open(rpt['pptx_path'], 'rb') as f:
                            st.download_button("⬇️ PPT", f.read(), os.path.basename(rpt['pptx_path']),
                                "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                                use_container_width=True, key=f"h_pptx_{i}")
    else:
        st.info("아직 생성된 보고서가 없습니다. 홈에서 보고서를 생성해보세요.")
    st.stop()

# ══════════════════════════════════════════
# 홈 페이지
# ══════════════════════════════════════════

# ── 히어로 ──
st.markdown("""
<div class="hero">
    <div class="hero-l">
        <div class="hero-badge">분석은 당신이, 보고서는 DANA가</div>
        <div class="hero-title">데이터 분석 결과를 <span class="hero-accent">AI 보고서로 자동 완성</span></div>
        <p class="hero-desc">파일을 업로드하면 분석 내용을 이해하여, <br> 비즈니스에 활용 가능한 보고서를 자동으로 생성해 드립니다.</p>
    </div>
    <div class="hero-r">
        <div class="laptop">
            <div class="laptop-bar">
                <div class="laptop-dot" style="background:#EF4444;"></div>
                <div class="laptop-dot" style="background:#F59E0B;"></div>
                <div class="laptop-dot" style="background:#22C55E;"></div>
            </div>
            <span class="kw">import</span> pandas <span class="kw">as</span> pd<br>
            <span class="kw">import</span> matplotlib.pyplot <span class="kw">as</span> plt<br><br>
            <span class="cm"># 데이터 로드</span><br>
            df = pd.<span class="fn">read_csv</span>(<span class="st">'sales_data.csv'</span>)<br><br>
            <span class="cm"># 매출 추이 분석</span><br>
            monthly = df.<span class="fn">groupby</span>('month')['sales'].<span class="fn">sum</span>()<br>
            plt.<span class="fn">figure</span>(figsize=(10, 5))<br>
            monthly.<span class="fn">plot</span>(kind=<span class="st">'line'</span>, marker=<span class="st">'o'</span>)<br>
            plt.<span class="fn">title</span>(<span class="st">'Monthly Sales Trend'</span>)<br>
            plt.<span class="fn">xlabel</span>(<span class="st">'Month'</span>)<br>
            plt.<span class="fn">ylabel</span>(<span class="st">'Sales'</span>)<br>
            plt.<span class="fn">grid</span>(True)<br>
            plt.<span class="fn">show</span>()
        </div>
        <div class="chart-pop">
            <div class="chart-pop-title">Monthly Sales Trend</div>
            <svg viewBox="0 0 170 60" fill="none">
                <polyline points="0,50 28,42 56,45 84,30 112,22 140,10 170,18"
                    stroke="#001489" stroke-width="2" fill="none" stroke-linecap="round"/>
                <polygon points="0,60 0,50 28,42 56,45 84,30 112,22 140,10 170,18 170,60"
                    fill="#001489" opacity="0.06"/>
                <text x="0" y="8" font-size="7" fill="#94A3B8">200K</text>
                <text x="0" y="58" font-size="7" fill="#94A3B8">0</text>
                <text x="5" y="60" font-size="6" fill="#94A3B8">Jan</text>
                <text x="33" y="60" font-size="6" fill="#94A3B8">Feb</text>
                <text x="61" y="60" font-size="6" fill="#94A3B8">Mar</text>
                <text x="89" y="60" font-size="6" fill="#94A3B8">Apr</text>
                <text x="117" y="60" font-size="6" fill="#94A3B8">May</text>
                <text x="148" y="60" font-size="6" fill="#94A3B8">Jun</text>
            </svg>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# 3컬럼
# ══════════════════════════════════════════
c1, c2, c3 = st.columns([1, 1, 1], gap="medium")

# ── 1. 데이터 업로드 ──
with c1:
    with st.container(border=True):
        st.markdown('<div class="ptitle"><span class="pnum">1</span> 데이터 업로드</div>', unsafe_allow_html=True)
        input_mode = st.radio("입력 방식", ["파일 업로드", "텍스트 입력"],
            captions=["ipynb, csv, xlsx, txt 파일을 업로드합니다. ",
                      "분석 결과나 데이터를 직접 붙여넣습니다. "],
            label_visibility="collapsed")
        uploaded_file = None
        text_input_data = ""
        if input_mode == "파일 업로드":
            uploaded_file = st.file_uploader("f", type=["ipynb","csv","xlsx","xls","txt"], label_visibility="collapsed")
            if uploaded_file:
                st.success(f"**{uploaded_file.name}** · {uploaded_file.size/1024:.1f}KB")
        else:
            text_input_data = st.text_area("t", height=130, placeholder="CSV, 분석 결과 등 붙여넣기", label_visibility="collapsed")
        st.markdown("""<div class="file-info">✦ <b>지원 형식</b><br>
            • Jupyter Notebook (.ipynb)<br>• CSV (.csv) · Excel (.xlsx)<br>
            • 텍스트 (.txt) · 직접 붙여넣기</div>""", unsafe_allow_html=True)

# ── 2. 보고서 설정 ──
with c2:
    with st.container(border=True):
        st.markdown('<div class="ptitle"><span class="pnum">2</span> 보고서 설정</div>', unsafe_allow_html=True)
        report_title = st.text_input("보고서 제목", placeholder="2024년 1분기 매출 분석 결과 보고서")
        report_type = st.selectbox("보고서 유형", ["분석 요약 보고서", "경영진 보고서"])
        target_audience = st.selectbox("대상 독자", [
            "팀 내부 (전문 용어 사용 가능, 상세 분석 포함)",
            "외부 공유 (쉽고 친근한 표현, 핵심 위주)"])
        s1, s2 = st.columns(2)
        with s1:
            dept_name = st.text_input("부서", placeholder="나이스화이팀")
        with s2:
            author_name = st.text_input("작성자", placeholder="김단하")

# ── 3. 보고서 생성 ──
with c3:
    with st.container(border=True):
        st.markdown('<div class="ptitle"><span class="pnum">3</span> 보고서 생성</div>', unsafe_allow_html=True)
        st.markdown('<div style="flex:1;"></div>', unsafe_allow_html=True)
        generate_clicked = st.button("✨  보고서 생성하기", type="primary", use_container_width=True)
        st.markdown('<div class="gen-note">생성 시간: 약 30초 ~ 1분</div>', unsafe_allow_html=True)
        if st.session_state.download_history:
            st.markdown("---")
            st.markdown('<div style="font-size:0.75rem;font-weight:700;color:#374151;margin-bottom:6px;">최근 생성 보고서</div>', unsafe_allow_html=True)
            for h in st.session_state.download_history[-3:][::-1]:
                st.markdown(f'<div style="font-size:0.7rem;color:#64748B;padding:4px 0;border-bottom:1px solid #F1F5F9;">📄 {h}</div>', unsafe_allow_html=True)
        st.markdown('<div style="flex:1;"></div>', unsafe_allow_html=True)

# 숨겨진 변수 (제거된 필드 기본값)
analysis_purpose = ""
report_length = "중간 (3-5 페이지)"

# ══════════════════════════════════════════
# 생성 로직
# ══════════════════════════════════════════
TYPE_MAP = {"분석 요약 보고서":"분석요약","경영진 보고서":"경영진"}

if generate_clicked:
    has_input = uploaded_file or text_input_data.strip()
    if not has_input:
        st.error("파일을 업로드하거나 텍스트를 입력해주세요.")
    else:
        tmp_path = None
        try:
            mapped = TYPE_MAP[report_type]
            chart_figures = []
            datasets = []
            report_text = ""

            with st.status("DANA가 보고서를 생성하고 있습니다...", expanded=True) as status:
                if text_input_data.strip():
                    st.write("📖 텍스트 데이터 분석 중...")
                    content = text_input_data.strip()
                    st.write(f"✅ 텍스트 읽기 완료 ({len(content):,}자)")
                elif uploaded_file:
                    fname = uploaded_file.name.lower()
                    suffix = os.path.splitext(fname)[1]
                    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                        tmp.write(uploaded_file.getvalue())
                        tmp_path = tmp.name
                    if fname.endswith('.ipynb'):
                        st.write("📖 노트북 분석 중...")
                        content = extract_notebook_content(tmp_path)
                        st.write(f"✅ 노트북 읽기 완료 ({len(content):,}자)")
                        st.write("📊 시각화 생성 중...")
                        datasets = extract_chart_data(tmp_path)
                    elif fname.endswith('.csv'):
                        st.write("📖 CSV 데이터 분석 중...")
                        content, df = extract_csv_content(tmp_path)
                        st.write(f"✅ CSV 읽기 완료 ({len(content):,}자)")
                        st.write("📊 시각화 생성 중...")
                        if df is not None: datasets = extract_csv_chart_data(df)
                    elif fname.endswith(('.xlsx','.xls')):
                        st.write("📖 Excel 데이터 분석 중...")
                        content, df = extract_excel_content(tmp_path)
                        st.write(f"✅ Excel 읽기 완료 ({len(content):,}자)")
                        st.write("📊 시각화 생성 중...")
                        if df is not None: datasets = extract_csv_chart_data(df)
                    elif fname.endswith('.txt'):
                        st.write("📖 텍스트 파일 분석 중...")
                        with open(tmp_path,'r',encoding='utf-8') as f: content = f.read()
                        st.write(f"✅ 텍스트 읽기 완료 ({len(content):,}자)")
                    else:
                        content = uploaded_file.getvalue().decode('utf-8',errors='ignore')

                if datasets:
                    chart_figures = generate_charts_figures(datasets)
                    st.write(f"✅ 차트 {len(chart_figures)}개 완료")
                st.write(f"📝 {report_type} 작성 중...")
                report_text = generate_report(content, mapped, title=report_title,
                    purpose=analysis_purpose, audience=target_audience, length=report_length)
                st.write("✅ 보고서 작성 완료")
                status.update(label="✅ 보고서 생성 완료!", state="complete", expanded=False)

            title_display = report_title if report_title else (uploaded_file.name.rsplit('.',1)[0] if uploaded_file else "분석 결과")
            from datetime import datetime as _dt
            st.session_state.download_history.append(f"{title_display} — {report_type} ({_dt.now().strftime('%m/%d %H:%M')})")
            st.markdown(f'<div class="result-hd"><div class="result-hd-title">📄 {title_display} — {report_type}</div></div>', unsafe_allow_html=True)

            if chart_figures:
                st.subheader("📊 시각화 자료")
                for idx in range(0, len(chart_figures), 2):
                    cols = st.columns(2)
                    for j, col in enumerate(cols):
                        if idx+j < len(chart_figures):
                            with col: st.pyplot(chart_figures[idx+j])
                st.divider()

            st.subheader("📄 보고서 본문")
            st.markdown(report_text)
            st.divider()

            st.write("📦 다운로드 파일 준비 중...")
            docx_data = export_docx(report_text, chart_figures=chart_figures)
            xlsx_data = export_xlsx(report_text, datasets=datasets if datasets else None)
            pptx_data = export_pptx(report_text, chart_figures=chart_figures,
                title=report_title, purpose=analysis_purpose,
                audience=target_audience, dept=dept_name, author=author_name,
                datasets=datasets if datasets else None)

            save_report_to_disk(title_display, report_type, report_text, docx_data, xlsx_data, pptx_data)

            d1, d2, d3 = st.columns(3)
            with d1:
                st.download_button("⬇️ Word (.docx)", docx_data, f"DANA_{mapped}_보고서.docx",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
            with d2:
                st.download_button("⬇️ Excel (.xlsx)", xlsx_data, f"DANA_{mapped}_보고서.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            with d3:
                st.download_button("⬇️ PPT (.pptx)", pptx_data, f"DANA_{mapped}_보고서.pptx",
                    "application/vnd.openxmlformats-officedocument.presentationml.presentation", use_container_width=True)

        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
        finally:
            if tmp_path and os.path.exists(tmp_path): os.unlink(tmp_path)
