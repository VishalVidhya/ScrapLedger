# ScrapLedger

## Product
ScrapLedger turns Central Pollution Control Board (CPCB) e-waste and battery waste rules into clear, structured Extended Producer Responsibility (EPR) checklists for electronics firms. It acts as a one-click EPR checklist generator for specific producer types, exporting obligations as validated JSON or printable lists. It also features a natural-language data analyst agent (using safe, read-only SQL) to track a firm's EPR targets against filed quantities in a Postgres database, citing the exact rule behind each target.

## Target User
EHS (Environment, Health, and Safety) executives at electronics manufacturing units (e.g., in Hosur), who are responsible for ensuring strict environmental compliance.

## The Problem
Electronics makers and recyclers must meet stringent EPR targets under the E-Waste and Battery Waste rules. The rules, SOPs, and amendments are scattered across 800+ pages of dense legal and technical text. Missing a filing step, misunderstanding a formula, or missing a deadline directly leads to heavy financial penalties and environmental compensation charges. 

## Dataset Source and Size
*   **Source:** Central Pollution Control Board (CPCB) official portal (https://cpcb.nic.in/)
*   **Documents:** E-Waste (Management) Rules 2022 and subsequent amendments, Battery Waste Management Rules 2022, CPCB EPR guidelines, SOPs, and relevant hazardous waste rules.
*   **Size:** Minimum 800+ pages of PDF documents. (First 50+ pages collected for initial prototype).

## 10 Real Questions 
1. What are the EPR collection targets for a producer of laptops in 2026-27?
2. What returns must a registered recycler file and by when?
3. What is the penalty for selling batteries without EPR registration?
4. What is the exact formula to calculate the EPR obligation for a new manufacturer of portable batteries?
5. Which specific forms must be submitted for the annual e-waste return, and what is the exact deadline?
6. Under the 2022 rules, what are the specific EPR recycling targets for solar photo-voltaic modules?
7. How long is an EPR registration valid before a producer needs to apply for renewal?
8. What are the specific environmental compensation (EC) charges for a 20% shortfall in meeting e-waste collection targets?
9. Does a company importing batteries for captive consumption need to register on the EPR portal?
10. **(Unanswerable by the documents):** Which local logistics vendor in Hosur offers the cheapest rates for moving hazardous e-waste to a registered recycling facility?