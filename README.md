# DANA - Data Analysis & NICE Automation
 **분석은 당신이, 보고서는 DANA가**
 Jupyter Notebook, CSV, Excel 등 데이터 분석 결과물을 업로드하면
 Claude AI가 자동으로 전문 보고서를 생성 시스템

---
## 시스템 아키텍처
![DANA 시스템 아키텍처](dana_architecture_diagram.png)

---

## 프로젝트 구조
```
dana/
├── app.py                  # Streamlit 웹 UI
├── report_generator.py     # 핵심 엔진 (파싱·AI·출력)
├── main.py                 # CLI 실행 모드
├── sample_notebooks/
│   └── analysis.ipynb      # 샘플 분석 파일
├── requirements.txt
├── .gitignore
└── .env                   
```

---
## 실행

```bash
streamlit run app.py
```
`http://localhost:8501`

---
## 주요 기능

- **다양한 입력 지원** — `.ipynb` · `.csv` · `.xlsx` · 텍스트 직접 입력
- **AI 보고서 자동 생성** — Claude API 기반 컨설팅 스타일 보고서
- **3종 동시 출력** — Word · Excel · PPT 한 번에 다운로드
- **차트 자동 생성** — 분석 데이터 기반 시각화 자동 포함
- **히스토리 관리** — 생성된 보고서 자동 저장 및 재다운로드

---
## 기술 스택

| 구분 | 기술 |
|------|------|
| AI 엔진 | Claude API (`claude-sonnet-4-6`) |
| 웹 UI | Streamlit |
| 데이터 처리 | pandas · nbformat |
| 시각화 | matplotlib |
| Word 출력 | python-docx |
| Excel 출력 | openpyxl |
| PPT 출력 | python-pptx |

