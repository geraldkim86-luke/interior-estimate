import streamlit as st
import pandas as pd
import os

# --- 1. 엑셀 데이터 처리 파트 ---
class DataManager:
    def __init__(self, filename='price_table.xlsx'):
        self.filename = filename
        self.df = self.load_data()

    def load_data(self):
        # 엑셀 파일이 없으면 테스트용 데이터를 생성합니다.
        if not os.path.exists(self.filename):
            data = {
                '대분류': ['도배', '도배', '도배', '바닥', '바닥', '바닥', '욕실', '욕실'],
                '자재명': ['선택안함', '합지', '실크', '선택안함', '장판', '강마루', '선택안함', '기본형(덧방)'],
                '단가': [0, 5, 12, 0, 4, 13, 0, 250],
                '단위': ['평', '평', '평', '평', '평', '평', '식', '식']
            }
            df = pd.DataFrame(data)
            df.to_excel(self.filename, index=False)
            return df
        
        # 엑셀 파일 읽기
        return pd.read_excel(self.filename)

    def get_categories(self):
        """대분류(시공 종류) 목록을 중복 없이 가져옵니다."""
        # 엑셀에 '대분류' 컬럼이 있는지 확인
        if '대분류' not in self.df.columns:
            st.error("엑셀 파일에 '대분류' 컬럼이 없습니다. price_table.xlsx를 삭제 후 다시 실행해주세요.")
            return []
        return self.df['대분류'].unique().tolist()

    def get_materials(self, category):
        """해당 대분류에 속하는 자재명 리스트를 가져옵니다."""
        return self.df[self.df['대분류'] == category]['자재명'].tolist()

    def get_info(self, category, material_name):
        """선택한 자재의 단가와 단위를 가져옵니다."""
        row = self.df[(self.df['대분류'] == category) & (self.df['자재명'] == material_name)]
        if not row.empty:
            return row.iloc[0]['단가'], row.iloc[0]['단위']
        return 0, '식'

# --- 2. 웹 화면(GUI) 및 계산 로직 파트 ---
def main():
    st.set_page_config(page_title="자동 인테리어 견적", layout="centered")
    dm = DataManager()

    # 타이틀
    st.title(" 맞춤 인테리어 견적 시스템")
    st.markdown("시공 항목별로 원하시는 자재를 선택해주세요.")
    st.divider()

    # [1] 기본 정보 입력
    col1, col2 = st.columns(2)
    with col1:
        pyeong = st.number_input("아파트 평수 (평)", min_value=10, max_value=100, value=32)

    st.subheader(" 시공 및 자재 선택")
    
    # [2] 동적 메뉴 생성
    categories = dm.get_categories()
    user_selections = {} 

    if not categories:
        st.stop() # 데이터가 없으면 중단

    for cat in categories:
        materials = dm.get_materials(cat)
        choice = st.selectbox(f"{cat} 시공 자재 선택", materials, key=cat)
        user_selections[cat] = choice

    st.divider()

    # [3] 견적 계산 및 출력
    if st.button("견적서 산출하기", type="primary", use_container_width=True):
        st.subheader(" 상세 견적서")
        
        total_cost = 0
        estimate_data = []

        for cat, material in user_selections.items():
            price, unit = dm.get_info(cat, material)
            
            if price == 0:
                continue

            if unit == '평':
                calc_cost = price * pyeong
                detail_txt = f"{pyeong}평 × {price}만원"
            else: 
                calc_cost = price
                detail_txt = f"1식 기준"

            total_cost += calc_cost
            
            estimate_data.append({
                "공정": cat,
                "선택 자재": material,
                "상세 계산": detail_txt,
                "예상 비용": f"{calc_cost:,} 만원"
            })

        if estimate_data:
            st.table(pd.DataFrame(estimate_data))
            
            st.markdown(f"""
            <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;'>
                <h3 style='margin:0; color: #333;'>총 예상 견적</h3>
                <h1 style='color: #0068c9; margin: 10px 0;'>{total_cost:,} 만원</h1>
                <p style='margin:0; font-size: 0.8em; color: #666;'>* 부가세(VAT) 별도 금액입니다.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("선택된 공정이 없습니다. 자재를 선택해주세요.")

if __name__ == "__main__":

    main()
