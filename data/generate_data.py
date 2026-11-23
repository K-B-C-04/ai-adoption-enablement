"""
Generate the synthetic dataset for AI Adoption & Enablement.

Wazobia Corp is a fictional company. Its internal AI assistant, "Ask Wazobia", answers
employee questions from a curated knowledge base. Every topic, ticket, person and
figure here is invented. No real company data is used.

Four linked datasets:
  topics.csv     knowledge-base topics: owner department, risk tier, curator, status,
                 and the support-ticket demand each topic would absorb
  evidence.csv   example support tickets showing why each topic is needed
  adoption.csv   weekly usage of the assistant by department since launch
  controls.csv   governance controls required before a topic can go live

Patterns planted so the analysis has decisions to support:
  - Business Technology moved first; Finance, People and Legal content lags.
  - Topics with a named curator ship far more often than unowned topics.
  - Tier 1 (compliance and personal data) topics carry high demand but sit in review.
  - Departments with more live content adopt the assistant faster and escalate less.

Usage (from data/):  python generate_data.py
"""
import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(11)
HERE = Path(__file__).resolve().parent
AS_OF = date(2026, 11, 20)
LAUNCH = date(2026, 6, 1)

DEPARTMENTS = {  # department -> headcount
    "Business Technology": 140, "Finance": 85, "People": 60, "Legal": 40,
    "Facilities": 30, "Sales Operations": 160, "Security": 35,
}
CURATORS = ["Curator A", "Curator B", "Curator C", "Curator D", "Curator E", "Curator F"]

# (department, category, topic, risk tier, tickets in last 90 days, avg handle minutes, [example tickets])
T = [
    ("Business Technology", "Hardware", "Laptop and peripheral setup", 3, 310, 25,
     ["My new monitor won't wake up when docked. I've tried two cables.", "Need a second charger and a keyboard for my home office."]),
    ("Business Technology", "Access", "Password reset and MFA", 2, 420, 12,
     ["Locked out after changing phones; the authenticator app shows no codes.", "Password expired while I was on leave and the reset link fails."]),
    ("Business Technology", "Network", "VPN and remote access", 2, 205, 30,
     ["VPN disconnects every few minutes when I'm working from home.", "Can't reach the shared drive unless I'm in the office."]),
    ("Business Technology", "Software", "Software requests and licensing", 3, 260, 18,
     ["How do I request a license for the diagramming tool?", "My analytics license expired and I need it for month-end."]),
    ("Business Technology", "Collaboration", "Video conferencing rooms", 3, 140, 15,
     ["Room 4B screen won't share from my laptop.", "Echo in every call from the large conference room."]),
    ("Business Technology", "Hardware", "Printing and scanning", 3, 95, 10,
     ["Badge-release printer on floor 3 says offline.", "Scan-to-email sends a blank attachment."]),
    ("Business Technology", "Access", "Internal application access", 2, 230, 20,
     ["I moved teams and can't see my new team's queue in the case system.", "Need read access to the finance reporting app."]),
    ("Business Technology", "Mobile", "Mobile device enrollment", 2, 80, 22,
     ["Work email stopped syncing on my phone after the update.", "How do I enroll a new phone for company apps?"]),
    ("Finance", "Expenses", "Expense reports and receipts", 2, 240, 16,
     ["My receipt upload keeps failing even though the file is a PDF.", "Expense report was returned with no reason given."]),
    ("Finance", "Travel", "Corporate travel policy", 3, 150, 12,
     ["Can I book a hotel above the city rate if the event venue is full?", "Is a rideshare to the airport reimbursable?"]),
    ("Finance", "Travel", "Per diem rules", 3, 90, 10,
     ["What is the meal per diem for a two-day trip to Chicago?", "Do I claim per diem if I stay with friends?"]),
    ("Finance", "Cards", "Corporate card disputes", 1, 70, 35,
     ["There's a charge on my corporate card I don't recognize.", "My card was declined at a vendor we use every month."]),
    ("Finance", "Payables", "Vendor invoices and payments", 2, 120, 28,
     ["A vendor says our payment is 30 days late. Where is it in the process?", "Invoice was entered twice; how do I stop the duplicate?"]),
    ("Finance", "Procurement", "Purchase requests", 3, 110, 14,
     ["What approvals do I need for a $4,000 software purchase?", "Purchase request is stuck with an approver who left."]),
    ("People", "Benefits", "Benefits enrollment", 1, 180, 30,
     ["My enrollment shows pending and the deadline is Friday.", "How do I add a dependent mid-year?"]),
    ("People", "Payroll", "Payroll and pay statements", 1, 160, 25,
     ["My last pay statement is missing overtime hours.", "Where do I update my tax withholding?"]),
    ("People", "Leave", "Leave and time-off policies", 1, 130, 20,
     ["How much parental leave am I eligible for?", "Can I carry over unused vacation into next year?"]),
    ("People", "Onboarding", "New hire onboarding checklist", 3, 115, 15,
     ["What do I need to finish in my first week?", "My manager hasn't received my onboarding tasks."]),
    ("People", "Performance", "Performance review cycle", 3, 85, 12,
     ["When does self-assessment close this cycle?", "How do I request feedback from a peer outside my team?"]),
    ("People", "Learning", "Learning platform", 3, 60, 8,
     ["Mandatory training shows incomplete even though I finished it.", "How do I enroll in the leadership course?"]),
    ("Legal", "Contracts", "Contract request intake", 2, 140, 30,
     ["Which form do I use to request a new client contract?", "How long does legal review take for a renewal?"]),
    ("Legal", "Contracts", "NDA templates", 2, 105, 10,
     ["Where is the mutual NDA template?", "Can I sign an NDA on the vendor's paper?"]),
    ("Legal", "Privacy", "Data privacy requests", 1, 55, 45,
     ["A customer asked us to delete their data. What's the process?", "Do we have a data processing agreement with this vendor?"]),
    ("Legal", "Compliance", "Legal hold", 1, 25, 40,
     ["I received a legal hold notice. What can't I delete?", "Does a legal hold apply to my chat messages?"]),
    ("Legal", "Contracts", "Signature authority", 2, 45, 15,
     ["Who can sign a contract over $250K?", "Can my director sign this order form?"]),
    ("Facilities", "Workplace", "Desk and room booking", 3, 95, 8,
     ["The desk booking map shows my floor as closed.", "How do I book a room for a 30-person session?"]),
    ("Facilities", "Access", "Office badges and building access", 2, 75, 15,
     ["My badge stopped working at the garage entrance.", "Visitor badges for a client meeting tomorrow?"]),
    ("Facilities", "Workplace", "Parking and commuting", 3, 50, 8,
     ["How do I get a parking permit?", "Is there a transit benefit?"]),
    ("Facilities", "Workplace", "Mail and shipping", 3, 40, 10,
     ["How do I ship equipment back to the office?", "Where do packages for remote staff get logged?"]),
    ("Sales Operations", "CRM", "CRM opportunity access", 2, 190, 18,
     ["I can't edit an opportunity my team owns.", "Need access to the partner accounts view."]),
    ("Sales Operations", "Quoting", "Quote generation", 2, 165, 22,
     ["Quote won't generate the order form; status is Customer Ready.", "Discount approval isn't routing to my manager."]),
    ("Sales Operations", "Compensation", "Commission questions", 1, 85, 30,
     ["My commission statement doesn't include a deal that closed last month.", "How are split deals credited?"]),
    ("Security", "Threats", "Phishing reporting", 2, 120, 10,
     ["I clicked a link in a suspicious email. What now?", "Got an email from the CEO asking for gift cards."]),
    ("Security", "Data", "Data classification", 2, 60, 15,
     ["Is customer usage data confidential or internal?", "Can I share this spreadsheet with a contractor?"]),
    ("Security", "Training", "Security awareness training", 3, 45, 6,
     ["My security training is overdue but the link doesn't load.", "How often is security training required?"]),
]

# rollout maturity by department (how far each team has moved)
MATURITY = {"Business Technology": 0.95, "Security": 0.7, "Facilities": 0.6, "Sales Operations": 0.45,
            "Finance": 0.3, "People": 0.25, "Legal": 0.15}
STATUS_ORDER = ["Not started", "Drafting", "In review", "Live"]
DEFLECT = {1: 0.15, 2: 0.30, 3: 0.45}  # share of tickets the assistant can resolve once a topic is live

topics, evidence, controls = [], [], []
for i, (dept, cat, name, tier, tix, aht, examples) in enumerate(T, start=1):
    m = MATURITY[dept]
    has_curator = random.random() < (0.35 + 0.6 * m)
    score = m + (0.35 if has_curator else -0.25) - (0.30 if tier == 1 else 0.10 if tier == 2 else 0) + random.uniform(-0.15, 0.15)
    status = "Live" if score > 0.75 else "In review" if score > 0.45 else "Drafting" if score > 0.2 else "Not started"
    if tier == 1 and status == "Live" and random.random() < 0.6:
        status = "In review"
    req = {1: ["PII review", "Legal approval", "Escalation path", "Answer-accuracy test"],
           2: ["Escalation path", "Answer-accuracy test", "Access-control check"],
           3: ["Answer-accuracy test"]}[tier]
    done_ct = len(req) if status == "Live" else {"In review": len(req) - 1, "Drafting": max(0, len(req) - 2), "Not started": 0}[status]
    for j, c in enumerate(req):
        controls.append({"topic_id": f"KB-{i:03d}", "control": c, "status": "Complete" if j < done_ct else "Open"})
    live_since = ""
    if status == "Live":
        live_since = (LAUNCH + timedelta(days=int(random.uniform(0, 120) * (1.2 - m)))).isoformat()
    topics.append({
        "topic_id": f"KB-{i:03d}", "department": dept, "category": cat, "topic": name, "risk_tier": tier,
        "curator": random.choice(CURATORS) if has_curator else "", "status": status, "live_since": live_since,
        "tickets_90d": tix, "avg_handle_min": aht, "deflection_rate": DEFLECT[tier],
        "controls_required": len(req), "controls_complete": done_ct,
    })
    for e in examples:
        evidence.append({"topic_id": f"KB-{i:03d}", "department": dept, "ticket_excerpt": e})

# ---- weekly adoption since launch ----
adoption = []
weeks = []
d = LAUNCH
while d <= AS_OF:
    weeks.append(d)
    d += timedelta(days=7)
CULTURE = {"Business Technology": 1.0, "Security": 0.9, "Facilities": 0.8, "Sales Operations": 1.15,
           "Finance": 1.3, "People": 0.9, "Legal": 0.75}  # appetite for self-service varies by team
for dept, hc in DEPARTMENTS.items():
    dept_topics = [t for t in topics if t["department"] == dept]
    for wi, wk in enumerate(weeks):
        live_share = sum(1 for t in dept_topics if t["status"] == "Live" and t["live_since"] and date.fromisoformat(t["live_since"]) <= wk) / len(dept_topics)
        ramp = min(1.0, (wi + 1) / 10)
        active_rate = min(0.92, (0.10 + 0.70 * live_share) * CULTURE[dept] * ramp * random.uniform(0.92, 1.06))
        active = int(hc * active_rate)
        queries = int(active * random.uniform(2.6, 3.6))
        answer_rate = min(0.9, 0.38 + 0.5 * live_share + random.uniform(-0.03, 0.03))
        resolved = int(queries * answer_rate)
        adoption.append({
            "week_start": wk.isoformat(), "department": dept, "headcount": hc, "active_users": active,
            "queries": queries, "resolved_by_assistant": resolved, "escalated_to_ticket": queries - resolved,
            "helpful_votes": int(resolved * random.uniform(0.74, 0.88)), "total_votes": int(resolved * 0.9) or 1,
        })


def write(name, rows):
    with open(HERE / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


write("topics.csv", topics)
write("evidence.csv", evidence)
write("adoption.csv", adoption)
write("controls.csv", controls)
(HERE.parent / "docs" / "data.json").write_text(json.dumps({
    "company": "Wazobia Corp (fictional)", "assistant": "Ask Wazobia", "as_of": AS_OF.isoformat(),
    "launch": LAUNCH.isoformat(), "topics": topics, "evidence": evidence, "adoption": adoption, "controls": controls,
}, separators=(",", ":")))
from collections import Counter
print(len(topics), "topics", Counter(t["status"] for t in topics), len(evidence), "evidence", len(adoption), "adoption rows")
