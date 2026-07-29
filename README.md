# 🛡️ Enterprise AI Risk Registry & Dashboard v2.0
### 企業級影子 AI 風險註冊表與動態監控駕駛艙

> **From Shadow IT to Governed Innovation** — An auditable AI Governance platform aligned with ISO 27001:2022 and ISO 42001:2023, featuring Continuous Lifecycle Monitoring.  
> **從影子 IT 到可控創新** — 對應 ISO 27001 與 ISO 42001 國際標準，且具備「持續生命週期監控」的企業級 AI 治理平台。

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-risk-registry.streamlit.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🚀 What's New in v2.0 / 全新升級功能

*   **Model Versioning (模型版本控制):** Track underlying foundation models (e.g., GPT-4o, Claude 3.5) to detect silent vendor updates and conceptual drift. / 追蹤底層基礎模型，應對供應商無聲更新風險。
*   **Risk-based Periodic Review (基於風險的定期審查):** Auto-schedule next review dates based on risk severity (HIGH: 6 months, MEDIUM: 12 months, LOW: 24 months). / 根據風險等級自動排程下次強制審核日。
*   **Compliance Alerts (合規警報儀表板):** Proactively flags overdue systems, enabling robust event-driven and time-driven monitoring (Domain IV Alignment). / 儀表板頂部自動攔截並警告逾期未審查的高風險系統。

---

## 📌 Executive Summary / 執行摘要

The rapid proliferation of Generative AI has created a significant governance challenge: **"Shadow AI."** Completely blocking these tools drives adoption underground, creating severe data leakage risks. 

**AI Risk Registry v2.0** is an open-source governance platform built on Streamlit. It operationalizes AI governance by providing a frictionless self-declaration portal for employees, an automated risk triage engine, and an **Event-Driven Continuous Monitoring** dashboard for management. It empowers GRC teams to maintain visibility over enterprise AI adoption while ensuring compliance with international standards.

生成式 AI 的普及帶來了嚴峻的治理挑戰——**「影子 AI」**。完全禁止只會讓風險轉入地下。**AI Risk Registry v2.0** 是一個基於 Streamlit 的開源 AI 管治平台。它透過員工自助申報門戶、自動化風險評級引擎，以及 **「事件驅動的持續監控機制」**，將影子 AI 轉化為透明、可控的資產，幫助資訊安全與 GRC 團隊在促進創新的同時，滿足國際資安與 AI 管理體系標準。

---

## ⚖️ ISO Standard & Control Mapping / 國際標準對照

| ISO Standard 控制項 | English Alignment | 繁體中文對照說明 |
| :--- | :--- | :--- |
| **ISO 27001:2022 A.5.19** | **Supplier Relationships:** Evaluates third-party AI vendor terms on model training and retention. | **供應商關係資訊安全：** 評估第三方 AI 供應商條款是否使用企業數據。 |
| **ISO 27001:2022 A.8.12** | **Data Leakage Prevention:** Flags submissions involving Confidential or PII data. | **防資料外洩：** 自動識別涉及機密資料或個人資料 (PII) 之申報。 |
| **ISO 27001:2022 A.12.4** | **Logging & Monitoring:** Timestamped audit logging tracking reviewer identity. | **日誌記錄：** 記錄所有審核變更之操作員姓名與時間戳記。 |
| **ISO 42001:2023 A.6** | **AI Risk Assessment:** Systematic identification and classification of AI system impact. | **AI 風險評估：** 針對 AI 系統之商業用途與風險等級進行結構化評估。 |
| **AIGP Domain IV** | **Continuous Monitoring:** Scheduled periodic reviews and foundation model tracking. | **持續監控與生命週期：** 落實定期審查與底層模型版本變更監控。 |

---

## 🚀 Quick Start / 快速部署

```bash
# Clone the repository
git clone [https://github.com/jackylawck/AI-Risk-Registry.git](https://github.com/jackylawck/AI-Risk-Registry.git)
cd AI-Risk-Registry

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app.py
