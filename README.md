# 🛡️ AI Risk Registry (AI 工具風險註冊表)

> **From Shadow IT to Governed Innovation — an auditable risk registry for enterprise AI adoption.**

The **AI Risk Registry** is a lightweight, zero-cost governance platform built on Streamlit. It addresses the critical challenge of "Shadow AI" by providing a structured, centralized workflow for employees to declare third-party AI tools. The system automatically performs risk stratification and control mapping, generating a dynamic Allowlist for enterprise use.

## 🎯 Value Proposition

In the era of Generative AI, completely blocking free AI tools drives usage underground, increasing data leakage risks. This tool adopts a "trust but verify" approach:
* **For Employees:** A simple, frictionless portal to request AI tools.
* **For Governance & IT Teams:** Automated risk scoring (High/Medium/Low) based on data classification and vendor training policies.
* **For the Board & Management:** Clear visibility into enterprise AI exposure, ensuring compliance with international frameworks.

## ⚖️ Compliance & Framework Alignment

This registry is designed with standard Information Security Management Systems (ISMS) and AI Management Systems (AIMS) in mind:
* **ISO 27001:2022:** Maps to Annex A controls (e.g., A.5.19 Supplier Relationships, A.8.12 Data Leakage Prevention).
* **ISO 42001:2023:** Supports AI risk assessment and third-party AI resource governance.

## 🚀 Key Features

1. **Self-Service Declaration Portal:** Captures use cases, data classification (Public, Internal, Confidential, PII), and vendor data retention policies.
2. **Automated Risk Triage:** A built-in rule engine that immediately flags high-risk applications (e.g., tools training on user data or handling PII).
3. **Dynamic Allowlist Dashboard:** Real-time visibility of approved, conditionally approved, and banned AI tools across different departments.
4. **Audit-Ready Registry:** Maintains a permanent timestamped log of who requested what, and the corresponding security controls applied.

## 🛠️ Architecture & Deployment

* **Frontend & Logic:** Streamlit (Python)
* **Hosting:** Streamlit Community Cloud (Zero-cost deployment)
* **Data Persistence:** GitHub repository (via CSV) or Google Sheets API

---
*Built for modern organizations to scale AI securely and responsibly.*
