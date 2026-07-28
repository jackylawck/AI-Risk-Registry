# 🛡️ Enterprise AI Risk Registry & Dynamic Allowlist
### 企業級影子 AI 風險註冊表與動態白名單

> **From Shadow IT to Governed Innovation** — An auditable, lightweight AI Governance platform aligned with ISO 27001:2022 and ISO 42001:2023 frameworks.  
> **從影子 IT 到可控創新** — 對應 ISO 27001:2022 與 ISO 42001:2023 國際標準的可審計輕量化 AI 治理平台。

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-risk-registry.streamlit.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

---

## 📌 Executive Summary / 執行摘要

### English
The rapid proliferation of Generative AI has created a significant governance challenge for modern enterprises: **"Shadow AI"** — unauthorized, ad-hoc usage of third-party, free-tier AI software by employees. Completely blocking these tools drives adoption underground, creating severe data leakage and compliance risks.

**AI Risk Registry** is an open-source, enterprise-grade governance platform built on Streamlit. It operationalizes AI governance by providing a frictionless self-declaration portal for employees, an automated risk triage engine, and a live, auditable Allowlist for management. It empowers Information Security (InfoSec), GRC teams, and CISOs to maintain visibility over enterprise AI adoption while ensuring compliance with international security standards.

### 繁體中文
生成式 AI 的普及為現代企業帶來了嚴峻的治理挑戰——**「影子 AI (Shadow AI)」**，即員工未經審批私自使用第三方免費 AI 軟體。完全禁止只會讓影子 AI 轉入地下，增加數據外洩與合規風險。

**AI Risk Registry（AI 工具風險註冊表）** 是一個基於 Streamlit 的企業級開源 AI 管治平台。它透過員工自助申報門戶、自動化風險評級引擎以及動態「認可白名單 (Allowlist)」，將影子 AI 轉化為透明、可控的資產，幫助資訊安全 (InfoSec) 與 GRC 團隊在促進創新的同時，滿足國際資安與 AI 管理體系標準。

---

## ✨ Key Features / 系統核心功能

| Feature 功能 | English Description | 繁體中文說明 |
| :--- | :--- | :--- |
| **Executive Dashboard**<br>管理層駕駛艙 | Top-level cockpit displaying total requests, pending reviews, high-risk ratio, and department risk profile. | 即時展示總申報數、待審核數、高風險工具佔比及各部門影子 AI 風險分布圖。 |
| **Self-Declaration Portal**<br>員工自助申報門戶 | Frictionless workflow capturing use cases, data classification, and vendor training policies. | 簡化申報流程，記錄商業用途、數據等級及供應商數據留存/訓練條款。 |
| **Automated Risk Engine**<br>自動化風險分級引擎 | Triages requests into High, Medium, or Low risk based on data sensitivity and customer exposure. | 根據資料敏感度及輸出情境，自動評估高/中/低風險等級並比對 ISO 控制項。 |
| **Enterprise Allowlist**<br>動態認可白名單 | Live list of approved AI tools with one-click Excel UTF-8-SIG CSV report export. | 動態維護公司認可工具清單，支援一鍵匯出 Excel 中文不亂碼之 CSV 報告。 |
| **Audit-Ready Console**<br>審計管理後台 | Admin interface with multi-criteria search/filtering, status mapping, and timestamped audit logs. | 後台支援多條件搜尋與過濾，修改狀態自動上記錄操作員與香港標準時間審計軌跡。 |
| **Duplicate Prevention**<br>工具重複申報檢測 | Pre-submission check against existing registry to prevent dirty data accumulation. | 提交前自動比對現有資料庫，若工具名稱重複即時阻擋，保持資料庫乾淨。 |
| **i18n Localization**<br>雙語流暢切換 | Seamless dynamic language switching between Traditional Chinese and English. | 側邊欄支援繁體中文與英文即時切換，底層代碼儲存解耦，邏輯堅如磐石。 |

---

## ⚖️ ISO Standard & Control Mapping / 國際標準對照

This platform maps user inputs directly to Information Security Management Systems (ISMS) and AI Management Systems (AIMS):  
系統將申報特徵直接對應至資安與 AI 管理體系標準控制項：

| ISO Standard 控制項 | English Alignment | 繁體中文對照說明 |
| :--- | :--- | :--- |
| **ISO 27001:2022 A.5.19** | **Supplier Relationships:** Evaluates third-party AI vendor terms on model training and retention. | **供應商關係資訊安全：** 評估第三方 AI 供應商條款是否使用企業數據進行模型訓練。 |
| **ISO 27001:2022 A.8.9** | **Configuration Management:** Maintains active inventory of approved operational AI tools. | **組態管理：** 維護全公司獲准使用的 AI 資產與工具白名單目錄。 |
| **ISO 27001:2022 A.8.12** | **Data Leakage Prevention:** Flags submissions involving Confidential or PII/GDPR data. | **防資料外洩：** 自動識別涉及機密資料或個人資料 (PII) 之高風險申報。 |
| **ISO 27001:2022 A.12.4** | **Logging & Monitoring:** Timestamped audit logging tracking reviewer identity for every change. | **日誌記錄：** 記錄所有審核變更之操作員姓名與時間戳記，確保不可否認性。 |
| **ISO 42001:2023 A.6** | **AI Risk Assessment:** Systematic identification and classification of AI system impact and risk. | **AI 風險評估：** 針對 AI 系統之商業用途、影響程度及風險等級進行結構化評估。 |

---

## 🚦 Risk Evaluation Architecture / 風險評估架構

```mermaid
graph TD
    A[Employee Submits AI Tool<br>員工申報 AI 工具] --> B{Data Class = PII / Confidential<br>OR Vendor Trains on Data<br>OR Customer Facing?}
    B -- Yes / 是 --> C[🔴 HIGH RISK / 高風險]
    C --> C1[ISO 27001 A.8.12 & ISO 42001 A.6]
    C1 --> C2[Status: Under Assessment / 評估中]
    
    B -- No / 否 --> D{Data Class = Internal Only<br>內部限閱?}
    D -- Yes / 是 --> E[🟡 MEDIUM RISK / 中風險]
    E --> E1[ISO 27001 A.5.19]
    E1 --> E2[Status: Submitted / 已提交]
    
    D -- No / 否 --> F[🟢 LOW RISK / 低風險]
    F --> F1[ISO 27001 A.8.9]
    F1 --> F2[Status: Submitted / 已提交]
