import os
import re
import nbformat
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from anthropic import Anthropic
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = Anthropic()

def extract_notebook_content(notebook_path):
    """Jupyter 노트북에서 텍스트 결과물 추출"""
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    
    content = []
    for cell in nb.cells:
        if cell.cell_type == 'code':
            # 코드 추출
            if cell.source.strip():
                content.append(f"[코드]\n{cell.source}")
            # 실행 결과 추출
            for output in cell.outputs:
                if output.output_type == 'stream':
                    content.append(f"[출력]\n{output.text}")
                elif output.output_type == 'display_data':
                    if 'text/plain' in output.data:
                        content.append(f"[데이터]\n{output.data['text/plain']}")
                elif output.output_type == 'execute_result':
                    if 'text/plain' in output.data:
                        content.append(f"[결과]\n{output.data['text/plain']}")
        elif cell.cell_type == 'markdown':
            content.append(f"[분석 메모]\n{cell.source}")
    
    return "\n\n".join(content)


def setup_korean_font():
    for name in ['AppleGothic', 'Malgun Gothic', 'NanumGothic']:
        matches = [f for f in fm.fontManager.ttflist if name in f.name]
        if matches:
            plt.rcParams['font.family'] = name
            break
    plt.rcParams['axes.unicode_minus'] = False


def extract_chart_data(notebook_path):
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)

    datasets = []
    for cell in nb.cells:
        if cell.cell_type != 'code':
            continue
        for output in cell.outputs:
            text = ''
            if output.output_type == 'stream':
                text = output.text
            elif output.output_type in ('execute_result', 'display_data'):
                text = output.data.get('text/plain', '')
            if not text.strip():
                continue

            lines = text.strip().split('\n')
            title = lines[0].strip().rstrip(':')

            count_labels, count_values = [], []
            pct_labels, pct_values = [], []

            for line in lines[1:]:
                stripped = line.strip()
                if not stripped or stripped.startswith(('-', '▶', '▼', '▲', '⚠')):
                    if not re.match(r'^[-\s]*\S+.*[:：]\s*[\d,]', stripped):
                        continue

                m_pct = re.match(r'^[-\s]*(.+?)[:：]\s*([\d,]+(?:\.\d+)?)\s*%', stripped)
                m_count = re.match(r'^[-\s]*(.+?)[:：]\s*([\d,]+(?:\.\d+)?)\s*건', stripped)

                if m_pct:
                    label = m_pct.group(1).strip()
                    if '전년' not in label and '동기' not in label:
                        pct_labels.append(label)
                        pct_values.append(float(m_pct.group(2).replace(',', '')))
                elif m_count:
                    label = m_count.group(1).strip()
                    skip_keywords = ['총', '합계', '평균', '월평균', '상반기', '하반기', '전체']
                    if not any(kw in label for kw in skip_keywords):
                        count_labels.append(label)
                        count_values.append(float(m_count.group(2).replace(',', '')))

            if len(pct_labels) >= 2:
                datasets.append({
                    'title': title,
                    'labels': pct_labels,
                    'values': pct_values,
                    'unit': '%',
                })
            if len(count_labels) >= 2:
                datasets.append({
                    'title': title,
                    'labels': count_labels,
                    'values': count_values,
                    'unit': '건',
                })
    return datasets


def generate_charts(datasets, output_dir="outputs"):
    os.makedirs(output_dir, exist_ok=True)
    setup_korean_font()

    colors = ['#2563EB', '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE', '#DBEAFE', '#EFF6FF']
    accent_colors = ['#1E40AF', '#2563EB', '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE', '#DBEAFE']
    chart_paths = []

    for i, ds in enumerate(datasets):
        fig, ax = plt.subplots(figsize=(10, 5))
        n = len(ds['labels'])

        if ds['unit'] == '%':
            bars = ax.barh(ds['labels'][::-1], ds['values'][::-1],
                           color=accent_colors[:n][::-1], height=0.6, edgecolor='white')
            for bar, val in zip(bars, ds['values'][::-1]):
                ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                        f'{val}%', va='center', fontsize=11, fontweight='bold')
            ax.set_xlabel('%', fontsize=11)
        elif '월별' in ds['title'] or '추이' in ds['title']:
            ax.plot(ds['labels'], ds['values'], marker='o', color='#2563EB',
                    linewidth=2.5, markersize=8, markerfacecolor='white',
                    markeredgecolor='#2563EB', markeredgewidth=2)
            ax.fill_between(ds['labels'], ds['values'], alpha=0.1, color='#2563EB')
            for x, y in zip(ds['labels'], ds['values']):
                ax.text(x, y + max(ds['values'])*0.02, f'{y:,.0f}',
                        ha='center', va='bottom', fontsize=10, fontweight='bold')
            ax.set_ylabel('건', fontsize=11)
        else:
            bars = ax.bar(ds['labels'], ds['values'],
                          color=colors[:n], width=0.6, edgecolor='white')
            for bar, val in zip(bars, ds['values']):
                label = f'{val:,.0f}{ds["unit"]}'
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(ds['values'])*0.01,
                        label, ha='center', va='bottom', fontsize=10, fontweight='bold')

        ax.set_title(ds['title'], fontsize=14, fontweight='bold', pad=15)
        ax.spines[['top', 'right']].set_visible(False)
        ax.tick_params(labelsize=10)
        fig.tight_layout()

        filename = f"chart_{i+1}.png"
        filepath = os.path.join(output_dir, filename)
        fig.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        chart_paths.append(filename)

    return chart_paths


def generate_report(notebook_content, report_type="경영진", title="", purpose="", audience="", length=""):
    prompts = {
        "분석요약": """당신은 데이터 분석 결과를 요약 보고서로 작성하는 전문가입니다.
아래 분석 결과를 바탕으로 핵심 인사이트와 주요 결과를 간단명료하게 요약하세요.

규칙:
- 핵심 인사이트 3가지를 가장 먼저
- 수치는 의미 중심으로 쉽게 해석
- 주요 수치는 반드시 마크다운 표(table)로 정리
- 분량: A4 1장 이내
- 마지막에 "주요 시사점" 포함

형식:
# [분석 요약] {날짜} 데이터 분석 결과

## 핵심 인사이트
## 주요 결과
## 주요 시사점
""",
        "비즈니스인사이트": """당신은 데이터 분석 결과에서 비즈니스 인사이트를 도출하는 전문가입니다.
아래 분석 결과를 바탕으로 비즈니스 관점의 인사이트와 액션 아이템을 포함한 보고서를 작성하세요.

규칙:
- 비즈니스 임팩트 중심으로 해석
- 전문 용어는 괄호 안에 설명 추가
- 각 인사이트별 구체적 액션 아이템 제시
- 주요 수치는 반드시 마크다운 표(table)로 정리
- 마지막에 "권장 액션 아이템" 포함

형식:
# [비즈니스 인사이트] {날짜} 분석 보고서

## 핵심 발견사항
## 비즈니스 임팩트 분석
## 권장 액션 아이템
""",
        "기술분석": """당신은 데이터 분석의 기술적 세부사항을 보고서로 작성하는 전문가입니다.
아래 분석 결과를 바탕으로 분석 방법론, 모델, 기술적 세부사항을 상세히 설명하세요.

규칙:
- 분석 방법론과 수치 상세 포함
- 데이터 품질 이슈나 특이사항 명시
- 추가 분석이 필요한 항목 표시
- 전문 용어 사용 가능
- 주요 수치 비교는 반드시 마크다운 표(table)로 정리

형식:
# [기술 분석] {날짜} 분석 상세 리포트

## 분석 개요
## 상세 결과
## 특이사항 및 데이터 품질
## 추가 검토 필요 항목
""",
        "경영진": """당신은 데이터 분석 결과를 경영진용 보고서로 작성하는 전문가입니다.
아래 분석 결과를 바탕으로 경영진을 위한 핵심 KPI와 전략적 제언 중심의 보고서를 작성하세요.

규칙:
- 핵심 인사이트 3가지를 가장 먼저
- 수치는 쉽게 해석해서 의미 중심으로
- 전문 용어 최소화, 비즈니스 임팩트 중심
- 주요 수치는 반드시 마크다운 표(table)로 정리
- 분량: A4 1장 이내
- 마지막에 반드시 "제언 및 다음 단계" 포함

형식:
# [경영진 보고] {날짜} 데이터 분석 결과 요약

## 핵심 인사이트
## 주요 현황
## 제언 및 다음 단계
"""
    }
    
    prompt = prompts[report_type]
    today = datetime.now().strftime("%Y년 %m월 %d일")
    prompt = prompt.replace("{날짜}", today)

    length_map = {
        "짧게 (1-2 페이지)": "A4 1-2장 이내로 간결하게",
        "중간 (3-5 페이지)": "A4 3-5장 분량으로 적절히 상세하게",
        "상세 (5-10 페이지)": "A4 5-10장 분량으로 매우 상세하게",
    }

    context_parts = []
    if title:
        context_parts.append(f"- 보고서 제목: {title}")
    if purpose:
        context_parts.append(f"- 분석 목적: {purpose}")
    if audience:
        context_parts.append(f"- 대상 독자: {audience} (이 독자 수준에 맞춰 용어와 설명 수준을 조절하세요)")
    if length and length in length_map:
        context_parts.append(f"- 분량: {length_map[length]}")

    context_str = ""
    if context_parts:
        context_str = "\n\n추가 요구사항:\n" + "\n".join(context_parts)

    max_tokens = 2000
    if "상세" in length:
        max_tokens = 4000
    elif "중간" in length:
        max_tokens = 3000

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        messages=[
            {
                "role": "user",
                "content": f"{prompt}{context_str}\n\n---\n분석 결과:\n{notebook_content}"
            }
        ]
    )

    return message.content[0].text


def save_report(report_content, report_type, chart_paths=None, output_dir="outputs"):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"{output_dir}/DANA_{report_type}_{timestamp}.md"

    chart_section = ""
    if chart_paths:
        chart_section = "\n\n---\n\n## 시각화 자료\n\n"
        for cp in chart_paths:
            chart_section += f"![chart]({cp})\n\n"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report_content)
        f.write(chart_section)

    return filename


def export_docx(report_text, chart_figures=None):
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    import io

    doc = Document()

    style = doc.styles['Normal']
    style.font.name = 'Malgun Gothic'
    style.font.size = Pt(10.5)

    for line in report_text.split('\n'):
        stripped = line.strip()
        if not stripped:
            doc.add_paragraph('')
            continue

        if stripped.startswith('# '):
            p = doc.add_heading(stripped[2:], level=1)
            for run in p.runs:
                run.font.color.rgb = RGBColor(0x11, 0x18, 0x27)
        elif stripped.startswith('## '):
            p = doc.add_heading(stripped[3:], level=2)
            for run in p.runs:
                run.font.color.rgb = RGBColor(0x11, 0x18, 0x27)
        elif stripped.startswith('### '):
            p = doc.add_heading(stripped[4:], level=3)
        elif stripped.startswith('|') and '|' in stripped[1:]:
            cells = [c.strip() for c in stripped.split('|')[1:-1]]
            if all(set(c) <= set('- :') for c in cells):
                continue
            if not hasattr(doc, '_dana_table'):
                table = doc.add_table(rows=0, cols=len(cells))
                table.style = 'Light Grid Accent 1'
                doc._dana_table = table
                doc._dana_table_started = True
            else:
                table = doc._dana_table
            row = table.add_row()
            for i, cell_text in enumerate(cells):
                if i < len(row.cells):
                    clean = cell_text.replace('**', '')
                    row.cells[i].text = clean
        else:
            if hasattr(doc, '_dana_table'):
                del doc._dana_table
            clean = stripped.replace('**', '').replace('> ', '')
            if stripped.startswith('- '):
                doc.add_paragraph(clean[2:], style='List Bullet')
            else:
                doc.add_paragraph(clean)

    if hasattr(doc, '_dana_table'):
        del doc._dana_table

    if chart_figures:
        doc.add_page_break()
        p = doc.add_heading('시각화 자료', level=1)
        for run in p.runs:
            run.font.color.rgb = RGBColor(0x11, 0x18, 0x27)
        for fig in chart_figures:
            img_buf = io.BytesIO()
            fig.savefig(img_buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
            img_buf.seek(0)
            doc.add_picture(img_buf, width=Inches(6))
            last_paragraph = doc.paragraphs[-1]
            last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            doc.add_paragraph('')

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()


def export_xlsx(report_text, datasets=None):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Border, Side
    import io

    wb = Workbook()

    ws_report = wb.active
    ws_report.title = "보고서"
    header_font = Font(bold=True, size=13, color="111827")
    sub_font = Font(bold=True, size=11, color="4F46E5")
    normal_font = Font(size=10.5)
    header_fill = PatternFill(start_color="EEF2FF", end_color="EEF2FF", fill_type="solid")

    row_num = 1
    for line in report_text.split('\n'):
        stripped = line.strip()
        if stripped.startswith('# '):
            cell = ws_report.cell(row=row_num, column=1, value=stripped[2:])
            cell.font = header_font
            cell.fill = header_fill
            row_num += 1
        elif stripped.startswith('## '):
            row_num += 1
            cell = ws_report.cell(row=row_num, column=1, value=stripped[3:])
            cell.font = sub_font
            row_num += 1
        elif stripped.startswith('|') and '|' in stripped[1:]:
            cells = [c.strip().replace('**', '') for c in stripped.split('|')[1:-1]]
            if all(set(c) <= set('- :') for c in cells):
                continue
            for i, val in enumerate(cells):
                cell = ws_report.cell(row=row_num, column=i+1, value=val)
                cell.font = normal_font
            row_num += 1
        elif stripped:
            clean = stripped.replace('**', '').replace('> ', '').replace('---', '')
            if clean:
                cell = ws_report.cell(row=row_num, column=1, value=clean)
                cell.font = normal_font
                row_num += 1

    ws_report.column_dimensions['A'].width = 80

    if datasets:
        for i, ds in enumerate(datasets):
            ws_name = ds['title'][:28] if len(ds['title']) > 28 else ds['title']
            ws = wb.create_sheet(title=ws_name)

            title_cell = ws.cell(row=1, column=1, value=ds['title'])
            title_cell.font = Font(bold=True, size=12, color="111827")

            ws.cell(row=3, column=1, value="항목").font = Font(bold=True, size=10.5)
            ws.cell(row=3, column=2, value=f"값 ({ds['unit']})").font = Font(bold=True, size=10.5)
            thin = Side(style='thin', color='E5E7EB')
            for j, (label, value) in enumerate(zip(ds['labels'], ds['values'])):
                r = j + 4
                c1 = ws.cell(row=r, column=1, value=label)
                c2 = ws.cell(row=r, column=2, value=value)
                c1.font = normal_font
                c2.font = normal_font
                c2.number_format = '#,##0.##'
                for c in [c1, c2]:
                    c.border = Border(bottom=thin)

            ws.column_dimensions['A'].width = 25
            ws.column_dimensions['B'].width = 18

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()