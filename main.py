import os
import sys
from report_generator import extract_notebook_content, extract_chart_data, generate_charts, generate_report, save_report

def run_dana(notebook_path, report_types=None):
    if report_types is None:
        report_types = ["경영진", "팀내부", "타부서"]

    print(f"\n🔍 DANA 시작 — {notebook_path} 분석 중...\n")

    try:
        content = extract_notebook_content(notebook_path)
        print(f"✅ 노트북 읽기 완료 ({len(content)}자 추출)\n")
    except Exception as e:
        print(f"❌ 노트북 읽기 실패: {e}")
        return

    chart_paths = []
    try:
        datasets = extract_chart_data(notebook_path)
        if datasets:
            chart_paths = generate_charts(datasets)
            print(f"📊 차트 {len(chart_paths)}개 생성 완료\n")
    except Exception as e:
        print(f"⚠️ 차트 생성 실패 (보고서는 계속 생성): {e}\n")

    for report_type in report_types:
        print(f"📝 {report_type}용 보고서 생성 중...")
        try:
            report = generate_report(content, report_type)
            filepath = save_report(report, report_type, chart_paths=chart_paths)
            print(f"✅ 저장 완료 → {filepath}\n")
        except Exception as e:
            print(f"❌ {report_type} 보고서 생성 실패: {e}\n")

    print("🎉 DANA 완료! outputs 폴더 확인하세요.")

if __name__ == "__main__":
    # 실행 방법: python main.py sample_notebooks/analysis.ipynb
    if len(sys.argv) < 2:
        print("사용법: python main.py [노트북경로]")
        print("예시:  python main.py sample_notebooks/analysis.ipynb")
    else:
        run_dana(sys.argv[1])

    