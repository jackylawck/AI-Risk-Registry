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
# 2. 資料庫初始化 (啟用 WAL Mode 解決 Concurrency 併發問題)
# ---------------------------------------------------------
def get_db_connection():
    conn = sqlite3.connect(DB_FILE, timeout=10)
    # 啟用 WAL Mode (Write-Ahead Logging) 大幅提升多使用者同時存取的效能
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    conn = get_db_connection()
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
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM registry", conn)
    conn.close()
    return df

def update_records_batch(updates, admin_name):
    """批次更新 Transaction 機制，避免多 Row 更新中途斷線導致資料不一致"""
    if not updates:
        return
    conn = get_db_connection()
    c = conn.cursor()
    mod_time = datetime.now(HK_TZ).strftime("%Y-%m-%d %H:%M:%S")
    try:
        for record_id, status_code, risk_code in updates:
            c.execute('''
                UPDATE registry 
                SET status_code = ?, risk_level_code = ?, last_modified_by = ?, last_modified_at = ?
                WHERE id = ?
            ''', (status_code, risk_code, admin_name, mod_time, record_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# ---------------------------------------------------------
# 3. Enum 字典與 i18n 本地化
# ---------------------------------------------------------
TEXTS = {
    "zh": {
        "title": "🛡️ Enterprise AI Risk Registry & Dashboard",
        "caption": "基於 ISO 27001 / ISO 42001 控制項之企業級影子 AI 治理駕駛艙",
        "tab1": "📝 員工自助申報",
        "tab2": "📋 認可工具白名單 (Allowlist)",
        "tab3": "⚙️ GRC 風險管理與審計",
        
        # Dashboard Metrics
        "m_total": "總申報數量",
        "m_pending": "待評估 / 審核中",
        "m_approved": "已獲核准 (含特許)",
        "m_high_risk": "高風險工具佔比",
        "chart_title": "📊 各部門 Shadow AI 採用與風險分布圖",
        
        # Form
        "form_header": "申報新 AI 工具",
        "form_info": "💡 依據企業資訊安全政策，使用任何未經審批之 AI 工具前請先完成申報。",
        "applicant": "申報人姓名",
        "dept": "所屬部門",
        "tool_name": "AI 工具名稱",
        "vendor": "服務供應商",
        "customer_facing": "輸出內容是否直接發布給客戶或用於自動決策？",
        "use_case": "商業用途說明",
        "submit_btn": "提交評估",
        
        # Mappings
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
        "title": "🛡️ Enterprise AI Risk Registry & Dashboard",
        "caption": "Auditable AI Governance platform aligned with ISO 27001 / ISO 42001.",
        "tab1": "📝 Self-Declaration",
        "tab2": "📋 Approved Allowlist",
        "tab3": "⚙️ GRC Admin Console",
        
        # Dashboard Metrics
        "m_total": "Total Declarations",
        "m_pending": "Pending Assessment",
        "m_approved": "Approved Tools",
        "m_high_risk": "High Risk Ratio",
        "chart_title": "📊 Shadow AI Adoption & Risk Profile by Department",
        
        # Form
        "form_header": "Register Third-Party AI Tool",
        "form_info": "💡 Declare unsanctioned AI tools prior to usage to ensure regulatory compliance.",
        "applicant": "Applicant Name",
        "dept": "Department",
        "tool_name": "Tool Name",
        "vendor": "Vendor",
        "customer_facing": "Is output customer-facing or used for automated decisions?",
        "use_case": "Business Use Case",
        "submit_btn": "Submit for Assessment",
        
        # Mappings
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

st.sidebar.title("🌐 Settings / 設定")
lang_choice = st.sidebar.selectbox("Language", ["繁體中文", "English"])
lang = "zh" if lang_choice == "繁體中文" else "en"
t = TEXTS[lang]

# 反向 Mapping
rev_data_map = {v: k for k, v in t["data_map"].items()}
rev_train_map = {v: k for k, v in t["train_map"].items()}
rev_risk_map = {v: k for k, v in t["risk_map"].items()}
rev_status_map = {v: k for k, v in t["status_map"].items()}

# ---------------------------------------------------------
# 4. 核心風險引擎
# ---------------------------------------------------------
def evaluate_risk(data_code, train_code, is_customer_facing):
    if data_code in ["CONFIDENTIAL", "PII"] or train_code == "YES" or is_customer_facing:
        return "HIGH", "ISO 27001 A.8.12 & ISO 42001 A.6"
    elif data_code == "INTERNAL":
        return "MEDIUM", "ISO 27001 A.5.19"
    else:
        return "LOW", "ISO 27001 A.8.9"

# ---------------------------------------------------------
# 5. 主介面與 Executive Dashboard 渲染
# ---------------------------------------------------------
st.title(t["title"])
st.caption(t["caption"])

# 📊 Executive Risk Dashboard (頂部管理層駕駛艙)
df_all = load_data()

if not df_all.empty:
    total_count = len(df_all)
    pending_count = len(df_all[df_all["status_code"].isin(["SUBMITTED", "ASSESSING"])])
    approved_count = len(df_all[df_all["status_code"].isin(["APPROVED", "EXCEPTION"])])
    high_risk_count = len(df_all[df_all["risk_level_code"] == "HIGH"])
    high_risk_ratio = f"{(high_risk_count / total_count * 100):.1f}%" if total_count > 0 else "0%"

    # KPI 關鍵指標卡片
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    col_kpi1.metric(t["m_total"], total_count)
    col_kpi2.metric(t["m_pending"], pending_count, delta_color="inverse")
    col_kpi3.metric(t["m_approved"], approved_count)
    col_kpi4.metric(t["m_high_risk"], high_risk_ratio)

    # 圖表：部門 vs 風險等級分布 (圖表預設收合，保持介面簡潔)
    with st.expander(t["chart_title"], expanded=False):
        df_chart = df_all.copy()
        df_chart["Risk"] = df_chart["risk_level_code"].map(t["risk_map"])
        dept_risk_summary = df_chart.groupby(["department", "Risk"]).size().unstack(fill_value=0)
        st.bar_chart(dept_risk_summary)

st.divider()

# 分頁結構
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
                
                conn = get_db_connection()
                c = conn.cursor()
                c.execute('''
                    INSERT INTO registry 
                    (timestamp, applicant, department, tool_name, vendor, use_case, data_class_code, trains_on_data_code, is_customer_facing, risk_level_code, iso_control, status_code, last_modified_by, last_modified_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (datetime.now(HK_TZ).strftime("%Y-%m-%d %H:%M:%S"), applicant, department, tool_name, vendor, use_case, data_code, train_code, is_cust, risk_code, iso_control, status_code, "System", ""))
                conn.commit()
                conn.close()
                st.success(f"✅ Submitted! Assessed Risk: {t['risk_map'][risk_code]}")
                st.rerun()
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
            
            st.dataframe(
                allowlist[["tool_name", "vendor", "use_case", "Risk", "Status", "iso_control", "last_modified_at"]], 
                use_container_width=True, 
                hide_index=True
            )
            
            # 匯出 CSV 報告 (UTF-8-SIG 確保中文字體不會在 Excel 顯示亂碼)
            csv = allowlist.to_csv(index=False).encode('utf-8-sig')
            st.download_button(label="📥 下載白名單報告 (Export CSV)", data=csv, file_name='AI_Allowlist.csv', mime='text/csv')
        else:
            st.warning("No approved tools in the registry.")

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
            view_df[["id", "timestamp", "tool_name", "department", "Risk Level", "Status", "last_modified_by", "last_modified_at"]],
            column_config={
                "id": None,
                "timestamp": st.column_config.Column(disabled=True),
                "tool_name": st.column_config.Column(disabled=True),
                "department": st.column_config.Column(disabled=True),
                "last_modified_by": st.column_config.Column(disabled=True),
                "last_modified_at": st.column_config.Column(disabled=True),
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
                updates = []
                for index, row in edited_df.iterrows():
                    orig_status = view_df.loc[index, "Status"]
                    orig_risk = view_df.loc[index, "Risk Level"]
                    
                    if row["Status"] != orig_status or row["Risk Level"] != orig_risk:
                        new_status_code = rev_status_map[row["Status"]]
                        new_risk_code = rev_risk_map[row["Risk Level"]]
                        updates.append((row["id"], new_status_code, new_risk_code))
                
                if updates:
                    update_records_batch(updates, admin_name)
                    st.success("✅ 風險註冊表已更新，並完整記錄審計軌跡！")
                    st.rerun()
                else:
                    st.info("無任何變更。")
