# BrightPay Cloud — Bureau Positioning & Commercial Growth Intelligence

**Deep Reference Document · April 2026 · Bright Software Group · Internal use only**

This document covers: (1) how BrightPay Cloud is engineered to operate at bureau scale across hundreds of employers and tens of thousands of employees; (2) the full self-service and employee value stack; (3) the payments infrastructure and what it means operationally; (4) the Employment Verification capability and its commercial significance; and (5) the complete commercial model for how BrightPay Cloud enables bureaus to win new clients, retain existing ones, and grow revenue without a direct cost correlation.

---

## Contents

- [Section A — Engineered for Bureau Scale](#section-a--engineered-for-bureau-scale)
- [Section B — The Self-Service Ecosystem](#section-b--the-self-service-ecosystem)
- [Section C — Payments Infrastructure](#section-c--payments-infrastructure)
- [Section D — Employment Verification](#section-d--employment-verification)
- [Section E — The Bureau Commercial Growth Model](#section-e--the-bureau-commercial-growth-model)

---

## Section A — Engineered for Bureau Scale

### A.1 What Bureau Scale Actually Means

Most payroll software is built around a single employer. The interface, the workflow, the data model — all optimised for one company, one payroll run, one set of employees. That is fine for a business running its own payroll. It is structurally inadequate for a bureau running 200 employers across 15,000 employees with a team of eight payroll professionals.

Bureau scale is a qualitatively different problem. It is not "one employer, bigger". It is:

- **Simultaneous** — multiple team members working on different employers at the same moment, with no file locking, no queuing, no version conflicts.
- **Asynchronous** — clients submitting payroll data on their own timelines, bureaus processing on their own schedules, employees accessing payslips independently, all without the bureau acting as an intermediary in every step.
- **Heterogeneous** — dozens of different payroll frequencies, industries, statutory situations, pension providers, accounting systems, and pay structures within a single bureau's portfolio.
- **Compliance-critical at every point** — a single error does not affect one company's employees; it potentially affects hundreds across multiple clients.
- **Time-compressed** — weekly, fortnightly, and monthly payroll deadlines overlap throughout the month, creating a near-continuous processing workload.

> **The question BrightPay Cloud answers is not "can you process a payroll?" — every platform can. The question is: can you process 250 payrolls, for 18,000 employees, across a team of 10, without the platform becoming the bottleneck?**

---

### A.2 The Bureau Architecture: How BrightPay Cloud Is Engineered for Scale

#### Unlimited Employers. Unlimited Users. No Artificial Ceilings.

BrightPay Cloud places no cap on the number of employers or users within a bureau subscription. The platform accommodates the full range of bureau sizes — from 10 clients to 500+ — within a single organisational account. Pricing is tied to actual usage (employer and employee count), not to user seats. A bureau can provision every payroll professional, every team lead, every client approver, and every manager without incurring per-user charges.

#### Real-Time Multi-User Collaboration on the Same Employer

The desktop product locked an employer file to a single user. If two payroll professionals needed to work on the same employer simultaneously — during a busy payroll run, during onboarding, during year-end — one had to wait. BrightPay Cloud eliminates this constraint entirely. Multiple users can work on the same employer at the same time, with changes visible in real time to all users. The platform shows who is doing what, preventing overwrites and enabling genuine parallel processing.

For a bureau running a large employer with 200+ employees, this is not a nice-to-have. It is the difference between a team being able to split and process a payroll run in hours versus a sequential queue that takes days.

#### Batch Processing Across the Portfolio

BrightPay Cloud's batch processing tools operate at the bureau level — not the individual employer level. A payroll professional can:

- Finalise open pay periods across multiple employers in a single operation.
- Batch-send outstanding RTI and CIS submissions across the entire client portfolio simultaneously.
- Batch-check for new HMRC coding notices across all employers at once.
- Batch-process payroll entry and approval requests from multiple clients in sequence.
- Apply pay changes, deductions, or notes to multiple employees across multiple employers without opening each employer individually.

Tasks that previously required opening each employer in turn — a process that scales linearly with client count — become parallelised, portfolio-wide operations.

#### Bureau Statistics and Portfolio Intelligence

The Bureau Statistics Report gives a real-time view across the entire portfolio: which employers have outstanding pay periods, which have pending RTI submissions, which have incomplete auto-enrolment assessments, and which have upcoming payroll deadlines. This is the bureau's operational dashboard — the single-pane view that tells a bureau manager where attention is needed before deadlines are missed.

#### Granular Permission Architecture

BrightPay Cloud's permission model allows bureau administrators to define exactly what each team member can see and do:

- **Role-based access:** define permissions at the organisation level, then assign by team member.
- **Employer-level access controls:** restrict specific team members to specific employers — relevant where client confidentiality or team specialisation requires separation.
- **Client portal access:** grant clients access to their own employer data without exposing the bureau's wider portfolio or other clients.
- **Approval hierarchies:** define who can finalise a payroll, who can submit RTI, and who can approve payments — creating a clear, auditable governance structure.

#### The Audit Trail — Accountability at Scale

Every action taken within BrightPay Cloud is logged: who made the change, what they changed, and when. The audit trail is immutable and exportable, providing the evidence base for any client query, HMRC enquiry, or internal review.

> **A bureau's professional reputation rests on accuracy and accountability. The audit trail is not just a compliance tool — it is a client confidence tool. When a client asks "who approved that payroll?" or "when was that change made?", BrightPay Cloud answers instantly and without ambiguity.**

---

## Section B — The Self-Service Ecosystem

### B.1 The Inbound Burden Problem

The most persistent margin drain in a payroll bureau is not the payroll run itself — it is everything around it. The queries. The requests. The chasing. The manual tasks that exist because information is trapped inside the bureau's system rather than being accessible to the people who need it.

| Statistic | Source |
|-----------|--------|
| 76% of payroll professionals still need up to a week to complete a pay run — the majority of that time is non-processing admin | Employment Hero, 2025 |
| ~2/3 of UK SME employees have never had self-service access to their own payslips or leave records | Market data, 2025 |

Every time a client emails to ask about an employee's year-to-date figures, every time an employee calls the bureau directly because they cannot access their payslip, every time a leave request is handled by email and manually reconciled at month end — that is time the bureau cannot spend processing payroll. At scale, this is the growth constraint. Bureaus do not fail to grow because they cannot process payroll. They fail to grow because the administrative overhead of managing client and employee communication scales with client count, and headcount scales with it.

BrightPay Cloud's self-service architecture is built to break this correlation. The goal is not to add a nice-to-have employee app. It is to systematically remove the bureau from every interaction that does not require payroll expertise.

---

### B.2 Three Portals — Three Distinct Audiences, One Platform

#### Portal 1: The Bureau Dashboard — Command and Control

The bureau dashboard is the operational hub for the payroll team. From a single login, the bureau sees its entire portfolio: all employers, all active pay periods, all outstanding submissions, all pending approvals, all client requests. The dashboard surfaces what needs attention today — not what was processed last week.

Bureau team members see their assigned employers, their submission status, and any client or employee actions awaiting response. Bureau managers see the portfolio-wide view. Both work in real time.

---

#### Portal 2: The Client (Employer) Portal — The Bureau's Interface with Its Customers

The client portal gives each employer direct access to their own payroll data without requiring the bureau to act as an intermediary for every query. The client can:

- View payroll summaries and historical payroll data for their employees.
- Access all employee records, including contact details, payslip history, and leave entitlements.
- Manage the employee self-service portal — activating employee access, reviewing employee requests.
- Submit payroll entry requests directly to the bureau — entering hours, additions, deductions, and new starter information through the portal rather than by email or spreadsheet.
- Review and approve payroll runs before the bureau finalises them — the payroll approval workflow.
- Access the employer calendar for a real-time view of leave across their workforce.
- Access HMRC payment information and outstanding amounts directly.
- Download or review shared documents uploaded by the bureau.

> **The client portal transforms the bureau's client relationship from reactive (the bureau answers queries) to proactive (the client finds what they need themselves). Bureaus that offer this capability differentiate themselves immediately from those that do not.**

---

#### Portal 3: The Employee Self-Service Portal — The Bureau's Gift to Its Clients' Workforce

The employee portal is the most visible element of BrightPay Cloud to the people who ultimately determine a payroll bureau's reputation with its clients: the employees themselves. Every employee at every client organisation gets secure, individual access to:

**Payslip and Document Access**

- Complete payslip history — every payslip, from onboarding to present, accessible from any device at any time.
- P60 access — year-end documents available the moment they are published, without printing, posting, or emailing.
- P11D access — benefits-in-kind documentation, where applicable.
- Documents shared by the employer — contracts of employment, company handbook, HR policies, team communications, training materials. Uploaded once by the bureau or employer, accessible to the right individuals permanently.

**Leave and Absence Management — Full Lifecycle**

This is substantively more than a holiday request form. BrightPay Cloud's leave management is a full absence management system:

- Leave requests submitted by the employee through the portal — annual leave, sick leave, parenting leave, and unpaid leave.
- Leave approval workflow: requests flow to the employer portal for approval or rejection — with the bureau never acting as the intermediary unless they choose to.
- Real-time leave balance display — employees see their remaining entitlement before they submit a request.
- Complete leave history — employees see all past and approved future leave in a personal calendar view.
- Company-wide leave calendar — employers see all approved leave across their workforce simultaneously, enabling resource planning.
- **Automatic payroll synchronisation** — approved leave flows directly into the payroll calculation. Sick leave, unpaid leave, and partial-pay absences are reflected in the next payslip without manual intervention by the bureau.

The operational significance for the bureau is profound. Leave management is traditionally one of the highest-volume sources of manual contact between bureau, client, and employee. By routing the entire lifecycle — request, approval, payroll impact — through the platform, BrightPay Cloud removes it entirely from the bureau's inbox.

**Personal Details Management**

- Employees update their own personal details (address, bank account, emergency contact) through the portal.
- Changes are submitted as requests — the employer or bureau reviews and approves before they take effect in the payroll system.
- Eliminates the constant flow of "can you update my bank details" emails that every bureau receives.

**Mobile Access**

The employee portal is fully mobile-accessible — employees access it on any device through a browser or the BrightPay employee app. For employees who never sit at a desk — hospitality, retail, construction, healthcare — mobile access to payslips and leave management is the baseline expectation.

---

### B.3 The Commercial Significance of Self-Service for Bureaus

Self-service is how bureaus grow revenue without growing headcount. The arithmetic is straightforward:

| Activity | Without Self-Service | With BrightPay Cloud Self-Service |
|----------|---------------------|----------------------------------|
| Payslip query from employee | Bureau receives call/email, locates record, responds — 10–15 minutes per query | Employee accesses directly — bureau involvement: zero |
| Leave request | Employee contacts employer, employer contacts bureau, bureau updates, bureau confirms — multiple touchpoints | Employee submits in portal, employer approves in portal, payroll updates automatically — bureau involvement: zero |
| Annual P60 distribution | Bureau prints, posts, or emails individually — high volume, error-prone | Published to all employees simultaneously via portal — bureau involvement: one click |
| New starter document pack | Bureau or employer emails individually | Uploaded once, available immediately to all new starters — bureau involvement: one upload |
| Bank detail update | Employee emails bureau or employer, bureau updates manually | Employee submits change request, employer approves, bureau confirms — audit trail maintained |
| Year-to-date pay query | Bureau retrieves data, responds to client | Client accesses directly via employer portal — bureau involvement: zero |

The cumulative effect of removing these touchpoints from a bureau with 150 clients and 3,000 employees is significant. Conservative modelling suggests bureaus operating at this scale could recover 15–25 hours of payroll team time per month — equivalent to a material portion of one FTE — purely from self-service automation of inbound administration.

> **The growth model becomes: add more clients using existing capacity, rather than add capacity to serve existing clients. Self-service is the mechanism that makes this possible.**

---

## Section C — Payments Infrastructure

### C.1 The Traditional Payroll Payment Problem

Traditional payroll has always had a structural inefficiency at the point of disbursement. The payroll is calculated. The payroll is approved. And then — the payroll professional creates a BACS file, exports it, logs into the bank, uploads the file, waits for bank processing (typically 2–3 business days), and hopes nothing went wrong in the transfer.

For bureaus, this creates three distinct problems:

- **Timing risk:** the 2–3 day BACS window means payroll must be run significantly ahead of pay day. Any late submission from a client pushes the payroll professional into an emergency CHAPS payment — expensive, manual, and stressful.
- **Error risk:** the bank file export-and-upload process introduces a manual step where errors can occur. File corruption, incorrect account details, mismatched payment amounts — these are the errors that damage client relationships and create compliance exposure.
- **Operational overhead:** for a bureau processing 100+ payrolls per month, the bank file management process is a meaningful time cost. Each payroll requires a separate file creation, upload, and verification cycle.

---

### C.2 The Modulr Integration — Payments Inside Payroll

BrightPay Cloud's integration with Modulr eliminates the gap between payroll calculation and payment execution. Modulr is an FCA-regulated Electronic Money Institution, a direct participant in the Faster Payments and BACS schemes, and holds funds at the Bank of England. It is not a third-party payment processor bolted onto the side of payroll. It is a payments infrastructure provider embedded directly into the payroll workflow.

#### How It Works

When a bureau processes a payroll run in BrightPay Cloud, rather than exporting a bank file and uploading it to a bank portal, the bureau selects 'Pay by Modulr'. The payroll calculations synchronise directly into Modulr payment entries — employee names, amounts, bank account details, all pulled from the payroll record. No re-entry. No export. No upload. The bureau reviews the payment batch and approves it. That is the complete process.

#### The Payment Timeline

| Metric | Detail |
|--------|--------|
| **90 seconds** | Payments processed within 90 seconds of approval — not 2–3 working days |
| **24/7, 365** | Available every day of the year — including bank holidays and weekends |
| **Same-day** | Submitted before 2:00 pm = employees paid the same day |

#### What This Means for the Bureau

- The BACS file process is eliminated — no bank portal logins, no file uploads, no 3-day payment window to manage around.
- Late client submissions can be absorbed — if a client submits their payroll data late, the bureau can process and pay on the same day rather than issuing an emergency CHAPS payment.
- Emergency payments become routine — one-off corrections, interim payments, and bonus payments are handled inside the payroll workflow without breaking the process.
- Client confidence increases — employees are paid faster, and clients can see payment status within the platform rather than chasing the bureau for confirmation.
- Security improves — encrypted communication between BrightPay and Modulr; no insecure bank file transfers; approval controls within the platform.

#### Modulr for Bureau Clients: A Deployable Value-Add

The Modulr integration is not just an operational efficiency for the bureau — it is a capability the bureau can deploy for its clients. Bureaus can enable Modulr payments for individual clients, giving those clients the ability to approve and execute payroll payments directly from their employer portal.

> **A bureau that offers same-day payment capability to its clients is offering something most competitors cannot. For clients in time-sensitive sectors — hospitality, healthcare, retail — this is not a feature. It is a requirement that the bureau can now meet.**

---

### C.3 Open Banking — The Next Step (Coming)

BrightPay Cloud's payments roadmap includes Open Banking integration — enabling direct account-to-account payment initiation without a separate Modulr account or intermediary. When live, this will allow bureaus to initiate payroll payments directly from their clients' business bank accounts through the BrightPay Cloud interface, using the bank's own payment rails and the client's own funds, without an intermediate e-money account.

Open Banking removes the requirement for bureaus or clients to maintain a funded Modulr account as a holding step. For bureaus whose clients are reluctant to pre-fund a payment account, Open Banking will provide an equally fast, direct-to-bank payment route — further compressing the gap between payroll calculation and employee payment.

---

## Section D — Employment Verification

### D.1 The Problem This Solves

Every year, millions of UK employees need to prove their income and employment status — for mortgages, rental reference checks, credit applications, visas, and professional accreditations. The traditional process:

1. Employee contacts their employer (or payroll bureau) to request an employment reference letter.
2. Employer (or bureau) locates the relevant employee record, compiles the required information, formats the letter, obtains authorisation, and sends it — a process that typically takes days.
3. The receiving organisation may not accept the letter format, may require additional verification, or may need to confirm directly with the employer.

For the bureau, this is a hidden but significant administrative burden. A bureau with 3,000 employees across its client base might handle dozens of these requests per month. Each one is an unplanned interruption that consumes time without generating any revenue.

For the employee, it is a source of anxiety — a delay in an employment reference can hold up a mortgage completion, delay a tenancy start, or slow a visa application.

---

### D.2 The BrightPay Cloud Employment Verification Capability

BrightPay Cloud has integrated directly with both **Experian** and **Equifax** — the UK's two leading credit reference and data verification agencies — to provide instant, digital employment and income verification for employees on payrolls processed through BrightPay.

#### How It Works — From the Employee's Perspective

1. The employee commences a mortgage application, tenancy agreement, credit application, or other process requiring income or employment verification.
2. The lender, landlord, or verifying organisation requests proof of income and employment status.
3. The employee consents to digital verification through the Experian or Equifax platform.
4. The verification platform queries BrightPay Cloud in real time — drawing on the payroll data that already exists in the system.
5. Income and employment status are confirmed instantly — salary, employment status, employer name, and tenure — without any action required from the employee, the employer, or the bureau.

#### How It Works — From the Bureau's Perspective

Employers are automatically opted in by default. The bureau does not need to handle individual verification requests. There is no document to produce, no letter to write, no record to locate. The verification happens entirely between the employee, the verification platform, and BrightPay Cloud's data. The bureau's involvement is zero for each individual transaction.

> **The bureau processes payroll. The verification infrastructure handles the rest. The employee gets instant confirmation. The bureau never has to field the request.**

---

### D.3 The Commercial Significance

#### It Makes the Bureau's Platform Directly Valuable to Employees

Most payroll bureau capabilities are visible to the employer — the client. Employment Verification is one of very few capabilities that is directly, tangibly valuable to individual employees. An employee at a client company does not typically know or care which payroll bureau their employer uses. But when that employee needs to verify income for a mortgage application and the process takes seconds rather than days, they notice. They tell their employer. The employer — the bureau's client — associates that positive experience with their payroll provider.

This is a qualitatively different value dynamic. The bureau is not just efficient for the employer. The bureau's platform makes the employer look good to their own employees. That is a retention driver with a very different gravity than software capability alone.

#### It Is a Client Acquisition Differentiator

When a bureau is competing for a new client, the conversation is typically about price, compliance, and service quality. Employment Verification adds a dimension most competitors cannot offer:

> *"Every employee at your company gets instant digital employment verification for mortgages, tenancy agreements, and credit applications — no letters, no delays, no admin for your HR team. That is included in your bureau service."*

For an HR manager or finance director evaluating payroll bureaus, this is a concrete, tangible benefit that reaches every employee in the company. It is not a feature on a comparison table. It is something they can explain to their CEO and their employees.

#### It Supports Upmarket Positioning

One of the structural challenges facing payroll bureaus is commoditisation. When every bureau processes the same statutory calculations, submits the same RTI filings, and manages the same pension auto-enrolment, the differentiation becomes price. Employment Verification is one of several capabilities in BrightPay Cloud that moves the bureau's value proposition beyond payroll processing and into an HR services model.

Bureaus that can credibly position themselves as providers of payroll, employee self-service, payments, and financial wellbeing infrastructure — rather than payroll processors with a portal — command higher fees, attract more sophisticated clients, and are structurally harder to displace.

---

### D.4 Why Both Experian and Equifax Matter

Different lenders, landlords, and verification platforms use different agency data. A mortgage lender might use Experian's verification infrastructure; a rental reference agency might use Equifax. By connecting to both, BrightPay Cloud ensures that an employee's income and employment data is accessible across the widest possible range of financial applications — regardless of which agency the verifying organisation uses.

For the bureau, this means the Employment Verification benefit is universal across the client base — not dependent on which verification infrastructure a specific client's employees happen to encounter.

---

## Section E — The Bureau Commercial Growth Model

### E.1 The Core Commercial Thesis

The traditional bureau growth constraint is a direct cost correlation: more clients requires more payroll professionals, which increases headcount costs, which compresses margin, which limits the bureau's ability to price competitively or invest in growth. BrightPay Cloud breaks this correlation in five distinct ways.

> **The platform's self-service architecture, payment integration, and employment verification capability are not feature additions. They are mechanisms that decouple revenue growth from cost growth — which is the fundamental condition for a scalable bureau business.**

---

### E.2 Five Commercial Growth Mechanisms

#### Mechanism 1 — Capacity Expansion Without Headcount

Self-service eliminates inbound administration. Batch processing compresses payroll run time. Real-time collaboration removes sequential bottlenecks. The combined effect is that each payroll professional can service more clients without working more hours. A bureau that previously needed one FTE per 30 clients can, with full BrightPay Cloud adoption, potentially move that ratio to 40–50 clients per FTE.

This is the direct mechanism for growing revenue without a direct cost correlation. Every additional client taken on above the old capacity threshold is essentially pure margin — no new hire required, no new software licence cost, and no increase in operational overhead beyond the incremental payroll run.

---

#### Mechanism 2 — Premium Positioning Through Client Experience

BrightPay Cloud enables bureaus to deliver a client experience that legacy platforms cannot match. The client approval portal, the employee self-service portal, instant P60 distribution, and same-day payment capability combine to give the bureau's clients — and their employees — a service that feels like an enterprise HR platform, not a payroll outsourcing arrangement.

This creates pricing power. Bureaus using BrightPay Cloud can legitimately charge more than a bureau offering a spreadsheet-and-email service, because the value they deliver is demonstrably greater.

| Service Element | Legacy Bureau Offer | BrightPay Cloud Bureau Offer |
|----------------|---------------------|------------------------------|
| Payslip access | Emailed PDF on pay day | 24/7 portal access, full history, mobile, any device |
| P60 distribution | Posted or emailed in April | Published instantly on the portal — zero admin |
| Leave management | Email to HR/bureau, manual update | Employee requests in portal, employer approves, payroll updates automatically |
| Employment verification | Bureau writes letter on request — days of delay | Instant digital verification via Experian and Equifax — zero bureau involvement |
| Payroll approval | Email sign-off from client contact | Structured approval workflow with audit trail in the platform |
| Payment execution | BACS file, 2–3 day payment window | Same-day Faster Payments via Modulr |
| Document distribution | Email attachments, no version control | Secure portal — accessible permanently, to the right individuals |

---

#### Mechanism 3 — Client Retention Through Dependency

A client using a bureau whose only interface is a monthly email with a BACS file can switch provider with minimal disruption — all they are moving is a calculation service. A client using a bureau where their employees log into a portal daily, where their payroll approval happens in a workflow, where their employment references are handled automatically, and where their payments execute in real time — that client faces a meaningful switching cost. The platform is embedded in the client's operations.

This is not lock-in through artificial barriers. It is retention through genuine value. The bureau's churn rate improves, which improves lifetime value per client, which improves the economics of client acquisition.

---

#### Mechanism 4 — New Client Acquisition Through Differentiation

When a bureau pitches for a new client, BrightPay Cloud provides a differentiated narrative that most competitors cannot match. The conversation shifts from "we process payroll accurately and reliably" to:

- Your employees get instant access to their payslips, P60s, and leave management from their phone.
- Your payroll is approved through a structured portal before it is finalised — with a full audit trail.
- Your staff get instant employment verification for mortgages and tenancy applications — no letters, no delays.
- Your employees are paid the same day payroll is approved — not 2–3 days later.
- Your HR team never has to field a "where is my payslip" query again.

This is a pitch about the client's employees' experience, not just the bureau's processing capability. An HR director or MD evaluating bureaus responds to this differently. It addresses concerns they have with their current provider that they may not have articulated as a payroll problem — because they have never been offered a payroll bureau that solves it.

---

#### Mechanism 5 — Revenue Expansion Within the Existing Client Base

BrightPay Cloud's capabilities create natural upsell opportunities within the existing bureau client base:

- Bureaus offering Modulr payment services can charge for payment execution as a separate service line — or bundle it into a premium tier.
- Bureaus offering Employment Verification can position this as an HR services capability, supporting a fee uplift on clients who value it.
- Bureaus offering full leave management can extend into HR advisory services — a natural adjacency to payroll.
- Bureaus with deep accounting software integration can offer accounting reconciliation services alongside payroll.

The platform is the infrastructure for a broader service model. The bureau that treats BrightPay Cloud purely as payroll processing software is leaving revenue on the table.

---

### E.3 The Bureau Positioning Statement

> **BrightPay Cloud is not payroll software that bureaus use. It is the platform on which bureaus build a scalable, differentiated, client-retaining, employee-valued payroll service. The distinction matters — because it changes what you sell, how you price it, and how hard it is for a client to leave.**

---

### E.4 Messaging Framework — Bureau Sales Conversations

#### When Competing Against a Legacy Bureau

Lead with the employee experience — not the bureau's internal efficiency. The prospect's employees are currently being under-served. Their payslips arrive by email. Their leave requests go to HR by email. Their employment references take days. Their payroll lands 3 days after it's approved. BrightPay Cloud solves all of this, and the bureau delivers it all as part of the service.

#### When Competing Against a Tech-Forward Bureau

Lead with breadth and integration depth. BrightPay Cloud combines scale architecture (unlimited employers, real-time collaboration, batch processing), self-service (full leave management, document management, mobile payslips), payments (Modulr Faster Payments, Open Banking incoming), employment verification (Experian and Equifax), and accounting integration (Xero, Sage, QuickBooks, FreeAgent) in a single platform with a single pricing model.

#### When a Client Is Considering In-House Payroll

Acknowledge the control argument — it is legitimate. Then quantify what they are not seeing: the compliance update overhead, the year-end pressure, the leave management administration, the employment reference handling, the payment file management. BrightPay Cloud's employee portal means their HR team still feels in control — they approve payroll, they manage leave, they communicate through the platform. The bureau handles the regulated, time-critical processing. Neither party duplicates the other's role.

---

### E.5 Proof Points — Ready for Content and Sales Use

- **90 seconds** — the Modulr payment processing time from approval to employee bank account.
- **24/7, 365** — Modulr payment availability, including bank holidays and weekends.
- **Same-day payment** — if submitted before 2:00 pm, employees are paid on the same day payroll is approved.
- **Instant verification** — Experian and Equifax employment verification confirmed in real time during the application process, with zero bureau or employer action required.
- **Both major UK agencies** — Experian and Equifax integration ensures verification works across the widest possible range of lending, tenancy, and professional verification processes.
- **Zero bureau involvement per verification** — employment references are handled automatically, permanently removing an unplanned administrative workload.
- **Full leave lifecycle** — request, approval, payroll integration, and calendar visibility all in one platform with no bureau intermediation.
- **Complete document management** — contracts, policies, P60s, payslips, and HR documents accessible securely from any device at any time.
- **Audit trail for every action** — who changed what, when, and whether it was approved. Immutable. Exportable.
- **Unlimited employers, unlimited users** — no per-seat pricing that creates a disincentive to provision clients or team members.

---

*BrightPay Cloud Bureau Positioning Document · Bright Software Group · April 2026 · Internal use only — not for external distribution in this form.*

*Bright Software Group · 3 Shortlands, Hammersmith, London W6 8DA · brightsg.com · Simply Brilliant Software*
