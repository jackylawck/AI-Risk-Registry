import os
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st

# ---------------------------------------------------------
# 1. 頁面基本設定與安全認證
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Risk Registry | 企業級 AI 工具風險註冊表",
    page_icon="🛡️",
    layout="wide",
)


def get_admin_password():
    """安全獲取管理員密碼：優先讀取 Streamlit Secrets，次之讀取環境變數，最後使用預設密碼"""
    try:
        return st.secrets["admin_password"]
    except Exception:
        return os.getenv("AI_REGISTRY_PASSWORD", "admin2026")


def check_password():
    """通行碼保護機制"""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.title("🔒 企業影子 AI 風險註冊表")
        pwd = st.text_input("請輸入企業通行碼 (Access Code)", type="password")
        target_pwd = get_admin_password()

        if pwd == target_pwd:
            st.session_state["password_correct"] = True
            st.rerun()
        elif pwd:
            st.error("密碼錯誤，請聯絡系統管理員。")
        return False
    return True


# ⚠️ 若要啟用通行碼保護，請取消下方兩行的註解 (Remove the '#' below)
# if not check_password():
#     st.stop()

DB_FILE = "shadow_ai_registry.db"
HK_TZ = ZoneInfo("Asia/Hong_Kong")


# ---------------------------------------------------------
# 2. 資料庫初始化 (SQLite WAL Mode + Cache 優化)
# ---------------------------------------------------------
def get_db_connection():
  conn = sqlite3.connect(DB_FILE, timeout=10)
  conn.execute("PRAGMA journal_mode=WAL;")
  return conn


def init_db():
  conn = get_db_connection()
  c = conn.cursor()
  c.execute("""
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
    """)
  conn.commit()
  conn.close()


init_db()


@st.cache_data(ttl=5)
def load_data():
  conn = get_db_connection()
  df = pd.read_sql_query("SELECT * FROM registry", conn)
  conn.close()
  return df


def update_records_batch(updates, admin_name):
  if not updates:
    return
  conn = get_db_connection()
  c = conn.cursor()
  mod_time = datetime.now(HK_TZ).strftime("%Y-%m-%d %H:%M:%S")
  try:
    for record_id, status_code, risk_code in updates:
      c.execute(
          """
                UPDATE registry 
                SET status_code = ?, risk_level_code = ?, last_modified_by = ?, last_modified_at = ?
                WHERE id = ?
            """,
          (status_code, risk_code, admin_name, mod_time, record_id),
      )
    conn.commit()
    st.cache_data.clear()  # 確保寫入成功後才清除快取
  except Exception as e:
    conn.rollback()
    raise e
  finally:
    conn.close()


# ---------------------------------------------------------
# 3. Enum 字典與 i18n 本地化
# ⚠️ 注意：維護者請確保各語言中的 Display Value 保持唯一性。
# ---------------------------------------------------------
TEXTS = {
    "zh": {
        "title": "🛡️ Enterprise AI Risk Registry & Dashboard",
        "caption": (
            "基於 ISO 27001 / ISO 42001 控制項之企業級影子 AI 治理駕駛艙"
        ),
        "tab1": "📝 員工自助申報",
        "tab2": "📋 認可工具白名單 (Allowlist)",
        "tab3": "⚙️ GRC 風險管理與審計",
        "m_total": "總申報數量",
        "m_pending": "待評估 / 審核中",
        "m_approved": "已獲核准 (含特許)",
        "m_high_risk": "高風險工具佔比",
        "chart_title": "📊 各部門 Shadow AI 採用與風險分布圖",
        "form_header": "申報新 AI 工具",
        "form_info": (
            "💡 依據企業資訊安全政策，使用任何未經審批之 AI 工具前請先完成申報。"
        ),
        "applicant": "申報人姓名",
        "dept": "所屬部門",
        "tool_name": "AI 工具名稱",
        "vendor": "服務供應商",
        "customer_facing": "輸出內容是否直接發布給客戶或用於自動決策？",
        "use_case": "商業用途說明",
        "submit_btn": "提交評估",
        "data_map": {
            "PUBLIC": "公開資料",
            "INTERNAL": "內部限閱",
            "CONFIDENTIAL": "機密資料",
            "PII": "個人資料 (PII/GDPR)",
        },
        "train_map": {"YES": "是", "NO": "否 / 已 Opt-Out", "UNSURE": "不確定"},
        "risk_map": {
            "LOW": "低風險 (Low)",
            "MEDIUM": "中風險 (Medium)",
            "HIGH": "高風險 (High)",
        },
        "status_map": {
            "SUBMITTED": "已提交 (Submitted)",
            "ASSESSING": "評估中 (Under Assessment)",
            "APPROVED": "正式核准 (Approved)",
            "REJECTED": "拒絕/需整改 (Rejected/Remediation Req.)",
            "EXCEPTION": "特許例外 (Exception Approved)",
        },
    },
    "en": {
        "title": "🛡️ Enterprise AI Risk Registry & Dashboard",
        "caption": (
            "Auditable AI Governance platform aligned with ISO 27001 / ISO"
            " 42001."
        ),
        "tab1": "📝 Self-Declaration",
        "tab2": "📋 Approved Allowlist",
        "tab3": "⚙️ GRC Admin Console",
        "m_total": "Total Declarations",
        "m_pending": "Pending Assessment",
        "m_approved": "Approved Tools",
        "m_high_risk": "High Risk Ratio",
        "chart_title": "📊 Shadow AI Adoption & Risk Profile by Department",
        "form_header": "Register Third-Party AI Tool",
        "form_info": (
            "💡 Declare unsanctioned AI tools prior to usage to ensure"
            " regulatory compliance."
        ),
        "applicant": "Applicant Name",
        "dept": "Department",
        "tool_name": "Tool Name",
        "vendor": "Vendor",
        "customer_facing": (
            "Is output customer-facing or used for automated decisions?"
        ),
        "use_case": "Business Use Case",
        "submit_btn": "Submit for Assessment",
        "data_map": {
            "PUBLIC": "Public",
            "INTERNAL": "Internal Only",
            "CONFIDENTIAL": "Confidential",
            "PII": "PII / Sensitive",
        },
        "train_map": {"YES": "Yes", "NO": "No / Opt-Out", "UNSURE": "Unsure"},
        "risk_map": {"LOW": "Low", "MEDIUM": "Medium", "HIGH": "High"},
        "status_map": {
            "SUBMITTED": "Submitted",
            "ASSESSING": "Under Assessment",
            "APPROVED": "Approved",
            "REJECTED": "Rejected / Remediation Req.",
            "EXCEPTION": "Exception Approved",
        },
    },
}

st.sidebar.title("🌐 Settings / 設定")
lang_choice = st.sidebar.selectbox("Language", ["繁體中文", "English"])
lang = "zh" if lang_choice == "繁體中文" else "en"
t = TEXTS[lang]

rev_data_map = {v: k for k, v in t["data_map"].items()}
rev_train_map = {v: k for k, v in t["train_map"].items()}
rev_risk_map = {v: k for k, v in t["risk_map"].items()}
rev_status_map = {v: k for k, v in t["status_map"].items()}


# ---------------------------------------------------------
# 4. 核心風險引擎
# ---------------------------------------------------------
def evaluate_risk(data_code, train_code, is_customer_facing):
  if (
      data_code in ["CONFIDENTIAL", "PII"]
      or train_code == "YES"
      or is_customer_facing
  ):
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

# 📊 Executive Risk Dashboard
df_all = load_data()

if not df_all.empty:
  total_count = len(df_all)
  pending_count = len(
      df_all[df_all["status_code"].isin(["SUBMITTED", "ASSESSING"])]
  )
  approved_count = len(
      df_all[df_all["status_code"].isin(["APPROVED", "EXCEPTION"])]
  )
  high_risk_count = len(df_all[df_all["risk_level_code"] == "HIGH"])
  high_risk_ratio = (
      f"{(high_risk_count / total_count * 100):.1f}%"
      if total_count > 0
      else "0%"
  )

  col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
  col_kpi1.metric(t["m_total"], total_count)
  col_kpi2.metric(t["m_pending"], pending_count, delta_color="inverse")
  col_kpi3.metric(t["m_approved"], approved_count)
  col_kpi4.metric(t["m_high_risk"], high_risk_ratio)

  with st.expander(t["chart_title"], expanded=False):
    df_chart = df_all.copy()
    df_chart["Risk"] = df_chart["risk_level_code"].map(t["risk_map"])
    dept_risk_summary = (
        df_chart.groupby(["department", "Risk"]).size().unstack(fill_value=0)
    )
    st.bar_chart(dept_risk_summary)

st.divider()

tab1, tab2, tab3 = st.tabs([t["tab1"], t["tab2"], t["tab3"]])

# --- Tab 1: 員工自助申報 ---
with tab1:
  st.subheader(t["form_header"])
  st.info(t["form_info"])

  with st.form("declaration_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
      applicant = st.text_input(t["applicant"])
      department = st.selectbox(
          t["dept"],
          ["HR", "Finance", "IT", "Marketing", "Legal", "Operations", "Other"],
      )
      tool_name = st.text_input(t["tool_name"])
      vendor = st.text_input(t["vendor"])
    with col2:
      data_disp = st.selectbox(
          "Data Classification", list(t["data_map"].values())
      )
      train_disp = st.radio(
          "Vendor Data Training", list(t["train_map"].values())
      )
      is_cust = st.checkbox(t["customer_facing"])

    use_case = st.text_area(t["use_case"])
    if st.form_submit_button(t["submit_btn"]):
      if applicant and tool_name:
        existing_tools = (
            df_all["tool_name"].str.lower().tolist() if not df_all.empty else []
        )

        if tool_name.lower() in existing_tools:
          st.error(
              f"⚠️ 工具 '{tool_name}' 已存在於風險註冊表中，請勿重複申報。"
          )
          st.stop()
        else:
          data_code = rev_data_map[data_disp]
          train_code = rev_train_map[train_disp]

          risk_code, iso_control = evaluate_risk(
              data_code, train_code, is_cust
          )
          status_code = "ASSESSING" if risk_code == "HIGH" else "SUBMITTED"

          conn = get_db_connection()
          c = conn.cursor()
          try:
            c.execute(
                """
                            INSERT INTO registry 
                            (timestamp, applicant, department, tool_name, vendor, use_case, data_class_code, trains_on_data_code, is_customer_facing, risk_level_code, iso_control, status_code, last_modified_by, last_modified_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                (
                    datetime.now(HK_TZ).strftime("%Y-%m-%d %H:%M:%S"),
                    applicant,
                    department,
                    tool_name,
                    vendor,
                    use_case,
                    data_code,
                    train_code,
                    is_cust,
                    risk_code,
                    iso_control,
                    status_code,
                    "System",
                    "",
                ),
            )
            conn.commit()
            st.cache_data.clear()
            st.toast(
                f"✅ Submitted! Assessed Risk: {t['risk_map'][risk_code]}",
                icon="🎉",
            )
          except Exception as e:
            conn.rollback()
            st.error("寫入資料庫時發生錯誤。")
          finally:
            conn.close()
      else:
        st.error("Missing required fields.")

# --- Tab 2: 企業白名單 ---
with tab2:
  st.subheader(t["tab2"])

  if not df_all.empty:
    allowlist = df_all[
        df_all["status_code"].isin(["APPROVED", "EXCEPTION"])
    ].copy()

    if not allowlist.empty:
      allowlist["Risk"] = allowlist["risk_level_code"].map(t["risk_map"])
      allowlist["Status"] = allowlist["status_code"].map(t["status_map"])

      st.dataframe(
          allowlist[[
              "tool_name",
              "vendor",
              "use_case",
              "Risk",
              "Status",
              "iso_control",
              "last_modified_at",
          ]],
          use_container_width=True,
          hide_index=True,
      )

      csv = allowlist.to_csv(index=False).encode("utf-8-sig")
      st.download_button(
          label="📥 下載白名單報告 (Export CSV)",
          data=csv,
          file_name="AI_Allowlist.csv",
          mime="text/csv",
      )
    else:
      st.warning("No approved tools in the registry.")
  else:
    st.write("尚無申報紀錄。")

# --- Tab 3: 管理員審計與後台 ---
with tab3:
  st.subheader(t["tab3"])
  admin_name = st.text_input(
      "👨‍💼 操作員姓名 (Admin/Reviewer Name for Audit Log):"
  )

  if not df_all.empty:
    view_df = df_all.copy()
    view_df["Risk Level"] = view_df["risk_level_code"].map(t["risk_map"])
    view_df["Status"] = view_df["status_code"].map(t["status_map"])

    col_f1, col_f2 = st.columns(2)
    with col_f1:
      selected_depts = st.multiselect(
          "過濾部門 (Filter Department)", options=view_df["department"].unique()
      )
    with col_f2:
      selected_statuses = st.multiselect(
          "過濾狀態 (Filter Status)", options=list(t["status_map"].values())
      )

    filtered_df = view_df.copy()
    if selected_depts:
      filtered_df = filtered_df[filtered_df["department"].isin(selected_depts)]
    if selected_statuses:
      filtered_df = filtered_df[filtered_df["Status"].isin(selected_statuses)]

    edited_df = st.data_editor(
        filtered_df[[
            "id",
            "timestamp",
            "tool_name",
            "department",
            "Risk Level",
            "Status",
            "last_modified_by",
            "last_modified_at",
        ]],
        column_config={
            "id": None,
            "timestamp": st.column_config.Column(disabled=True),
            "tool_name": st.column_config.Column(disabled=True),
            "department": st.column_config.Column(disabled=True),
            "last_modified_by": st.column_config.Column(disabled=True),
            "last_modified_at": st.column_config.Column(disabled=True),
            "Status": st.column_config.SelectboxColumn(
                options=list(t["status_map"].values()), required=True
            ),
            "Risk Level": st.column_config.SelectboxColumn(
                options=list(t["risk_map"].values()), required=True
            ),
        },
        use_container_width=True,
        key="admin_editor",
    )

    col_b1, col_b2 = st.columns([1, 4])
    with col_b1:
      if st.button("💾 儲存變更 (Save Changes)"):
        if not admin_name:
          st.error("⚠️ 請輸入操作員姓名以建立審計軌跡！")
        else:
          updates = []
          for index, row in edited_df.iterrows():
            orig_status = view_df.loc[
                view_df["id"] == row["id"], "Status"
            ].values[0]
            orig_risk = view_df.loc[
                view_df["id"] == row["id"], "Risk Level"
            ].values[0]

            if row["Status"] != orig_status or row["Risk Level"] != orig_risk:
              new_status_code = rev_status_map[row["Status"]]
              new_risk_code = rev_risk_map[row["Risk Level"]]
              updates.append((row["id"], new_status_code, new_risk_code))

          if updates:
            update_records_batch(updates, admin_name)
            st.toast("✅ 風險註冊表已更新！", icon="💾")
            st.rerun()
          else:
            st.info("無任何變更。")

    with col_b2:
      full_audit_csv = view_df.to_csv(index=False).encode("utf-8-sig")
      st.download_button(
          label="📊 匯出完整審計軌跡 (Export Audit Log CSV)",
          data=full_audit_csv,
          file_name="Full_AI_Audit_Log.csv",
          mime="text/csv",
      )
