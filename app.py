import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ---------------------------------------------------------
# 1. 頁面基本設定
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Risk Registry | AI 工具風險註冊表",
    page_icon="🛡️",
    layout="wide"
)

DATA_FILE = "shadow_ai_registry.csv"

# 初始化資料庫 (若不存在則建立 CSV)
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=[
        "Timestamp", "Applicant", "Department", "Tool_Name", "Vendor", 
        "Use_Case", "Data_Classification", "Trains_On_Data", "Risk_Level", 
        "ISO_Control", "Status"
    ])
    df_init.to_csv(DATA_FILE, index=False)

def load_data():
    return pd.read_csv(DATA_FILE)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# ---------------------------------------------------------
# 2. 多語言文本字典 (i18n Localization Dictionary)
# ---------------------------------------------------------
TEXTS = {
    "zh": {
        "title": "🛡️ 影子 AI (Shadow AI) 申報與企業動態白名單",
        "caption": "基於 ISO 27001 / ISO 42001 控制項之輕量化 AI 治理工具",
        "tab1": "📝 員工工具申報",
        "tab2": "📋 認可工具白名單 (Allowlist)",
        "tab3": "⚙️ 管理員風險註冊表 (Registry)",
        
        # Tab 1
        "form_header": "申報新 AI 工具 / 服務",
        "form_info": "💡 依據企業資訊安全政策，使用任何未經 IT 預裝之免費或付費 AI 工具前請先完成申報。",
        "applicant": "申報人姓名 / Email",
        "dept": "所屬部門",
        "tool_name": "AI 工具名稱 (例: ChatGPT Free, Claude, Gamma)",
        "vendor": "服務提供商 (例: OpenAI, Anthropic)",
        "data_class": "預計輸入之資料等級",
        "data_class_opts": ["公開資料 (Public)", "內部限閱 (Internal Only)", "機密資料 (Confidential)", "個人資料 (PII/GDPR)"],
        "trains_data": "免費版條款是否會使用數據進行模型訓練？",
        "trains_opts": ["是 (Yes)", "否 / 已設定 Opt-Out (No)", "不確定 (Unsure)"],
        "customer_facing": "該工具輸出內容是否直接發布給外部客戶或用於自動決策？",
        "use_case": "主要用途與情境說明",
        "submit_btn": "提交風險評估",
        "err_msg": "請填寫申報人與工具名稱！",
        "success_msg": "申報完成！自動評估等級：",
        "iso_label": "對應 ISO 管控項：",
        
        # Tab 2
        "allowlist_header": "✅ 企業認可 AI 工具清單 (Allowlist)",
        "no_approved": "目前尚無核准的 AI 工具清單。",
        "m_approved": "已核准工具數",
        "m_low_risk": "低風險工具",
        "m_med_risk": "需特許/中風險工具",
        
        # Tab 3
        "admin_header": "⚙️ 資安 / Governance 團隊管理後台",
        "no_record": "尚無任何申報紀錄。",
        "admin_help": "可直接在表格中修改審核狀態 (Status) 與風險等級 (Risk Level)：",
        "save_btn": "儲存變更",
        "save_success": "動態風險註冊表已成功更新！",
        
        # Risk & Status Mapping
        "status_pending": "待審核 (Pending Review)",
        "status_cond_approved": "條件式核准 (Conditionally Approved)",
        "status_approved": "正式核准 (Approved)",
        "status_banned": "禁止使用 (Banned)",
        "risk_high": "高風險 (High)",
        "risk_med": "中風險 (Medium)",
        "risk_low": "低風險 (Low)"
    },
    "en": {
        "title": "🛡️ Enterprise AI Risk Registry & Dynamic Allowlist",
        "caption": "A lightweight AI Governance tool aligned with ISO 27001 / ISO 42001 controls.",
        "tab1": "📝 Self-Declaration Portal",
        "tab2": "📋 Approved Allowlist",
        "tab3": "⚙️ Risk Registry Admin",
        
        # Tab 1
        "form_header": "Register a New AI Tool / Service",
        "form_info": "💡 Pursuant to Enterprise Information Security Policy, please register any free or paid third-party AI tools before usage.",
        "applicant": "Applicant Name / Email",
        "dept": "Department",
        "tool_name": "AI Tool Name (e.g., ChatGPT Free, Claude, Gamma)",
        "vendor": "Vendor / Provider (e.g., OpenAI, Anthropic)",
        "data_class": "Target Data Classification",
        "data_class_opts": ["Public", "Internal Only", "Confidential", "PII / Sensitive Data"],
        "trains_data": "Does the vendor train models on your data (per Terms of Service)?",
        "trains_opts": ["Yes", "No / Opted Out", "Unsure"],
        "customer_facing": "Is the output customer-facing or used for automated decision-making?",
        "use_case": "Business Use Case Description",
        "submit_btn": "Submit for Risk Assessment",
        "err_msg": "Please fill in both Applicant Name and Tool Name!",
        "success_msg": "Submission complete! Assessed Risk Tier: ",
        "iso_label": "Mapped ISO Control: ",
        
        # Tab 2
        "allowlist_header": "✅ Enterprise Approved AI Allowlist",
        "no_approved": "No approved AI tools currently in the registry.",
        "m_approved": "Total Approved Tools",
        "m_low_risk": "Low Risk Tools",
        "m_med_risk": "Medium Risk Tools",
        
        # Tab 3
        "admin_header": "⚙️ Information Security & Governance Admin",
        "no_record": "No declaration records found.",
        "admin_help": "Modify approval status and risk levels directly in the interactive table:",
        "save_btn": "Save Changes",
        "save_success": "Risk Registry updated successfully!",
        
        # Risk & Status Mapping
        "status_pending": "Pending Review",
        "status_cond_approved": "Conditionally Approved",
        "status_approved": "Approved",
        "status_banned": "Banned",
        "risk_high": "High",
        "risk_med": "Medium",
        "risk_low": "Low"
    }
}

# ---------------------------------------------------------
# 3. 語言切換選單 (Sidebar)
# ---------------------------------------------------------
st.sidebar.title("🌐 Language / 語言")
lang_choice = st.sidebar.selectbox("Select Language", ["繁體中文", "English"])
lang = "zh" if lang_choice == "繁體中文" else "en"
t = TEXTS[lang]

# ---------------------------------------------------------
# 4. 自動風險評估引擎
# ---------------------------------------------------------
def evaluate_risk(data_class, trains_on_data, is_customer_facing):
    # 高風險條件
    high_data_triggers = ["機密資料 (Confidential)", "個人資料 (PII/GDPR)", "Confidential", "PII / Sensitive Data"]
    yes_train_triggers = ["是 (Yes)", "Yes"]
    
    if (data_class in high_data_triggers) or (trains_on_data in yes_train_triggers) or is_customer_facing:
        risk = t["risk_high"]
        iso_control = "ISO 27001 A.8.12 (Data Leakage) & ISO 42001 A.6 (AI Risk)"
    elif data_class in ["內部限閱 (Internal Only)", "Internal Only"]:
        risk = t["risk_med"]
        iso_control = "ISO 27001 A.5.19 (Supplier Relationships)"
    else:
        risk = t["risk_low"]
        iso_control = "ISO 27001 A.8.9 (Configuration Management)"
    return risk, iso_control

# ---------------------------------------------------------
# 5. 主介面渲染
# ---------------------------------------------------------
st.title(t["title"])
st.caption(t["caption"])

tab1, tab2, tab3 = st.tabs([t["tab1"], t["tab2"], t["tab3"]])

# ---------------- Tab 1: 員工申報表單 ----------------
with tab1:
    st.subheader(t["form_header"])
    st.info(t["form_info"])
    
    with st.form("ai_declaration_form"):
        col1, col2 = st.columns(2)
        with col1:
            applicant = st.text_input(t["applicant"])
            department = st.selectbox(t["dept"], ["HR", "Finance", "Marketing", "IT", "Operations", "Legal", "Other"])
            tool_name = st.text_input(t["tool_name"])
            vendor = st.text_input(t["vendor"])
        
        with col2:
            data_class = st.selectbox(t["data_class"], t["data_class_opts"])
            trains_on_data = st.radio(t["trains_data"], t["trains_opts"])
            is_customer_facing = st.checkbox(t["customer_facing"])
        
        use_case = st.text_area(t["use_case"])
        submitted = st.form_submit_button(t["submit_btn"])
        
        if submitted:
            if not applicant or not tool_name:
                st.error(t["err_msg"])
            else:
                risk, iso_control = evaluate_risk(data_class, trains_on_data, is_customer_facing)
                
                # 自動判斷初期狀態
                initial_status = t["status_pending"] if risk == t["risk_high"] else t["status_cond_approved"]
                
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
                    "ISO_Control": iso_control,
                    "Status": initial_status
                }
                
                df = load_data()
                df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                save_data(df)
                
                st.success(f"{t['success_msg']} **{risk}**。{t['iso_label']}`{iso_control}`")

# ---------------- Tab 2: 企業白名單 ----------------
with tab2:
    st.subheader(t["allowlist_header"])
    df = load_data()
    
    # 篩選已核准/條件核准的工具
    approved_statuses = [t["status_approved"], t["status_cond_approved"], "Approved", "Conditionally Approved", "正式核准 (Approved)", "條件式核准 (Conditionally Approved)"]
    approved_df = df[df["Status"].isin(approved_statuses)]
    
    if approved_df.empty:
        st.warning(t["no_approved"])
    else:
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric(t["m_approved"], len(approved_df))
        
        low_risks = [t["risk_low"], "Low", "低風險 (Low)"]
        med_risks = [t["risk_med"], "Medium", "中風險 (Medium)"]
        
        col_m2.metric(t["m_low_risk"], len(approved_df[approved_df["Risk_Level"].isin(low_risks)]))
        col_m3.metric(t["m_med_risk"], len(approved_df[approved_df["Risk_Level"].isin(med_risks)]))
        
        st.divider()
        st.dataframe(
            approved_df[["Tool_Name", "Vendor", "Use_Case", "Risk_Level", "Status", "ISO_Control"]],
            use_container_width=True,
            hide_index=True
        )

# ---------------- Tab 3: 管理員後台 ----------------
with tab3:
    st.subheader(t["admin_header"])
    df = load_data()
    
    if df.empty:
        st.write(t["no_record"])
    else:
        st.write(t["admin_help"])
        
        edited_df = st.data_editor(
            df,
            column_config={
                "Status": st.column_config.SelectboxColumn(
                    "Status / 審核狀態",
                    options=[
                        "Pending Review", "Conditionally Approved", "Approved", "Banned",
                        "待審核 (Pending Review)", "條件式核准 (Conditionally Approved)", "正式核准 (Approved)", "禁止使用 (Banned)"
                    ],
                    required=True
                ),
                "Risk_Level": st.column_config.SelectboxColumn(
                    "Risk Level / 風險等級",
                    options=[
                        "Low", "Medium", "High",
                        "低風險 (Low)", "中風險 (Medium)", "高風險 (High)"
                    ],
                    required=True
                )
            },
            disabled=["Timestamp", "Applicant", "Tool_Name"],
            use_container_width=True,
            key="admin_editor"
        )
        
        if st.button(t["save_btn"]):
            save_data(edited_df)
            st.success(t["save_success"])
            st.rerun()
