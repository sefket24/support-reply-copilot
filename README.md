# Improving Support Response Quality and Reducing Unnecessary Escalations

**Tool:** Support Reply Copilot  
**Type:** Internal decision-aid tool for support agents  
**Status:** Prototype / proof of concept  
**Built with:** Python · Streamlit · Anthropic Claude API

---

## Problem

Support teams send inconsistent replies to similar tickets. Two agents handling the same billing question on the same day can produce responses that differ wildly in tone, completeness, and the next steps they offer. Neither response is technically wrong, but one of them will generate a follow-up ticket and the other won't.

On the escalation side, the problem runs in both directions. Some tickets get escalated that didn't need to be — an agent wasn't confident in their answer and routed it upward to be safe. Others that genuinely needed a second look got a copy-paste reply and fell through the cracks.

There's also a subtler issue: agents vary in how well they read tone. A frustrated customer who writes in short sentences and uses words like "again" and "still" is signaling something different than someone politely asking the same question for the first time. That signal affects how the reply should be framed, but it's easy to miss when you're moving fast through a queue.

---

## Observations

These patterns show up consistently across support teams that handle mixed ticket queues:

- **How-to questions get over-escalated.** A question like "how do I export my data as CSV?" has a clear answer. It doesn't need a second pair of eyes. But agents who aren't sure will escalate anyway.

- **Billing tickets underperform.** Agents are cautious with anything involving money, which is reasonable. But caution often translates into vague replies ("someone will look into this") instead of direct ones ("here's what happened and here's what we're doing").

- **Bug reports are hard to triage quickly.** The line between "user error" and "actual bug" is blurry. Agents often err on the side of "let me look into this" when the ticket is actually describing something that's been fixed, or a known issue with a workaround.

- **Tone detection is inconsistent.** Agents who are newer or working through high volume don't always catch signals of frustration or churn risk. Those tickets get the same reply as neutral ones.

---

## Hypothesis

If we give agents a fast, structured first pass on each ticket — before they start typing — we can improve two things:

1. **Reply quality.** An agent who sees a suggested reply, even if they rewrite it, starts from a better baseline than a blank text box.

2. **Escalation accuracy.** A clear deflect/escalate recommendation, with a one-line reason, gives agents a reference point. They can override it, but they're making an active decision rather than a default one.

The hypothesis is not that the AI reply gets sent as-is. It's that the structure and the first draft reduce the variance between agents and surface the signals that matter — sentiment, complexity, risk flags — before the agent commits to a response direction.

---

## Proposed Solution

A lightweight internal tool that sits alongside the support queue. Agents paste an incoming ticket (or it gets piped in via integration), and the tool returns:

- **Sentiment detection** — neutral, frustrated, urgent
- **Complexity classification** — simple, moderate, complex
- **Request type** — how-to, bug, billing, account, data, performance, cancellation, unclear
- **Deflection decision** — deflect with guidance, or route to human handling
- **Escalation flags** — specific signals worth acting on
- **Confidence score** — how certain the model is in its deflection recommendation
- **Suggested reply** — a draft the agent can use, edit, or ignore
- **Internal note** — one line for the agent that the customer won't see

The tool doesn't send anything. It doesn't update the ticket. It gives the agent a structured read of the situation in under five seconds, then gets out of the way.

---

## Example Scenario

**Incoming ticket:**

> Subject: Charged twice this month  
> 
> Hi, I've been charged twice for my subscription this month. I've emailed about this before and nothing happened. This is really frustrating. I'm considering canceling if this isn't sorted out today.

**What an agent might do without the tool:**

Route it to billing, add a note saying "customer upset about duplicate charge," wait for someone else to pick it up.

**What the tool surfaces:**

- Sentiment: **Frustrated**
- Type: **Billing**
- Complexity: **Moderate**
- Deflection: **Requires human handling** — billing errors require account verification and a refund action
- Escalation flags: *Billing error, mentions prior contact with no resolution, threatening cancellation, churn risk*
- Suggested reply: Direct acknowledgment, confirmation that this is being looked into today, clear timeline
- Internal note: *Previous contact flagged — check ticket history before responding*

The agent still owns the response. But they're starting from a clearer picture of what's at stake and what the customer actually needs.

---

## Expected Impact

- **Reduce unnecessary escalations** on simple ticket types (how-to, known bugs, standard account questions) where a confident direct answer is the right move
- **Improve first-contact resolution** on tickets where agents have the information to resolve but default to hedging
- **Surface churn risk earlier** so the right person sees it before a frustrated customer has to escalate themselves
- **Reduce onboarding time** for new agents by giving them a structural read of each ticket before they respond

These are directional. The actual numbers depend on queue volume, agent adoption, and how the tool gets integrated into the workflow.

---

## Assumptions and Reasoning

**The tool will be used as a reference, not a crutch.** Agents who treat the suggested reply as a starting point will get value from it. Agents who copy-paste without reading will occasionally send something that doesn't fit. That's a workflow and training problem, not a tool problem — but it's worth acknowledging.

**The deflection signal is the most useful output.** Agents don't need AI to write their replies for them. They need something that tells them "this one is yours to handle" vs "this one is fine to answer directly and close." That single decision point, surfaced fast, is where the tool earns its keep.

**False confidence is a risk.** If the model says "deflect" on a ticket that actually needed escalation, an agent who trusts that recommendation will send the wrong reply. The confidence score is there to surface uncertainty — agents should treat low-confidence deflection calls differently than high-confidence ones.

**The quality of the suggested reply depends on the ticket.** Short, vague tickets produce worse suggestions than detailed ones. The tool works best when the customer has given enough context to work with.

---

## Validation Plan

**Phase 1 — Manual testing (current)**  
Run real tickets through the tool (manually, using the prototype) and compare the suggested deflection decision and reply against what the agent actually sent. Look for patterns in where the two diverge and why.

**Phase 2 — Side-by-side pilot**  
Have a small group of agents use the tool alongside their normal workflow for two to four weeks. Track:
- Did the agent follow or override the deflection recommendation?
- Did tickets they deflected generate a follow-up?
- Did tickets they escalated get resolved at the next level, or bounced back?

**Phase 3 — Calibration**  
Use the pilot data to improve the prompt and classification logic. Focus on the ticket types where the tool's recommendation diverged most from the agent's actual decision.

Success looks like: fewer follow-ups on deflected tickets, fewer unnecessary escalations, agents reporting that the tool gives them useful signal. It doesn't look like: agents sending the AI reply verbatim or the tool becoming a dependency.

---

## Demo Instructions

### Run locally

```bash
git clone https://github.com/sefket24/support-reply-copilot.git
cd support-reply-copilot

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and add your Anthropic API key: ANTHROPIC_API_KEY=sk-ant-...

streamlit run app.py
```

App opens at `http://localhost:8501`.

### Deploy on Streamlit Cloud

1. Push the repo to GitHub
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud) → New app
3. Select repo, set `app.py` as the main file
4. Under **Advanced settings → Secrets**, add:

```
ANTHROPIC_API_KEY = "sk-ant-...your-key-here..."
```

5. Deploy — live in under a minute

### Test tickets to try

Paste these into the tool to see how it handles different ticket types:

**Simple how-to:**
> How do I change the email address on my account?

**Frustrated billing:**
> I was charged $99 yesterday and I cancelled my subscription two weeks ago. This is the second time this has happened. I want a refund immediately.

**Ambiguous bug:**
> The export button doesn't do anything when I click it. I've tried refreshing. Using Chrome on Windows 11.

**Churn risk:**
> We've been customers for three years and honestly the product has gotten worse, not better. Response times are slower, the new UI is confusing, and your support has been unhelpful lately. We're evaluating alternatives.

---

## Tech Stack

| Layer      | Tool                  |
|------------|-----------------------|
| UI         | Streamlit             |
| AI         | Anthropic Claude API  |
| Config     | python-dotenv         |
| Language   | Python 3.10+          |

---

## License

MIT
