import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 頁面基本設定
st.set_page_config(
    page_title="企業 Shadow AI 治理與動態風險註冊表",
    page_icon="🛡️",
    layout="wide"
)

DATA_FILE = "shadow_ai_registry.csv"

# 初始化資料庫 (若不存在則建立 CSV)
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=[
        "Timestamp", "Applicant", "Department", "Tool_Name", "Vendor", 
        "Use_Case", "Data_Classification", "Trains_On_Data", "Risk_Level", 
        "ISO27001_Control", "Status"
    ])
    df_init.to_csv(DATA_FILE, index=False)

def load_data():
    return pd.read_csv(DATA_FILE)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# 自動風險評估引擎
def evaluate_risk(data_class, trains_on_data, is_customer_facing):
    if data_class in ["機密資料 (Confidential)", "個人資料 (PII/GDPR)"] or trains_on_data == "是 (Yes)" or is_customer_facing:
        risk = "高風險 (High)"
        iso_control = "A.8.12 (Data Leakage) & A.5.19 (Supplier Relationships)"
    elif data_class == "內部限閱 (Internal Only)":
        risk = "中風險 (Medium)"
        iso_control = "A.5.8 (Information Security in Project Management)"
    else:
        risk = "低風險 (Low)"
        iso_control = "A.8.9 (Configuration Management)"
    return risk, iso_control

# 標頭資訊
st.title("🛡️ 影子 AI (Shadow AI) 申報與企業動態白名單")
st.caption("基於 ISO 27001 / ISO 42001 控制項之輕量化 AI 治理工具")

tab1, tab2, tab3 = st.tabs(["📝 員工工具申報", "📋 認可工具白名單 (Allowlist)", "⚙️ 管理員風險註冊表 (Registry)"])

# ---------------- Tab 1: 員工申報表單 ----------------
with tab1:
    st.subheader("申報新 AI 工具 / 服務")
    st.info("💡 依據企業資訊安全政策，使用任何未經 IT 預裝之免費或付費 AI 工具前請先完成申報。")
    
    with st.form("ai_declaration_form"):
        col1, col2 = st.columns(2)
        with col1:
            applicant = st.text_input("申報人姓名 / Email")
            department = st.selectbox("所屬部門", ["HR", "Finance", "Marketing", "IT", "Operations", "Legal", "Other"])
            tool_name = st.text_input("AI 工具名稱 (例: ChatGPT Free, Claude, Gamma, Perplexity)")
            vendor = st.text_input("服務提供商 (例: OpenAI, Anthropic)")
        
        with col2:
            data_class = st.selectbox(
                "預計輸入之資料等級 (Data Classification)",
                ["公開資料 (Public)", "內部限閱 (Internal Only)", "機密資料 (Confidential)", "個人資料 (PII/GDPR)"]
            )
            trains_on_data = st.radio(
                "免費版條款是否會使用數據進行模型訓練？",
                ["是 (Yes)", "否 / 已設定 Opt-Out (No)", "不確定 (Unsure)"]
            )
            is_customer_facing = st.checkbox("該工具輸出內容是否直接發布給外部客戶或用於自動決策？")
        
        use_case = st.text_area("主要用途與情境說明 (Use Case Description)")
        
        submitted = st.form_submit_button("提交風險評估")
        
        if submitted:
            if not applicant or not tool_name:
                st.error("請填寫申報人與工具名稱！")
            else:
                risk, iso_control = evaluate_risk(data_class, trains_on_data, is_customer_facing)
                
                # 自動判斷審核狀態
                initial_status = "待審核 (Pending Review)" if risk != "低風險 (Low)" else "條件式核准 (Conditionally Approved)"
                
                new_data = {
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Applicant": applicant,
                    "Department": department,
                    "Tool_Name": tool_name,
                    "Vendor": vendor,
                    "Use_Case": use_case,
                    "Data_Classification": data_class,
                    "Trains_On_Data": trains_on_data,
                    "Risk_Level": risk,
                    "ISO27001_Control": iso_control,
                    "Status": initial_status
                }
                
                df = load_data()
                df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=False)
                save_data(df)
                
                st.success(f"申報完成！自動評估等級：**{risk}**。對應 ISO 管控項：`{iso_control}`")

# ---------------- Tab 2: 企業白名單展示 ----------------
with tab2:
    st.subheader("✅ 企業認可 AI 工具清單 (Allowlist)")
    df = load_data()
    
    # 篩選已核准的工具
    approved_df = df[df["Status"].isin(["正式核准 (Approved)", "條件式核准 (Conditionally Approved)"])]
    
    if approved_df.empty:
        st.warning("目前尚無核准的 AI 工具清單。")
    else:
        # 指標概覽
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("已核准工具數", len(approved_df))
        col_m2.metric("低風險工具", len(approved_df[approved_df["Risk_Level"] == "低風險 (Low)"]))
        col_m3.metric("需特許/中風險工具", len(approved_df[approved_df["Risk_Level"] == "中風險 (Medium)"]))
        
        st.divider()
        st.dataframe(
            approved_df[["Tool_Name", "Vendor", "Use_Case", "Risk_Level", "Status", "ISO27001_Control"]],
            use_container_width=True,
            hide_index=True
        )

# ---------------- Tab 3: 管理員風險審核 ----------------
with tab3:
    st.subheader("⚙️ 資安 / Governance 團隊管理後台")
    df = load_data()
    
    if df.empty:
        st.write("尚無任何申報紀錄。")
    else:
        st.write("可直接在表格中修改狀態 (Status) 與風險等級：")
        
        # 使用 Streamlit data_editor 進行動態編輯
        edited_df = st.data_editor(
            df,
            column_config={
                "Status": st.column_config.SelectboxColumn(
                    "審核狀態",
                    options=["待審核 (Pending Review)", "條件式核准 (Conditionally Approved)", "正式核准 (Approved)", "禁止使用 (Banned)"],
                    required=True
                ),
                "Risk_Level": st.column_config.SelectboxColumn(
                    "風險等級",
                    options=["低風險 (Low)", "中風險 (Medium)", "高風險 (High)"],
                    required=True
                )
            },
            disabled=["Timestamp", "Applicant", "Tool_Name"],
            use_container_width=True,
            key="admin_editor"
        )
        
        if st.button("儲存變更"):
            save_data(edited_df)
            st.success("動態風險註冊表已成功更新！")
            st.rerun()
