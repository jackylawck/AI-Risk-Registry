import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

# ---------------------------------------------------------
# 1. 頁面基本設定
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Risk Registry | 企業級 AI 工具風險註冊表",
    page_icon="🛡️",
    layout="wide"
)

DB_FILE = "shadow_ai_registry.db"
HK_TZ = ZoneInfo('Asia/Hong_Kong')

# ---------------------------------------------------------
# 2. 資料庫初始化 (SQLite 解決 Concurrent 撞資料問題)
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS registry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            applicant TEXT,
            department TEXT,
            tool_name TEXT,
            vendor TEXT,
            use_case TEXT,
            data_class_code TEXT,
            trains_on_data_code TEXT,
            is_customer_facing INTEGER,
            risk_level_code TEXT,
            iso_control TEXT,
            status_code TEXT,
            last_modified_by TEXT,
            last_modified_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def load_data():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM registry", conn)
    conn.close()
    return df

def update_record(record_id, status_code, risk_code, admin_name):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    mod_time = datetime.now(HK_TZ).strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        UPDATE registry 
        SET status_code = ?, risk_level_code = ?, last_modified_by = ?, last_modified_at = ?
        WHERE id = ?
    ''', (status_code, risk_code, admin_name, mod_time, record_id))
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# 3. Enum 字典與 i18n 本地化 (解決字串 Hard-code 導致邏輯出錯)
# ---------------------------------------------------------
DATA_CLASS = ["PUBLIC", "INTERNAL", "CONFIDENTIAL", "PII"]
TRAINS_DATA = ["YES", "NO", "UNSURE"]
RISK_LEVELS = ["LOW", "MEDIUM", "HIGH"]
STATUS_CODES = ["SUBMITTED", "ASSESSING", "APPROVED", "REJECTED", "EXCEPTION"]

TEXTS = {
    "zh": {
        "title": "🛡️ AI Risk Registry (影子 AI 風險註冊表)",
        "caption": "基於 ISO 27001 / ISO 42001 控制項之企業級 AI 治理工具",
        "tab1": "📝 員工自助申報",
        "tab2": "📋 認可工具白名單 (Allowlist)",
        "tab3": "⚙️ 審計與風險管理台",
        
        # UI Labels
        "form_header": "申報新 AI 工具",
        "form_info": "💡 依據企業資訊安全政策，使用任何未經審批之 AI 工具前請先完成申報。",
        "applicant": "申報人姓名",
        "dept": "所屬部門",
        "tool_name": "AI 工具名稱",
        "vendor": "服務供應商",
        "customer_facing": "輸出內容是否直接發布給客戶或用於自動決策？",
        "use_case": "商業用途說明",
        "submit_btn": "提交評估",
        
        # Mappings (Enum -> Display)
        "data_map": {"PUBLIC": "公開資料", "INTERNAL": "內部限閱", "CONFIDENTIAL": "機密資料", "PII": "個人資料 (PII/GDPR)"},
        "train_map": {"YES": "是", "NO": "否 / 已 Opt-Out", "UNSURE": "不確定"},
        "risk_map": {"LOW": "低風險 (Low)", "MEDIUM": "中風險 (Medium)", "HIGH": "高風險 (High)"},
        "status_map": {
            "SUBMITTED": "已提交 (Submitted)", 
            "ASSESSING": "評估中 (Under Assessment)", 
            "APPROVED": "正式核准 (Approved)", 
            "REJECTED": "拒絕/需整改 (Rejected/Remediation Req.)", 
            "EXCEPTION": "特許例外 (Exception Approved)"
        }
    },
    "en": {
        "title": "🛡️ Enterprise AI Risk Registry",
        "caption": "Auditable AI Governance tool aligned with ISO 27001 / ISO 42001.",
        "tab1": "📝 Self-Declaration",
        "tab2": "📋 Approved Allowlist",
        "tab3": "⚙️ GRC Admin Console",
        
        # UI Labels
        "form_header": "Register AI Tool",
        "form_info": "💡 Please declare third-party AI tools prior to usage to ensure regulatory compliance.",
        "applicant": "Applicant Name",
        "dept": "Department",
        "tool_name": "Tool Name",
        "vendor": "Vendor",
        "customer_facing": "Is output customer-facing or used for automated decisions?",
        "use_case": "Business Use Case",
        "submit_btn": "Submit for Assessment",
        
        # Mappings (Enum -> Display)
        "data_map": {"PUBLIC": "Public", "INTERNAL": "Internal Only", "CONFIDENTIAL": "Confidential", "PII": "PII / Sensitive"},
        "train_map": {"YES": "Yes", "NO": "No / Opt-Out", "UNSURE": "Unsure"},
        "risk_map": {"LOW": "Low", "MEDIUM": "Medium", "HIGH": "High"},
        "status_map": {
            "SUBMITTED": "Submitted", 
            "ASSESSING": "Under Assessment", 
            "APPROVED": "Approved", 
            "REJECTED": "Rejected / Remediation Req.", 
            "EXCEPTION": "Exception Approved"
        }
    }
}

st.sidebar.title("🌐 設定 / Settings")
lang_choice = st.sidebar.selectbox("Language", ["繁體中文", "English"])
lang = "zh" if lang_choice == "繁體中文" else "en"
t = TEXTS[lang]

# 反向 Mapping (Display -> Enum)
rev_data_map = {v: k for k, v in t["data_map"].items()}
rev_train_map = {v: k for k, v in t["train_map"].items()}
rev_risk_map = {v: k for k, v in t["risk_map"].items()}
rev_status_map = {v: k for k, v in t["status_map"].items()}

# ---------------------------------------------------------
# 4. 核心風險引擎 (完全基於 Enum 運作)
# ---------------------------------------------------------
def evaluate_risk(data_code, train_code, is_customer_facing):
    if data_code in ["CONFIDENTIAL", "PII"] or train_code == "YES" or is_customer_facing:
        return "HIGH", "ISO 27001 A.8.12 & ISO 42001 A.6"
    elif data_code == "INTERNAL":
        return "MEDIUM", "ISO 27001 A.5.19"
    else:
        return "LOW", "ISO 27001 A.8.9"

# ---------------------------------------------------------
# 5. 主介面渲染
# ---------------------------------------------------------
st.title(t["title"])
st.caption(t["caption"])

tab1, tab2, tab3 = st.tabs([t["tab1"], t["tab2"], t["tab3"]])

# --- Tab 1: 員工自助申報 ---
with tab1:
    st.subheader(t["form_header"])
    st.info(t["form_info"])
    
    with st.form("declaration_form"):
        col1, col2 = st.columns(2)
        with col1:
            applicant = st.text_input(t["applicant"])
            department = st.selectbox(t["dept"], ["HR", "Finance", "IT", "Marketing", "Legal", "Operations", "Other"])
            tool_name = st.text_input(t["tool_name"])
            vendor = st.text_input(t["vendor"])
        with col2:
            data_disp = st.selectbox("Data Classification", list(t["data_map"].values()))
            train_disp = st.radio("Vendor Data Training", list(t["train_map"].values()))
            is_cust = st.checkbox(t["customer_facing"])
        
        use_case = st.text_area(t["use_case"])
        if st.form_submit_button(t["submit_btn"]):
            if applicant and tool_name:
                data_code = rev_data_map[data_disp]
                train_code = rev_train_map[train_disp]
                
                risk_code, iso_control = evaluate_risk(data_code, train_code, is_cust)
                status_code = "ASSESSING" if risk_code == "HIGH" else "SUBMITTED"
                
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute('''
                    INSERT INTO registry 
                    (timestamp, applicant, department, tool_name, vendor, use_case, data_class_code, trains_on_data_code, is_customer_facing, risk_level_code, iso_control, status_code, last_modified_by, last_modified_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (datetime.now(HK_TZ).strftime("%Y-%m-%d %H:%M:%S"), applicant, department, tool_name, vendor, use_case, data_code, train_code, is_cust, risk_code, iso_control, status_code, "System", ""))
                conn.commit()
                conn.close()
                st.success(f"✅ Submitted! Assessed Risk: {t['risk_map'][risk_code]}")
            else:
                st.error("Missing required fields.")

# --- Tab 2: 企業白名單 ---
with tab2:
    st.subheader(t["tab2"])
    df = load_data()
    
    if not df.empty:
        allowlist = df[df["status_code"].isin(["APPROVED", "EXCEPTION"])].copy()
        
        if not allowlist.empty:
            allowlist["Risk"] = allowlist["risk_level_code"].map(t["risk_map"])
            allowlist["Status"] = allowlist["status_code"].map(t["status_map"])
            
            st.dataframe(allowlist[["tool_name", "vendor", "use_case", "Risk", "Status", "iso_control"]], use_container_width=True, hide_index=True)
            
            # UTF-8-SIG 避免 Excel 開啟中文 CSV 亂碼
            csv = allowlist.to_csv(index=False).encode('utf-8-sig')
            st.download_button(label="📥 下載白名單報告 (Export CSV)", data=csv, file_name='AI_Allowlist.csv', mime='text/csv')
        else:
            st.warning("No approved tools yet.")

# --- Tab 3: 管理員審計與後台 ---
with tab3:
    st.subheader(t["tab3"])
    admin_name = st.text_input("👨‍💼 操作員姓名 (Admin/Reviewer Name for Audit Log):")
    
    df = load_data()
    if not df.empty:
        view_df = df.copy()
        view_df["Risk Level"] = view_df["risk_level_code"].map(t["risk_map"])
        view_df["Status"] = view_df["status_code"].map(t["status_map"])
        
        edited_df = st.data_editor(
            view_df[["id", "timestamp", "tool_name", "data_class_code", "Risk Level", "Status", "last_modified_by"]],
            column_config={
                "id": None,
                "timestamp": st.column_config.Column(disabled=True),
                "tool_name": st.column_config.Column(disabled=True),
                "data_class_code": st.column_config.Column(disabled=True),
                "last_modified_by": st.column_config.Column(disabled=True),
                "Status": st.column_config.SelectboxColumn(options=list(t["status_map"].values()), required=True),
                "Risk Level": st.column_config.SelectboxColumn(options=list(t["risk_map"].values()), required=True)
            },
            use_container_width=True,
            key="admin_editor"
        )
        
        if st.button("💾 儲存變更 (Save Changes)"):
            if not admin_name:
                st.error("⚠️ 請輸入操作員姓名以建立審計軌跡 (Audit Log)！")
            else:
                for index, row in edited_df.iterrows():
                    orig_status = view_df.loc[index, "Status"]
                    orig_risk = view_df.loc[index, "Risk Level"]
                    
                    if row["Status"] != orig_status or row["Risk Level"] != orig_risk:
                        new_status_code = rev_status_map[row["Status"]]
                        new_risk_code = rev_risk_map[row["Risk Level"]]
                        update_record(row["id"], new_status_code, new_risk_code, admin_name)
                
                st.success("✅ 風險註冊表已更新，並記錄審計軌跡！")
                st.rerun()
