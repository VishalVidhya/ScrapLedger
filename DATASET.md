# Dataset Documentation

## Overview
This dataset contains official government regulatory documents from the Central Pollution Control Board (CPCB) of India detailing Extended Producer Responsibility (EPR) obligations.

## Source Details
* **Primary Source:** Central Pollution Control Board (CPCB) official portal (https://cpcb.nic.in/)
* **Licence/Terms:** Publicly available government regulatory documents.
* **Initial Collection:** 50+ pages of core regulations.

## File Inventory (`data/sample/`)
1. **E-Waste (Management) Rules 2022:** Contains rules, schedules, and EPR target formulas for electronics manufacturers.
2. **Battery Waste Management Rules 2022:** Contains compliance mandates, formulas, and deadlines for battery producers and recyclers.

## Collection Method
Files were downloaded using a polite Python script (`app/tools/download.py`) which logs the source URL, download date, file size, and SHA256 checksum into `data/manifest.csv` to ensure data traceability.
