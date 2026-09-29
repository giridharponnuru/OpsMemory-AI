# 🧠 OpsMemory AI — Incident Response Agent with Persistent Memory

## One-line pitch

**OpsMemory AI turns every production incident into organizational memory, so the next similar outage gets diagnosed faster.**

## Problem

Production incidents repeat. Engineers spend valuable time searching old incident tickets, postmortems and runbooks to rediscover what happened and what fixed it.

A generic chatbot can explain an error, but it does not automatically build durable organizational experience from previous incidents.

## Solution

OpsMemory AI is an incident-response agent powered by **Hindsight**.

It:
1. receives a live incident/alert,
2. recalls relevant historical incidents,
3. reasons over those memories,
4. proposes a safe response,
5. stores the final resolution as new experience,
6. uses that experience during future incidents.

### Memory loop

`Incident → Recall → Reflect → Resolve → Retain → Better future response`

## Why Hindsight is central

Hindsight provides the persistent memory layer through its core operations:
- **Retain** — store incidents and resolutions
- **Recall** — retrieve relevant previous incidents
- **Reflect** — reason over memories and formulate a response

The hackathon problem statement explicitly requires Hindsight and says memory should be central and visibly improve the agent over time.

## Demo scenario

Historical:
- checkout API 502 caused by missing payment gateway environment variable
- another checkout 502 caused by bad gateway configuration
- Redis memory incident
- database connection pool incident

Current:
> Checkout API is returning HTTP 502 for ~35% of requests immediately after today's deployment.

The agent recalls the historical 502 incidents and recommends comparing deployment configuration, checking the payment gateway environment variable, considering rollback, and verifying the fix.

Then the resolved incident is retained. A future similar incident can use that new experience.

## Stack

- Python
- Streamlit
- Hindsight Cloud / Hindsight Python SDK
- Any LLM configured by Hindsight Cloud

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

set HINDSIGHT_API_KEY=hsk_your_key_here
set HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io
set HINDSIGHT_BANK_ID=ops-memory-agent

streamlit run app.py
```

## Security

Never commit the Hindsight API key. Use environment variables or Streamlit secrets.

## Judging alignment

| Criterion | How OpsMemory AI addresses it |
|---|---|
| Innovation — 30% | Converts incident history into an evolving operational memory rather than a one-shot chatbot |
| Hindsight Memory — 25% | Retain + Recall + Reflect are the core workflow |
| Technical Implementation — 20% | Clean Python app, explicit memory loop, error handling and persistent bank |
| User Experience — 15% | One-screen incident workflow with visible recalled memories |
| Real-world Impact — 10% | Targets a genuine production/on-call workflow |

## Suggested future extensions

- Jira/ServiceNow incident ingestion
- Slack incident-channel ingestion
- GitHub deployment correlation
- automatic postmortem generation
- approval workflow before production actions
- incident similarity dashboard
