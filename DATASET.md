# Dataset

| File | Source URL | Pages | Licence / terms | Downloaded on |
|---|---|---|---|---|
| `Battery-WasteManagementRules-2022.pdf` | [eprbattery.cpcb.gov.in](https://eprbattery.cpcb.gov.in/upload/adminDoc/Battery-WasteManagementRules-2022.pdf) | 51 | Public domain Indian regulatory gazette (CPCB) | 2026-10-25 |
| `e-waste_rules_2022.pdf` | [eprewaste.cpcb.gov.in](https://eprewaste.cpcb.gov.in/assets/PDF/e-waste_rules_2022.pdf) | 38 | Public domain Indian regulatory gazette (CPCB) | 2026-10-25 |
| `Hazardous-Waste-Rules-2016.pdf` | [cpcb.gov.in](https://cpcb.gov.in/displaypdf.php?id=aHdtZC9Id21fcnVsZXNfMjAxNi5wZGY=) | 97 | Public domain Indian regulatory gazette (MoEFCC/CPCB) | 2026-10-25 |
| `CPCB-Guidelines-Recycling-ELV-2019.pdf` | [cpcb.gov.in](https://cpcb.gov.in/uploads/hwmd/Guidelines_Handling_Processing_and_Recycling_ELV_11.03.2019.pdf) | 41 | Public domain Indian regulatory guidelines (CPCB) | 2026-10-25 |
| `Guidance-Manual-Refurbishers.pdf` | [eprbattery.cpcb.gov.in](https://eprbattery.cpcb.gov.in/upload/adminDoc/GuidanceManuals/Guidance%20Manual%20Refurbisher.pdf) | 44 | Public domain compliance guidance manual (CPCB) | 2026-10-25 |
| `Guidance-Manual-Recyclers.pdf` | [eprbattery.cpcb.gov.in](https://eprbattery.cpcb.gov.in/upload/adminDoc/GuidanceManuals/Guidance%20Manual%20Recyclers.pdf) | 33 | Public domain compliance guidance manual (CPCB) | 2026-10-25 |
| `Guidance-Manual-Producers.pdf` | [eprbattery.cpcb.gov.in](https://eprbattery.cpcb.gov.in/upload/adminDoc/GuidanceManuals/Guidance%20Manual%20Producers.pdf) | 20 | Public domain compliance guidance manual (CPCB) | 2026-10-25 |
| `EC-Guidelines-EWaste-Rules-2022.pdf` | [eprewaste.cpcb.gov.in](https://eprewaste.cpcb.gov.in/assets/PDF/EC-Guidelines-under-E-Waste-Management-Rules-2022-25.08.25.pdf.pdf) | 20 | Public domain Environmental Compensation guidelines | 2026-10-25 |
| `CPCB-Environmental-Compensation-Guidelines-Batteries.pdf` | [eprbattery.cpcb.gov.in](https://eprbattery.cpcb.gov.in/upload/adminDoc/Notice_EC%20Guidelines.pdf) | 13 | Public domain Environmental Compensation guidelines | 2026-10-25 |
| `Battery-Waste-Management-Amendment-Rules-2023.pdf` | [eprbattery.cpcb.gov.in](https://eprbattery.cpcb.gov.in/upload/adminDoc/Battery-Waste-Management-(Amendment)-Rules-2023.pdf) | 13 | Public domain statutory amendment gazette | 2026-10-25 |
| `CPCB-EWaste-FAQs.pdf` | [eprewaste.cpcb.gov.in](https://eprewaste.cpcb.gov.in/assets/PDF/faqewaste.pdf) | 13 | Public domain CPCB FAQ document | 2026-10-25 |
| `Guidance-Document-EWaste-EPR-Certificates.pdf` | [eprewaste.cpcb.gov.in](https://eprewaste.cpcb.gov.in/assets/Guidance%20document%20for%20E-Waste%20-%20generation%20and%20transfer%20of%20EPR%20Certificate_Final%20(1).pdf) | 12 | Public domain EPR generation & transfer guide | 2026-10-25 |
| `CPCB-SOP-Battery-Recyclers.pdf` | [eprbattery.cpcb.gov.in](https://eprbattery.cpcb.gov.in/upload/adminDoc/SoP_for_recyclers.pdf) | 10 | Public domain standard operating procedure | 2026-10-25 |
| `Battery-SOP-Producers-Recyclers.pdf` | [eprbattery.cpcb.gov.in](https://eprbattery.cpcb.gov.in/upload/adminDoc/SOP.pdf) | 10 | Public domain SOP guidance manual | 2026-10-25 |
| *Other statutory orders, SOPs & guidance (24 additional files)* | [eprbattery.cpcb.gov.in](https://eprbattery.cpcb.gov.in/) | 124 | Public domain official CPCB notices & circulars | 2026-10-25 |

Full data lives in `data/raw/` (**38 files, 537 pages total**, exceeding the 500+ page requirement). A representative sample lives in `data/sample/`.

## Overview
This dataset contains official statutory regulatory gazettes and Standard Operating Procedures (SOPs) from the Ministry of Environment, Forest and Climate Change (MoEFCC) and Central Pollution Control Board (CPCB) of India detailing Extended Producer Responsibility (EPR) mandates, recycling quotas, return timelines, End-of-Life Vehicles (ELV) recycling, hazardous waste management, and environmental compensation formulas.

## Source Details
* **Primary Source Portals:**
  * CPCB E-Waste EPR Portal: [eprewaste.cpcb.gov.in](https://eprewaste.cpcb.gov.in/)
  * CPCB Battery Waste EPR Portal: [eprbattery.cpcb.gov.in](https://eprbattery.cpcb.gov.in/)
  * CPCB Official Portal: [cpcb.gov.in](https://cpcb.gov.in/)
* **Licence / Terms:** Publicly available official Indian government gazette notifications and statutory circulars (free for academic, compliance, and public access).
* **Collection Size:** 537 pages collected across 38 files in `data/raw/`.

## Collection Method
Files were retrieved using the polite downloader script ([`app/tools/download.py`](app/tools/download.py)), which checks `robots.txt`, applies rate limiting between requests, and logs source URLs, download timestamps, file size in bytes, and SHA256 checksums into [`data/manifest.csv`](data/manifest.csv) for complete data provenance.
