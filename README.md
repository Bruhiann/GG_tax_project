# AI Tax Return Agent Prototype

An AI-powered tax return preparation agent that automates basic federal income tax calculations for the 2024 tax year.

## Features

- **Tax Input Form** — Collects income, filing status, deductions, and withholdings with client-side validation
- **Tax Calculation Engine** — Progressive bracket calculations using 2024 IRS federal tax rates for all four filing statuses
- **Results Dashboard** — Detailed breakdown with bracket-by-bracket visualization and effective/marginal rate display
- **PDF Tax Return** — Generates a downloadable simplified Form 1040-style document with all calculated fields
- **AI Chat Assistant** — Optional Claude-powered conversational assistant for answering tax questions, context-aware of the user's current calculation

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                     Browser (Client)                  │
│  ┌──────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │ Input     │  │ Results Page │  │ AI Chat UI     │ │
│  │ Form      │  │ + Bracket Viz│  │ (JS fetch)     │ │
│  └─────┬─────┘  └──────▲──────┘  └───────┬────────┘ │
└────────┼───────────────┼──────────────────┼──────────┘
         │ POST          │ render           │ POST
         ▼               │                  ▼
┌──────────────────────────────────────────────────────┐
│                    Flask App (app.py)                  │
│                                                       │
│  /             → render index.html                    │
│  /calculate    → validate → tax_engine → results.html │
│  /download     → generate_pdf → send file             │
│  /chat         → render chat.html                     │
│  /chat/ask     → Claude API → JSON response           │
└───────────────────────┬──────────────────────────────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
   ┌────────────┐ ┌──────────┐ ┌──────────────┐
   │ tax_engine │ │ generate │ │ Claude API   │
   │   .py      │ │ _pdf.py  │ │ (external)   │
   │            │ │          │ │              │
   │ Brackets,  │ │ ReportLab│ │ Sonnet 4     │
   │ deductions,│ │ 1040-    │ │ tax Q&A with │
   │ progressive│ │ style PDF│ │ user context │
   │ tax calc   │ │          │ │              │
   └────────────┘ └──────────┘ └──────────────┘
```

### Data Flow

1. User fills out the tax form in the browser
2. Form data is POSTed to `/calculate`
3. Flask validates input and passes it to `tax_engine.calculate_tax()`
4. The engine applies the standard deduction (or itemized if higher), runs progressive bracket calculations, and returns a full breakdown
5. Results are stored in the Flask session and rendered on the results page
6. User can download a PDF (generated on-demand by `generate_pdf.py`) or ask the AI assistant follow-up questions

### Key Design Decisions

- **Separated tax engine from Flask app** — The calculation logic is a pure Python module with no web framework dependencies. This makes it independently testable and reusable.
- **Session-based state** — Tax results are stored in the Flask session so the PDF download route and AI chat can reference them without re-computation.
- **Graceful AI degradation** — The AI chat feature requires an API key but the core tax calculator works fully without it. This keeps the demo reliable.
- **Client-side + server-side validation** — Input is validated in both the browser (immediate feedback) and Flask (security).

## Quick Start

```bash
# Clone the repository
git clone https://github.com/Bruhiann/ai-tax-agent.git
cd ai-tax-agent

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Open http://localhost:5000 in your browser
```

### Enable AI Chat (Optional)

```bash
export ANTHROPIC_API_KEY=your-key-here
python app.py
```

## Testing

```bash
cd tests
python test_tax_engine.py
```

Runs 8 test scenarios covering different income levels, filing statuses, deduction types, and edge cases.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3, Flask |
| Frontend | HTML5, CSS3, Vanilla JS |
| Tax Logic | Custom Python module (2024 IRS brackets) |
| PDF Generation | ReportLab |
| AI Assistant | Anthropic Claude API (Sonnet) |

## Security Considerations

This prototype implements basic security measures appropriate for a demo:

- **Input validation & sanitization** — All numeric inputs are validated server-side. Filing status is checked against a whitelist.
- **Flask session security** — Secret key for session signing (should be environment variable in production).
- **No persistent data storage** — No database; user data exists only in the session during use.

For a production version, additional measures would include:
- HTTPS/TLS encryption
- User authentication and authorization
- Database encryption at rest for any stored PII
- CSRF protection tokens
- Rate limiting on the AI chat endpoint
- SOC 2 compliance and IRS e-file certification
- GDPR/CCPA data handling policies

## Limitations & Future Improvements

- Only handles federal income tax (no state taxes)
- Single income source (W-2 wages only)
- No support for credits (Child Tax Credit, EITC, etc.)
- No AMT calculation
- Simplified deductions (no Schedule A itemization detail)

Future enhancements could include:
- Integration with IRS e-file systems
- Multi-state tax support
- OCR-based W-2 document scanning
- Support for investment income, self-employment, and other schedules
- Real-time tax law updates via AI retrieval
