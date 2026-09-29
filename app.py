import os
import streamlit as st
from hindsight_client import Hindsight

st.set_page_config(
    page_title="OpsMemory AI",
    page_icon="🧠",
    layout="wide",
)

st.markdown("""
<style>
.main-title {font-size: 2.4rem; font-weight: 800; margin-bottom: 0.2rem;}
.subtitle {color: #6b7280; font-size: 1.05rem;}
.memory-card {padding: 1rem; border: 1px solid #e5e7eb; border-radius: 12px; margin-bottom: .7rem;}
.badge {display:inline-block; padding:.2rem .55rem; border-radius:999px; background:#eef2ff; margin-right:.35rem; font-size:.8rem;}
</style>
""", unsafe_allow_html=True)

HINDSIGHT_URL = os.getenv("HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io")
HINDSIGHT_KEY = os.getenv("HINDSIGHT_API_KEY", "")
BANK_ID = os.getenv("HINDSIGHT_BANK_ID", "ops-memory-agent")

st.markdown('<div class="main-title">🧠 OpsMemory AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">An incident-response agent that remembers what happened, '
    'what fixed it, and gets better when the next incident arrives.</div>',
    unsafe_allow_html=True
)

if not HINDSIGHT_KEY:
    st.error("Add HINDSIGHT_API_KEY to your environment before running the app.")
    st.code("set HINDSIGHT_API_KEY=hsk_your_key_here", language="powershell")
    st.stop()

@st.cache_resource
def get_client():
    return Hindsight(base_url=HINDSIGHT_URL, api_key=HINDSIGHT_KEY)

client = get_client()

def ensure_bank():
    try:
        client.create_bank(bank_id=BANK_ID, name="OpsMemory AI")
    except Exception:
        # Bank may already exist.
        pass

def seed_memories():
    ensure_bank()
    memories = [
        {
            "content": (
                "Incident INC-104: Checkout API returned HTTP 502 after a production deployment. "
                "Root cause: the payment-service environment variable PAYMENT_GATEWAY_URL was missing "
                "from the new deployment. Resolution: rollback, restore the environment variable, "
                "redeploy, and add an environment validation check to CI."
            ),
            "context": "Production incident postmortem",
            "metadata": {"incident_id": "INC-104", "service": "checkout", "status": "resolved"}
        },
        {
            "content": (
                "Incident INC-087: Checkout API returned HTTP 502 during a release. "
                "Root cause: an incompatible gateway configuration was deployed. "
                "Resolution: rollback to the last known-good release, validate gateway configuration "
                "in staging, then redeploy."
            ),
            "context": "Production incident postmortem",
            "metadata": {"incident_id": "INC-087", "service": "checkout", "status": "resolved"}
        },
        {
            "content": (
                "Incident INC-091: Redis memory reached 98 percent and requests became slow. "
                "Root cause: an unbounded cache allowed stale keys to accumulate. "
                "Resolution: enable maxmemory with an eviction policy, remove stale keys, and add "
                "a Redis memory alert at 80 percent."
            ),
            "context": "Production incident postmortem",
            "metadata": {"incident_id": "INC-091", "service": "redis", "status": "resolved"}
        },
        {
            "content": (
                "Incident INC-113: Orders service exhausted its database connection pool. "
                "Root cause: a code path did not close connections on an exception. "
                "Resolution: restart affected pods, patch connection handling, add pool saturation "
                "monitoring, and test exception paths."
            ),
            "context": "Production incident postmortem",
            "metadata": {"incident_id": "INC-113", "service": "orders", "status": "resolved"}
        },
        {
            "content": (
                "Team learning: for recurring production incidents, first compare the current "
                "symptoms with previous incidents, verify the likely root cause, apply the safest "
                "known remediation, and record the outcome so the next response improves."
            ),
            "context": "Operational learning",
            "metadata": {"type": "lesson"}
        },
    ]
    try:
        client.retain_batch(bank_id=BANK_ID, items=memories)
        return True, "Demo memory seeded."
    except Exception as e:
        return False, str(e)

def analyze_incident(incident):
    ensure_bank()
    recall = client.recall(
        bank_id=BANK_ID,
        query=f"Find previous incidents similar to this: {incident}",
        max_tokens=3000,
        budget="mid",
    )
    prompt = f"""
You are OpsMemory AI, a production incident-response assistant.

Current incident:
{incident}

Use the persistent memories you have retrieved to produce:
1. Likely root cause, clearly labeled as a hypothesis.
2. Immediate safe actions, in priority order.
3. Similar past incidents and what worked.
4. What should be checked before changing production.
5. A short verification plan.
6. One lesson that should be retained after resolution.

Do not claim certainty when the evidence is incomplete. Prefer rollback or reversible actions
when appropriate. Keep the response practical for an on-call engineer.
"""
    reflection = client.reflect(
        bank_id=BANK_ID,
        query=prompt,
        context="\n".join([m.text for m in recall.results[:8]]),
        budget="mid",
        max_tokens=1600,
    )
    return recall, reflection

def retain_resolution(incident, resolution):
    ensure_bank()
    content = (
        f"New incident and resolution learned by OpsMemory AI.\n"
        f"Incident: {incident}\n"
        f"Resolution/outcome: {resolution}\n"
        f"Lesson: Preserve the successful diagnostic path and verification step for similar "
        f"future incidents."
    )
    client.retain(
        bank_id=BANK_ID,
        content=content,
        context="Resolved production incident",
        metadata={"source": "live_demo", "status": "resolved"}
    )

with st.sidebar:
    st.header("🎬 Demo controls")
    st.caption("Use these controls to make the memory-learning loop visible to judges.")
    if st.button("🌱 Seed realistic incident memory", use_container_width=True):
        ok, msg = seed_memories()
        (st.success if ok else st.error)(msg)

    st.divider()
    st.markdown("**Architecture**")
    st.markdown("""
    `Incident → Recall → Reflect → Action → Resolve → Retain → Better next response`
    """)
    st.caption("Required technology: Hindsight persistent memory.")

tab1, tab2 = st.tabs(["🚨 Investigate incident", "🧠 Learning loop"])

with tab1:
    st.subheader("Current production incident")
    incident = st.text_area(
        "Paste the alert, error log, or incident description",
        height=180,
        value=(
            "Checkout API is returning HTTP 502 for about 35% of requests immediately after "
            "today's deployment. Payment failures increased. The previous release was healthy."
        ),
    )

    if st.button("🔎 Investigate with memory", type="primary", use_container_width=True):
        with st.spinner("Recalling past incidents and reasoning over them..."):
            try:
                recall, reflection = analyze_incident(incident)
                st.session_state["last_incident"] = incident
                st.session_state["last_reflection"] = reflection.text
                st.session_state["last_memories"] = recall.results

                c1, c2 = st.columns([1.4, 1])
                with c1:
                    st.markdown("### 🤖 Recommended response")
                    st.write(reflection.text)
                with c2:
                    st.markdown("### 🧠 Memories used")
                    if recall.results:
                        for m in recall.results[:5]:
                            st.markdown(
                                f'<div class="memory-card"><span class="badge">{m.type}</span>{m.text}</div>',
                                unsafe_allow_html=True
                            )
                    else:
                        st.info("No relevant memories found. This is the cold-start state.")
            except Exception as e:
                st.error(f"Investigation failed: {e}")

with tab2:
    st.subheader("Make the agent learn from the outcome")
    st.write(
        "After the incident is resolved, store the outcome. The next similar incident can "
        "retrieve this experience."
    )
    resolution = st.text_area(
        "Resolution / postmortem outcome",
        height=160,
        value=(
            "Rolled back the deployment. Confirmed the payment gateway environment variable "
            "was missing in the new deployment. Restored it, redeployed successfully, and "
            "added CI validation for required production environment variables."
        ),
    )
    if st.button("💾 Retain this lesson in Hindsight", use_container_width=True):
        if "last_incident" not in st.session_state:
            st.warning("Investigate an incident first.")
        else:
            try:
                retain_resolution(st.session_state["last_incident"], resolution)
                st.success(
                    "Memory retained. The agent has now learned from this incident. "
                    "Run another similar incident to demonstrate recall."
                )
            except Exception as e:
                st.error(f"Could not retain memory: {e}")

    st.divider()
    st.markdown("### 🎥 60-second judge demo")
    st.markdown("""
    **1. Cold start:** show a new incident and explain that a stateless assistant has no incident history.

    **2. Recall:** click **Investigate with memory** and show the previous 502 incidents appearing.

    **3. Reason:** show that the agent connects the current symptoms to the remembered root cause and remediation.

    **4. Learn:** change the resolution slightly, click **Retain this lesson in Hindsight**.

    **5. Prove persistence:** enter a second similar incident and investigate again. The new response should
    incorporate the newly retained experience.

    **Closing line:** “The value isn't that our agent can answer an incident once. The value is that every
    resolved incident becomes organizational memory for the next one.”
    """)
