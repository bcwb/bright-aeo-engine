# Bright Software Group — Brand Guidelines

> **Simply Brilliant Software**

![Bright banner](assets/images/bright-banner.png)

---

## Company Identity

| | |
|---|---|
| **Full name** | Bright Software Group |
| **Short name** | Bright |
| **Strapline** | Simply Brilliant Software |
| **Markets** | UK and Ireland |
| **Legal footer** | © 2026 Bright. All Rights Reserved. |

**Never use:** BSG, Bright SG, BrightSG, Bright Group, or any other abbreviation.  
**Never alter** the strapline — do not translate, paraphrase, or reword it.

### About Bright (Boilerplate)

> Bright provides a suite of industry-leading software solutions for accountants and bookkeepers across the UK and Ireland. Our multi-award-winning, user-friendly and innovative products let users support clients while profitably running their practices, with the backing of exceptional support.

---

## Brand Colours

| Colour | Hex | RGB | Usage |
|--------|-----|-----|-------|
| **Navy** | `#0F2B3D` | rgb(15, 43, 61) | Primary text, headings, dark backgrounds |
| **Blue** | `#009FC7` | rgb(0, 159, 199) | Accents, CTAs, links, highlights |
| **Orange** | `#E39400` | rgb(227, 148, 0) | Secondary accents, warmth, alerts |
| **Yellow** | `#E6D600` | rgb(230, 214, 0) | Tertiary accent — use sparingly for emphasis |
| **White** | `#FFFFFF` | rgb(255, 255, 255) | Light text on dark backgrounds |

### Colour Rules

- Dark backgrounds must always use **Navy (#0F2B3D)** — never pure black (`#000000`)
- Light text on dark backgrounds must be **white (#FFFFFF)**
- All colour pairings must meet **WCAG AA minimum contrast** ratio
- Never introduce off-brand colours — only the four brand colours above

### Colour Gradient

The brand gradient runs: Navy → Blue → Orange → Yellow  
CSS: `linear-gradient(90deg, #0F2B3D 0%, #009FC7 40%, #E39400 75%, #E6D600 100%)`

![Bright gradient](assets/images/bright-gradient.png)

### Colour Swatches

![Bright colour swatches](assets/images/bright-colour-swatches.png)

---

## Logo

![Bright logo](assets/images/bright-logo.png)

### Variants

| Variant | File | Usage |
|---------|------|-------|
| Primary | `assets/images/bright-logo.png` | Navy text + coloured icon — light backgrounds |
| Reversed | `assets/images/bright-logo-reversed.png` | White text + coloured icon — dark backgrounds |
| Monochrome Navy | `assets/images/bright-logo-mono-navy.png` | All-navy — light backgrounds when colour conflicts |
| Monochrome White | `assets/images/bright-logo-mono-white.png` | All-white — dark backgrounds when colour conflicts |
| Icon only | `assets/images/bright-icon.png` | Standalone icon / favicon |

### Logo Do's

- Maintain clear space around the logo at all times
- Always maintain the original aspect ratio
- Use the correct variant for the background colour

### Logo Don'ts

- Never rotate the logo
- Never stretch or distort the logo
- Never alter or remove any elements
- Never change any colours
- Never change the strapline
- Never add a drop shadow
- Never place on a similar-coloured background (contrast must be maintained)
- Never remove the gradient from the icon

---

## Typography

### Font Stack

- **Primary:** Clean, modern sans-serif (as used on brightsg.com)
- **Document fallback:** Arial, Calibri
- **Code/mono:** Monospace fallback

### Scale

| Style | Size | Weight | Colour | Notes |
|-------|------|--------|--------|-------|
| Heading 1 | 28–32px | 700 | Navy or Blue | Page/section titles |
| Heading 2 | 22–24px | 700 | Navy or Blue | Sub-section titles |
| Heading 3 | 18–20px | 600 | Navy | Section headings |
| Body | 15–16px | 400 | Navy | Line height 1.7 |
| Caption / Label | 11–13px | 400 | Muted grey | Supporting text |

- **Headings:** Bold, Navy or Blue — never use off-brand colours for headings
- **Body text:** Navy on white or light backgrounds
- **Two weights only** in most contexts: regular (400) and bold (500–700)

![Bright typography specimen](assets/images/bright-typography.png)

---

## Imagery

### Style

- Clean, modern, and professional
- Illustration/SVG-style graphics that show product UI elements are preferred
- Photography must show real people in professional settings
- Avoid stock photography clichés

![Bright dark background](assets/images/bright-background-dark.png)

### Asset Directory Structure

```
assets/
└── images/
    ├── bright-banner.png              ← Primary brand banner (hero)
    ├── bright-logo.png                ← Primary logo (light backgrounds) — add manually
    ├── bright-logo-reversed.png       ← Reversed logo (dark backgrounds) — add manually
    ├── bright-logo-mono-navy.png      ← Monochrome navy logo — add manually
    ├── bright-logo-mono-white.png     ← Monochrome white logo — add manually
    ├── bright-icon.png                ← Standalone icon / favicon
    ├── bright-icon.svg                ← Icon (vector)
    ├── bright-colour-swatches.png     ← All four brand colour swatches
    ├── bright-colour-swatches.svg     ← Colour swatches (vector)
    ├── bright-gradient.png            ← Brand gradient strip
    ├── bright-gradient.svg            ← Brand gradient (vector)
    ├── bright-typography.png          ← Typography scale specimen
    ├── bright-typography.svg          ← Typography specimen (vector)
    ├── bright-cta-styles.png          ← Primary and secondary CTA button styles
    ├── bright-cta-styles.svg          ← CTA styles (vector)
    ├── bright-background-dark.png     ← Navy dark background with brand shapes
    └── bright-background-dark.svg     ← Dark background (vector)
```

---

## Tone of Voice

### Core Personality

Bright's voice is **confident, warm, approachable, and knowledgeable**. The brand positions itself as a trusted partner that simplifies complexity for accountants, bookkeepers, payroll bureaus, and small businesses.

### Five Principles

1. **Be brilliantly simple** — Avoid jargon where possible. When technical terms are necessary (PAYE, RTI, CIS, MTD), use them confidently but explain them for mixed audiences.

2. **Be warm and human** — Write as though speaking to a colleague, not reading from a manual. Use "you" and "your" freely. Use "we" and "our" when speaking as Bright.

3. **Be confident, not arrogant** — State benefits clearly with evidence and specifics (e.g. "the average BrightPay user saves over 63 hours a month") rather than vague superlatives.

4. **Be encouraging** — Frame features as opportunities and benefits, not just capabilities. Focus on outcomes: saving time, growing the practice, reducing stress, staying compliant.

5. **Be professional** — Whilst the tone is warm, it must always be appropriate for a B2B professional audience in accounting and payroll. Avoid slang, excessive exclamation marks, or overly casual language.

### Language Preferences

| Prefer | Avoid |
|--------|-------|
| Streamline | Simply / just |
| Automate | Easy |
| Empower | Straightforward |
| Transform | Basic |
| Unlock | Obviously |

- **British English** always — colour, specialise, recognise, programme (but "program" in software contexts)
- **Active voice** preferred over passive
- **Second person** ("you") for customer-facing content
- **Contractions** are acceptable in marketing copy (you'll, we're, it's) — avoid in formal or legal contexts

---

## Messaging Pillars

| Pillar | Key Message |
|--------|-------------|
| **Automate** | Escape repetitive tasks; supercharge productivity |
| **Win** | Unlock new opportunities; wow clients and win business |
| **Learn** | Empower decisions with analysis and insights |
| **Save** | Transform time into savings; reduce manual effort |

---

## Audience Segments

| Segment | Key Concerns | Emphasis |
|---------|-------------|----------|
| Accountants & Bookkeepers | Practice growth, efficiency, compliance, client service | Productivity, compliance, scale |
| Small & Medium Businesses | Ease of use, cost-effectiveness, compliance | Simplicity, value, reliability |
| Payroll Bureaus | Reliability, scale, accuracy, HMRC compliance | Accuracy, throughput, support |

Always identify which segment you are writing for and tailor the emphasis accordingly.

---

## Product Names

Product names follow strict CamelCase conventions. This is critical — incorrect naming undermines brand credibility.

| Correct Name | Never Write |
|---|---|
| BrightPay | Bright Pay, Brightpay, BRIGHTPAY |
| BrightPay Connect | BrightPayConnect, Bright Pay Connect |
| BrightManager | Bright Manager, BrightManagers |
| BrightPropose | Bright Propose, BrightPropose.com |
| BrightAccountsProduction | Bright AP, Bright Accounts Prod |
| BrightBooks | Bright Books, BrightBook |
| BrightTax | Bright Tax, BrighTax |
| BrightCoSec | Bright CoSec, BrightCosec |
| BrightCIS | Bright CIS, BrightCis |
| BrightChecks | Bright Checks, BrightCheck |
| BrightExpenses | Bright Expenses |
| Inform Direct | InformDirect, Inform direct |
| MyWorkpapers | My Workpapers, My Work Papers |
| TimeKeeper | Timekeeper, Time Keeper |

### Product Naming Rules

- Always CamelCase — single word (exceptions: Inform Direct, BrightPay Connect, TimeKeeper)
- Never pluralise product names
- Never use product names as verbs (e.g. not "BrightPay your staff")
- When first mentioning a product in long-form content, briefly describe what it does

### Official Product Descriptions

| Product | Description |
|---------|-------------|
| **BrightPay** | Multi-award-winning payroll software that makes managing your payroll quick and easy. Available on both Windows and in the cloud. |
| **BrightPay Connect** | The cloud extension for the desktop version of BrightPay. Enables automatic cloud backups, HR management tools, employer and bureau dashboards, and an employee app. |
| **BrightManager** | Multi-award-winning, cloud-based practice management software. The fully customisable solution enables you to automate your admin and onboard clients with ease. |
| **BrightPropose** | Pricing and proposal software that takes the guesswork out of fee setting and gives you the ability to create branded proposal documents in minutes. |
| **BrightAccountsProduction** | Intuitive and fully compliant accounts production software. |
| **BrightBooks** | Smooth online invoicing and payments platform. |
| **BrightTax** | A suite of cloud-based tax and accounting solutions that ensure accuracy, efficiency, and compliance with tax regulations for both businesses and individuals. |
| **BrightCoSec** | Cloud company secretarial solution which helps you manage corporate governance with ease. |
| **Inform Direct** | The most efficient company secretarial solution, seamlessly synced with Companies House. |

---

## Calls to Action

| Type | Examples |
|------|---------|
| **Primary CTAs** | Book a Demo · Get Started · Find Out More |
| **Secondary CTAs** | Learn More · Download Now · Sign Up Today |

- Always action-oriented
- Always Title Case
- Primary CTAs: Blue (`#009FC7`) background with white text
- Secondary CTAs: Blue outline with Blue text on transparent background

![Bright CTA styles](assets/images/bright-cta-styles.png)

---

## Content Templates

### Email Subject Lines

- Keep under 50 characters where possible
- Lead with benefit or action
- Examples: `Save 63 hours a month on payroll` · `Your practice management upgrade awaits`

### Social Media

- Handle: `@BrightUKIre` (X/Twitter)
- Hashtags: `#BrightSoftware` `#SimplyBrilliant` `#Payroll` `#Accounting`
- Tone may be slightly more informal but must remain professional

---

## Markets & Compliance Context

- Bright operates in the **UK and Ireland** markets
- Key regulatory frameworks: HMRC, Companies House, Revenue (Ireland), Making Tax Digital (MTD), Auto-Enrolment, CIS
- Always specify which jurisdiction content relates to when relevant
- The website has separate UK and Ireland sections — ensure content is appropriate for the target market

---

## Pre-Publication Checklist

Before finalising any content, confirm all of the following:

- [ ] Product names are correctly capitalised (CamelCase, no spaces)
- [ ] British English spelling used throughout
- [ ] Tone is warm, confident, and professional
- [ ] Brand colours used correctly — no off-brand colours
- [ ] Strapline is unchanged if included
- [ ] Target audience segment is clearly identified
- [ ] Messaging is benefits-led (outcomes, not features alone)
- [ ] Logo usage follows all guidelines
- [ ] CTA is action-oriented and Title Case
- [ ] UK/Ireland jurisdiction is specified where relevant

---

*© 2026 Bright. All Rights Reserved. — Simply Brilliant Software*