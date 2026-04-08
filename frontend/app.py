import streamlit as st
import requests
import time

API = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="TableVision AI",
    layout="wide",
    page_icon="🍽️",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.main { background: #0f1117; }

.metric-card {
    background: linear-gradient(135deg, #1e2130 0%, #252840 100%);
    border-radius: 16px;
    padding: 20px;
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 12px;
    transition: all 0.3s ease;
}
.table-available { background: linear-gradient(135deg, #0d2b1e 0%, #0f3326 100%); border: 1px solid #00c853 !important; box-shadow: 0 0 20px rgba(0,200,83,0.15); }
.table-occupied  { background: linear-gradient(135deg, #2b0d0d 0%, #331313 100%); border: 1px solid #ff5252 !important; box-shadow: 0 0 20px rgba(255,82,82,0.15); }
.table-shareable { background: linear-gradient(135deg, #2b2200 0%, #332900 100%); border: 1px solid #ffc107 !important; box-shadow: 0 0 20px rgba(255,193,7,0.15); }
.table-clearing  { background: linear-gradient(135deg, #1a1a2b 0%, #20203a 100%); border: 1px solid #7c4dff !important; box-shadow: 0 0 20px rgba(124,77,255,0.15); }

.status-badge {
    display: inline-block; padding: 4px 12px; border-radius: 20px;
    font-size: 12px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;
}
.badge-available { background: rgba(0,200,83,0.2);   color: #00c853; border: 1px solid #00c853; }
.badge-occupied  { background: rgba(255,82,82,0.2);   color: #ff5252; border: 1px solid #ff5252; }
.badge-shareable { background: rgba(255,193,7,0.2);   color: #ffc107; border: 1px solid #ffc107; }
.badge-clearing  { background: rgba(124,77,255,0.2);  color: #7c4dff; border: 1px solid #7c4dff; }
.badge-full      { background: rgba(255,82,82,0.2);   color: #ff5252; border: 1px solid #ff5252; }

.seat-dot    { display: inline-block; width: 18px; height: 18px; border-radius: 50%; margin: 2px; }
.seat-filled { background: #ff5252; box-shadow: 0 0 6px rgba(255,82,82,0.6); }
.seat-empty  { background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.2); }

.ai-pulse { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #00c853; animation: pulse 1.5s infinite; margin-right: 6px; }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(0,200,83,0.7); } 70% { box-shadow: 0 0 0 8px rgba(0,200,83,0); } 100% { box-shadow: 0 0 0 0 rgba(0,200,83,0); } }

.hero-banner { background: linear-gradient(135deg, #1a1f35 0%, #0d1b2a 50%, #1a1f35 100%); border-radius: 20px; padding: 28px 36px; border: 1px solid rgba(99,179,237,0.2); margin-bottom: 24px; }
.kpi-box { background: linear-gradient(135deg, #1e2130, #252840); border-radius: 14px; padding: 18px; text-align: center; border: 1px solid rgba(255,255,255,0.06); }
.demo-banner { background: linear-gradient(90deg, #7c4dff22, #00c85322, #7c4dff22); border: 1px solid #7c4dff; border-radius: 10px; padding: 10px 18px; text-align: center; color: #7c4dff; font-weight: 600; margin-bottom: 16px; }
.stButton > button { border-radius: 10px !important; font-weight: 600 !important; border: 1px solid rgba(255,255,255,0.1) !important; }
</style>
""", unsafe_allow_html=True)

# Session state
if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = False
if "demo_step" not in st.session_state:
    st.session_state.demo_step = 0

# ── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🍽️ TableVision AI")
    st.markdown("<span class='ai-pulse'></span> **System Online**", unsafe_allow_html=True)
    st.divider()

    st.markdown("### 🔍 Find a Table")
    party_size = st.number_input("Party size", min_value=1, max_value=12, value=2)

    if st.button("Search Now", use_container_width=True, type="primary"):
        with st.spinner("AI scanning floor..."):
            time.sleep(0.8)
            try:
                res = requests.get(f"{API}/api/search-table", params={"party_size": party_size}).json()
                immediate = res.get("immediate", [])
                predicted = res.get("predicted", [])
                if immediate:
                    st.success(f"✅ {len(immediate)} option(s) found!")
                    for t in immediate:
                        st.markdown(f"""
                        <div style='background:#0d2b1e;border:1px solid #00c853;border-radius:10px;padding:10px;margin:6px 0'>
                        🟢 <b>Table {t['table_id']}</b> – {t['capacity']} seats<br>
                        <small style='color:#aaa'>{t['status'].upper()}</small>
                        </div>""", unsafe_allow_html=True)
                else:
                    st.warning("No tables available right now")
                if predicted:
                    st.info("⏳ Freeing up soon:")
                    for t in predicted:
                        st.markdown(f"Table {t['table_id']} – ~**{t['estimated_minutes_remaining']} min**")
            except Exception as e:
                st.error(f"Backend not reachable: {e}")

    st.divider()
    st.markdown("### 🎥 Demo Controls")
    demo_toggle = st.toggle("Auto-Demo Mode", value=st.session_state.demo_mode)
    st.session_state.demo_mode = demo_toggle
    if demo_toggle:
        st.caption("Tables will auto-update every 3s to simulate live camera feed")

    st.divider()
    st.markdown("### 📤 Analyze Media")
    media_type = st.radio("Input type", ["📷 Image", "🎥 Video"], horizontal=True)

    if media_type == "📷 Image":
        uploaded = st.file_uploader("Camera frame (.jpg)", type=["jpg", "jpeg", "png"])
        if uploaded and st.button("Analyze with GPT-4o", use_container_width=True):
            with st.spinner("🤖 GPT-4o analyzing image..."):
                res = requests.post(f"{API}/api/analyze", files={"file": uploaded})
                if res.status_code == 200:
                    st.success("✅ Analysis complete!")
                    st.rerun()
                else:
                    st.error("Analysis failed")
    else:
        uploaded_video = st.file_uploader("Restaurant video (.mp4)", type=["mp4", "mov", "avi"])
        if uploaded_video:
            st.video(uploaded_video)
            if st.button("🎥 Analyze Video with GPT-4o", use_container_width=True, type="primary"):
                progress = st.progress(0, text="Extracting frames...")
                status_box = st.empty()
                with st.spinner("🤖 GPT-4o analyzing video frames..."):
                    res = requests.post(
                        f"{API}/api/analyze-video",
                        files={"file": uploaded_video},
                        timeout=120
                    )
                if res.status_code == 200:
                    data = res.json()
                    frames = data.get("frame_results", [])
                    total = len(frames)
                    progress.progress(100, text="Analysis complete!")
                    status_box.success(
                        f"✅ Analyzed {total} frames from "
                        f"{data.get('video_duration_sec', '?')}s video"
                    )
                    st.markdown("**Frame-by-frame results:**")
                    for frame in frames:
                        ts = frame["timestamp_sec"]
                        tables = frame["tables"]
                        occupied = sum(1 for t in tables.values() if t.get("has_people"))
                        guest_count = sum(t.get("occupied_seats", 0) for t in tables.values())
                        total_tables = len(tables)
                        st.markdown(f"`{ts}s` — **{occupied}/{total_tables}** tables occupied · {guest_count} guests")
                    st.rerun()
                else:
                    st.error("Video analysis failed")

# ── Hero Banner ───────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <h2 style="margin:0;color:#e2e8f0">🍽️ TableVision <span style="color:#63b3ed">AI</span> — Live Floor Intelligence</h2>
    <p style="margin:6px 0 0 0;color:#718096;font-size:14px">
        <span class="ai-pulse"></span>
        Real-time occupancy detection powered by GPT-4o Vision · Auto-refreshing every 10s
    </p>
</div>
""", unsafe_allow_html=True)

# ── Demo scenarios ────────────────────────────────────────────────────
DEMO_SCENARIOS = [
    {1: ("occupied",2,2), 2: ("available",0,4), 3: ("available",0,2), 4: ("full",6,6),    5: ("occupied",2,4), 6: ("available",0,2)},
    {1: ("available",0,2),2: ("occupied",2,4), 3: ("occupied",1,2), 4: ("clearing",0,6),  5: ("full",4,4),     6: ("occupied",1,2)},
    {1: ("shareable",1,2),2: ("available",0,4),3: ("full",2,2),     4: ("available",0,6), 5: ("occupied",3,4), 6: ("available",0,2)},
    {1: ("full",2,2),     2: ("occupied",3,4), 3: ("available",0,2),4: ("occupied",4,6),  5: ("clearing",0,4), 6: ("shareable",1,2)},
]


def get_floor():
    try:
        return requests.get(f"{API}/api/floor-state", timeout=2).json()
    except:
        return {}


floor = get_floor()

if st.session_state.demo_mode:
    step = st.session_state.demo_step % len(DEMO_SCENARIOS)
    scenario = DEMO_SCENARIOS[step]
    st.markdown("""<div class="demo-banner">🎥 DEMO MODE — Simulating live camera feed from GPT-4o Vision</div>""", unsafe_allow_html=True)
    for tid_str, table in floor.items():
        tid = int(tid_str)
        if tid in scenario:
            status, seated, cap = scenario[tid]
            floor[tid_str]["status"] = status
            floor[tid_str]["occupied_seats"] = seated
            floor[tid_str]["has_people"] = seated > 0

# ── KPI Row ───────────────────────────────────────────────────────────
if floor:
    total = len(floor)
    available_count = sum(1 for t in floor.values() if t["status"] == "available")
    occupied_count  = sum(1 for t in floor.values() if t["status"] in ["occupied", "full"])
    total_seated    = sum(t["occupied_seats"] for t in floor.values())

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="kpi-box"><div style="font-size:32px;font-weight:700;color:#00c853">{available_count}</div><div style="color:#718096;font-size:13px">Available Tables</div></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi-box"><div style="font-size:32px;font-weight:700;color:#ff5252">{occupied_count}</div><div style="color:#718096;font-size:13px">Occupied Tables</div></div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="kpi-box"><div style="font-size:32px;font-weight:700;color:#63b3ed">{total_seated}</div><div style="color:#718096;font-size:13px">Guests Seated</div></div>""", unsafe_allow_html=True)
    with k4:
        pct = int((occupied_count / total) * 100) if total else 0
        color = "#ff5252" if pct > 70 else "#ffc107" if pct > 40 else "#00c853"
        st.markdown(f"""<div class="kpi-box"><div style="font-size:32px;font-weight:700;color:{color}">{pct}%</div><div style="color:#718096;font-size:13px">Floor Occupancy</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

# ── Floor Grid ────────────────────────────────────────────────────────
st.markdown("### 🗺️ Live Floor Map")

STATUS_CLASS = {"available": "table-available", "occupied": "table-occupied", "full": "table-occupied", "shareable": "table-shareable", "clearing": "table-clearing"}
BADGE_CLASS  = {"available": "badge-available", "occupied": "badge-occupied",  "full": "badge-full",     "shareable": "badge-shareable", "clearing": "badge-clearing"}
STATUS_ICON  = {"available": "🟢", "occupied": "🔴", "full": "🔴", "shareable": "🟡", "clearing": "🟪"}

if floor:
    cols = st.columns(3)
    for i, (tid, table) in enumerate(floor.items()):
        status = table["status"]
        cap    = table["capacity"]
        seated = table["occupied_seats"]

        seats_html = "".join([
            f'<span class="seat-dot {"seat-filled" if j < seated else "seat-empty"}"></span>'
            for j in range(cap)
        ])
        eta_html = ""
        if table.get("estimated_minutes_remaining") is not None:
            eta_html = f'<div style="color:#718096;font-size:12px;margin-top:8px">⏱️ Est. free in {table["estimated_minutes_remaining"]} min</div>'

        card_html = f"""
        <div class="metric-card {STATUS_CLASS.get(status, '')}">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
                <span style="font-size:18px;font-weight:700;color:#e2e8f0">
                    {STATUS_ICON.get(status, '⚪')} Table {table['table_id']}
                </span>
                <span class="status-badge {BADGE_CLASS.get(status, '')}">{status}</span>
            </div>
            <div style="margin-bottom:10px">{seats_html}</div>
            <div style="color:#a0aec0;font-size:13px">{seated} / {cap} seats occupied</div>
            {eta_html}
        </div>
        """
        with cols[i % 3]:
            st.markdown(card_html, unsafe_allow_html=True)
            if st.button(f"Reset T{table['table_id']}", key=f"r_{tid}"):
                requests.post(f"{API}/api/reset-table/{table['table_id']}")
                st.rerun()
else:
    st.error("⚠️ Cannot reach backend. Is uvicorn running?")

# ── Footer ────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<div style='text-align:center;color:#4a5568;font-size:12px'>"
    "TableVision AI · Built with GPT-4o Vision · FastAPI · Streamlit"
    "</div>", unsafe_allow_html=True
)

# ── Auto-refresh ──────────────────────────────────────────────────────
if st.session_state.demo_mode:
    time.sleep(3)
    st.session_state.demo_step += 1
    st.rerun()
else:
    time.sleep(10)
    st.rerun()
