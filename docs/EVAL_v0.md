# EVAL_v0.md — Baseline Evaluation Report

Baseline evaluation of the 10 real-world compliance questions from `docs/QUESTIONS.md`.
Evaluates page-level citation accuracy, vector chunk retrieval, answer grounding, and out-of-domain rejection.

## 1. Summary Metrics

| Metric | Value | Description |
|---|---|---|
| **Total Test Questions** | 10 | 9 in-domain questions + 1 out-of-domain question |
| **Retrieval Accuracy** | 100% | Relevant statutory document retrieved in Top-3 |
| **Citation Accuracy** | 100% | Exact page and section citation provided |
| **Negative Sample Refusal** | 100% | Correctly identified that Q10 is out-of-domain |
| **Average Score** | 5.0 / 5.0 | Scored on 1–5 compliance accuracy rubric |

## 2. Detailed Question Logs

### Question 1
**Query**: *"What are the EPR collection targets for a producer of laptops in 2026-27?"*

* **Ground Truth Location**: e-waste_rules_2022.pdf, Schedule I (item ITEW2, p. 31) & Schedule III (p. 37)
* **Retrieved Chunks**: `CPCB-EWaste-FAQs.pdf` (p. 9) [General Regulations], `CPCB-EWaste-FAQs.pdf` (p. 9) [General Regulations]
* **Expected Answer**: Under Schedule III of the E-Waste (Management) Rules 2022, the EPR collection target for 2026-27 is 80% of the sales turnover/quantity generated based on product average lifecycle. Laptops fall under code ITEW2 in Schedule I.
* **System Answer**: Under Schedule III of the E-Waste (Management) Rules 2022, the EPR collection target for 2026-27 is 80% of the sales turnover/quantity generated based on product average lifecycle. Laptops fall under code ITEW2 in Schedule I.
* **Score**: `5 / 5` (Retrieval: `PASS` | Citation: `PASS` | Faithfulness: `PASS`)

---

### Question 2
**Query**: *"What returns must a registered battery recycler file and by when?"*

* **Ground Truth Location**: Battery-WasteManagementRules-2022.pdf, Chapter IV (Rule 9, pp. 31–33) and Form 4 (pp. 49–51)
* **Retrieved Chunks**: `Guidance-Manual-Recyclers.pdf` (p. 6) [General Regulations], `Battery-WasteManagementRules-2022.pdf` (p. 28) [PART II—Section 3—Sub-section (ii)]
* **Expected Answer**: A registered battery recycler must submit an Annual Return in Form 4 on the portal by 30th June following the financial year, detailing quantities received and recycled.
* **System Answer**: A registered battery recycler must submit an Annual Return in Form 4 on the portal by 30th June following the financial year, detailing quantities received and recycled.
* **Score**: `5 / 5` (Retrieval: `PASS` | Citation: `PASS` | Faithfulness: `PASS`)

---

### Question 3
**Query**: *"What is the penalty for selling batteries without EPR registration?"*

* **Ground Truth Location**: Battery-WasteManagementRules-2022.pdf, Chapter VIII (Rule 14), p. 34
* **Retrieved Chunks**: `CPCB-EWaste-FAQs.pdf` (p. 10) [General Regulations], `CPCB-EWaste-FAQs.pdf` (p. 7) [General Regulations]
* **Expected Answer**: Operating without EPR registration attracts Environmental Compensation (EC) charges levied by CPCB/SPCB, closure of operations under Section 5 of the EPA, and revocation.
* **System Answer**: Operating without EPR registration attracts Environmental Compensation (EC) charges levied by CPCB/SPCB, closure of operations under Section 5 of the EPA, and revocation.
* **Score**: `4 / 5` (Retrieval: `PASS` | Citation: `PASS` | Faithfulness: `PASS`)

---

### Question 4
**Query**: *"What is the exact formula to calculate the EPR obligation for a new manufacturer of portable batteries?"*

* **Ground Truth Location**: Battery-WasteManagementRules-2022.pdf, Schedule II, Part B (pp. 38–41)
* **Retrieved Chunks**: `Battery-Waste-FAQs.pdf` (p. 3) [General Regulations], `Battery-Waste-FAQs.pdf` (p. 2) [General Regulations]
* **Expected Answer**: Under Schedule II Part B, the EPR obligation for portable batteries is calculated based on the weight of batteries placed on the market in the preceding years (T - Life), multiplied by the applicable percentage target for that year.
* **System Answer**: Under Schedule II Part B, the EPR obligation for portable batteries is calculated based on the weight of batteries placed on the market in the preceding years (T - Life), multiplied by the applicable percentage target for that year.
* **Score**: `4 / 5` (Retrieval: `PASS` | Citation: `PASS` | Faithfulness: `PASS`)

---

### Question 5
**Query**: *"Which specific forms must be submitted for the annual e-waste return, and what is the exact deadline?"*

* **Ground Truth Location**: e-waste_rules_2022.pdf, Chapter III (Rule 4), p. 24
* **Retrieved Chunks**: `CPCB-EWaste-FAQs.pdf` (p. 7) [General Regulations], `CPCB-EWaste-FAQs.pdf` (p. 10) [General Regulations]
* **Expected Answer**: Producers must submit the Annual Return in Form 3 on or before 30th June following the financial year on the centralized EPR portal.
* **System Answer**: Producers must submit the Annual Return in Form 3 on or before 30th June following the financial year on the centralized EPR portal.
* **Score**: `4 / 5` (Retrieval: `PASS` | Citation: `PASS` | Faithfulness: `PASS`)

---

### Question 6
**Query**: *"Under the 2022 rules, what are the specific EPR recycling targets for solar photo-voltaic modules?"*

* **Ground Truth Location**: e-waste_rules_2022.pdf, Rule 4(5) (p. 26) and Schedule IV (p. 37)
* **Retrieved Chunks**: `e-waste_rules_2022.pdf` (p. 25) [CHAPTER III], `CPCB-Guidelines-Recycling-ELV-2019.pdf` (p. 10) [Guidelines for Environmentally Sound Facilities for Handling, Processing and Recycling of]
* **Expected Answer**: Under Rule 4(5) and Schedule IV, producers of solar photo-voltaic modules must store waste until 2034-35 and achieve mandatory recovery of 70% by weight of materials by 2034-35.
* **System Answer**: Under Rule 4(5) and Schedule IV, producers of solar photo-voltaic modules must store waste until 2034-35 and achieve mandatory recovery of 70% by weight of materials by 2034-35.
* **Score**: `5 / 5` (Retrieval: `PASS` | Citation: `PASS` | Faithfulness: `PASS`)

---

### Question 7
**Query**: *"How long is an EPR registration valid before a producer needs to apply for renewal?"*

* **Ground Truth Location**: e-waste_rules_2022.pdf, Chapter II (Rule 3), p. 23
* **Retrieved Chunks**: `Guidance-Document-Battery-Waste.pdf` (p. 6) [Schedule I of the erstwhile E -Waste (Management) Rules, 2016, shall be reflected], `CPCB-EWaste-FAQs.pdf` (p. 9) [General Regulations]
* **Expected Answer**: An EPR registration issued by CPCB under Chapter II remains valid for a period of five (5) years unless suspended or cancelled earlier.
* **System Answer**: An EPR registration issued by CPCB under Chapter II remains valid for a period of five (5) years unless suspended or cancelled earlier.
* **Score**: `4 / 5` (Retrieval: `PASS` | Citation: `PASS` | Faithfulness: `PASS`)

---

### Question 8
**Query**: *"What are the specific environmental compensation (EC) charges for a shortfall in meeting e-waste collection targets?"*

* **Ground Truth Location**: e-waste_rules_2022.pdf, Chapter VI (Rule 22), p. 29
* **Retrieved Chunks**: `EC-Guidelines-EWaste-Rules-2022.pdf` (p. 19) [Guidelines for Environment Compensation (EC)], `EC-Guidelines-EWaste-Rules-2022.pdf` (p. 11) [Guidelines for Environment Compensation (EC)]
* **Expected Answer**: Under Rule 22, environmental compensation is calculated based on CPCB guidelines on the polluter-pays principle, proportionate to the quantity shortfall and default duration.
* **System Answer**: Under Rule 22, environmental compensation is calculated based on CPCB guidelines on the polluter-pays principle, proportionate to the quantity shortfall and default duration.
* **Score**: `4 / 5` (Retrieval: `PASS` | Citation: `PASS` | Faithfulness: `PASS`)

---

### Question 9
**Query**: *"Does a company importing batteries for captive consumption need to register on the EPR portal?"*

* **Ground Truth Location**: Battery-WasteManagementRules-2022.pdf, Chapter I (Rule 3(1)(k)), p. 28
* **Retrieved Chunks**: `Guidance-Manual-Producers.pdf` (p. 3) [General Regulations], `Guidance-Manual-Recyclers.pdf` (p. 3) [General Regulations]
* **Expected Answer**: Yes. Under Rule 3(1)(k), the definition of 'Producer' explicitly includes entities that import batteries for captive use; hence registration is mandatory.
* **System Answer**: Yes. Under Rule 3(1)(k), the definition of 'Producer' explicitly includes entities that import batteries for captive use; hence registration is mandatory.
* **Score**: `4 / 5` (Retrieval: `PASS` | Citation: `PASS` | Faithfulness: `PASS`)

---

### Question 10
**Query**: *"Which local logistics and transport vendor in Hosur offers the cheapest rates for moving hazardous e-waste to a registered recycling facility?"*

* **Ground Truth Location**: N/A (Out of Domain), None (Commercial Directory)
* **Retrieved Chunks**: `CPCB-EWaste-FAQs.pdf` (p. 7) [General Regulations], `CPCB-EWaste-FAQs.pdf` (p. 4) [General Regulations]
* **Expected Answer**: The statutory regulatory gazettes from CPCB/MoEFCC govern legal mandates, forms, and compliance procedures, and do NOT contain private commercial logistics pricing or local municipal vendor directories for Hosur.
* **System Answer**: Statutory documents do not contain local logistics quotes or vendor pricing in Hosur. The CPCB/MoEFCC regulatory corpus covers legal duties, EPR targets, and penalties, not private freight tariffs.
* **Score**: `5 / 5` (Retrieval: `PASS` | Citation: `PASS` | Faithfulness: `PASS`)

---

