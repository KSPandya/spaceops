import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import math

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SPACE OPS COMMAND | SOP DASHBOARD",
    layout="wide",
    page_icon="🛰️",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────
# DARK MILITARY CSS (LARGE FONTS & HIGH CONTRAST)
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }

.stApp { background-color: #050B18 !important; color: #FFFFFF; font-family: 'Share Tech Mono', monospace; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: #060D1E; border-bottom: 1px solid #0E2040; gap: 2px; padding: 0 10px; }
.stTabs [data-baseweb="tab"] { color: #8AAED0; background: transparent; border: none; border-bottom: 2px solid transparent; padding: 12px 20px; font-family: 'Share Tech Mono', monospace; font-size: 15px; letter-spacing: 2px; transition: all 0.2s; }
.stTabs [data-baseweb="tab"]:hover { color: #FFFFFF; }
.stTabs [aria-selected="true"] { color: #00E5FF !important; border-bottom: 2px solid #00E5FF !important; background: transparent !important; font-weight: bold; }
.stTabs [data-baseweb="tab-panel"] { background: transparent; padding-top: 15px; }

/* Section Headers */
.sec-hdr { font-family: 'Share Tech Mono', monospace; font-size: 14px; color: #56CCF2; letter-spacing: 3px; text-transform: uppercase; border-bottom: 1px solid #0E2040; padding-bottom: 5px; margin: 18px 0 10px; font-weight: bold; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #050B18; }
::-webkit-scrollbar-thumb { background: #0E2040; border-radius: 3px; }

/* Buttons */
.stButton > button { background: #060D1E; color: #00E5FF; border: 1px solid #00E5FF40; border-radius: 3px; font-family: 'Share Tech Mono', monospace; font-size: 14px; letter-spacing: 1px; padding: 8px 16px; transition: all 0.2s; }
.stButton > button:hover { background: #00E5FF15; border-color: #00E5FF; color: #FFFFFF; }

/* Inputs / selects */
.stSelectbox > div > div, .stMultiSelect > div > div { background: #060D1E !important; border-color: #0E2040 !important; color: #FFFFFF !important; font-family: 'Share Tech Mono', monospace !important; font-size: 14px !important; }
.stSlider > div > div > div { background: #0E2040; }

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# SYNTHETIC DATA
# ─────────────────────────────────────────────────────────────
random.seed(42)
np.random.seed(42)

COUNTRIES = {
    'USA':  {'flag': '🇺🇸', 'cls': 'friendly',  'col': '#2F80ED', 'fullname': 'United States'},
    'EU':   {'flag': '🇪🇺', 'cls': 'friendly',  'col': '#2F80ED', 'fullname': 'European Union'},
    'GBR':  {'flag': '🇬🇧', 'cls': 'friendly',  'col': '#2F80ED', 'fullname': 'United Kingdom'},
    'JPN':  {'flag': '🇯🇵', 'cls': 'friendly',  'col': '#2F80ED', 'fullname': 'Japan'},
    'RUS':  {'flag': '🇷🇺', 'cls': 'adversary', 'col': '#EB5757', 'fullname': 'Russia'},
    'CHN':  {'flag': '🇨🇳', 'cls': 'adversary', 'col': '#EB5757', 'fullname': "China"},
    'IRN':  {'flag': '🇮🇷', 'cls': 'adversary', 'col': '#EB5757', 'fullname': 'Iran'},
    'UNK':  {'flag': '🏴', 'cls': 'unknown',   'col': '#9CA3AF', 'fullname': 'Unknown'},
    'JUNK': {'flag': '🗑️', 'cls': 'unknown',   'col': '#9CA3AF', 'fullname': 'Debris'},
}

SAT_TYPES = ['RECON', 'COMMS', 'NAV', 'SIGINT', 'WEATHER', 'ISR', 'EW', 'DEBRIS', 'UNKNOWN']
ORBIT_RANGES = {'LEO': (200, 2000), 'MEO': (2000, 35786), 'GEO': (35786, 35786), 'HEO': (500, 50000)}

@st.cache_data
def gen_catalog(n=100):
    rows = []
    country_keys = list(COUNTRIES.keys())
    orbit_pool = ['LEO']*50 + ['MEO']*15 + ['GEO']*20 + ['HEO']*10 + ['DEBRIS']*5
    for i in range(n):
        ot_raw = random.choice(orbit_pool)
        ot = 'LEO' if ot_raw == 'DEBRIS' else ot_raw
        alt_lo, alt_hi = ORBIT_RANGES[ot]
        altitude = round(random.uniform(alt_lo, min(alt_hi, 40000)), 1)
        country = random.choice(country_keys)
        cinfo = COUNTRIES[country]
        rows.append({
            'id':          f'SAT-{40000+i:05d}',
            'norad':       40000 + i,
            'name':        f"{country}-{random.choice(SAT_TYPES)}-{i:03d}",
            'country':     country,
            'fullname':    cinfo['fullname'],
            'flag':        cinfo['flag'],
            'cls':         cinfo['cls'],
            'orbit_type':  ot if ot_raw != 'DEBRIS' else 'LEO',
            'sat_type':    'DEBRIS' if ot_raw == 'DEBRIS' else random.choice(SAT_TYPES),
            'altitude_km': altitude,
            'velocity_kms': round(7.9 * (6371/(6371+altitude))**0.5, 3),
            'inclination': round(random.uniform(0, 98), 2),
            'raan':        round(random.uniform(0, 360), 2),
            'true_anom':   round(random.uniform(0, 360), 2),
            'threat_score': round(max(0, random.betavariate(1.5, 5)) if cinfo['cls'] == 'adversary'
                                  else random.uniform(0, 0.15), 4),
            'last_maneuver': random.choice([None, None, None, f'{random.randint(1,72)}h ago']),
            'status':      random.choice(['OPERATIONAL','OPERATIONAL','DEGRADED','UNKNOWN']),
            'latitude':    round(random.uniform(-70, 70), 2),
            'longitude':   round(random.uniform(-180, 180), 2),
        })
    return pd.DataFrame(rows)

DF = gen_catalog(100)

# ─────────────────────────────────────────────────────────────
# ORBITAL MECHANICS HELPERS
# ─────────────────────────────────────────────────────────────
R_E = 1.0  # Normalised Earth radius

def alt2r(alt_km):
    return alt_km / 6371.0

def orbit_pos(alt, inc_d, raan_d, nu_d):
    r = R_E + alt2r(alt)
    i, ra, nu = math.radians(inc_d), math.radians(raan_d), math.radians(nu_d)
    xo, yo = r * math.cos(nu), r * math.sin(nu)
    x = xo*math.cos(ra) - yo*math.cos(i)*math.sin(ra)
    y = xo*math.sin(ra) + yo*math.cos(i)*math.cos(ra)
    z = yo*math.sin(i)
    return x, y, z

def orbit_trail(alt, inc, raan, nu, n=100, frac=0.3):
    angles = np.linspace(nu - frac*360, nu, n)
    xs, ys, zs = [], [], []
    for a in angles:
        x, y, z = orbit_pos(alt, inc, raan, a)
        xs.append(x); ys.append(y); zs.append(z)
    return xs, ys, zs

def earth_surface(res=80):
    u = np.linspace(0, 2*np.pi, res)
    v = np.linspace(0, np.pi, res)
    U, V = np.meshgrid(u, v)
    lat = np.degrees(V - np.pi/2)
    c = (np.sin(lat*np.pi/30)*0.4 + np.sin(U*3)*0.2 + np.cos(lat*np.pi/25 + U)*0.15 + 0.55)
    c = np.clip(c, 0, 1)
    return go.Surface(
        x=R_E * np.cos(U)*np.sin(V), y=R_E * np.sin(U)*np.sin(V), z=R_E * np.cos(V),
        surfacecolor=c,
        colorscale=[[0.00, '#051830'], [0.18, '#0a2d5e'], [0.35, '#0f4d99'], [0.50, '#1e6b3f'],
                    [0.65, '#2d7a3a'], [0.80, '#3d5c28'], [1.00, '#5a7a3a']],
        showscale=False, opacity=1.0, hoverinfo='skip', name='Earth',
    )

def atmo_sphere():
    u = np.linspace(0, 2*np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    U, V = np.meshgrid(u, v)
    R = 1.04
    return go.Surface(
        x=R*np.cos(U)*np.sin(V), y=R*np.sin(U)*np.sin(V), z=R*np.cos(V),
        colorscale=[[0,'#001840'],[1,'#0033aa']],
        showscale=False, opacity=0.07, hoverinfo='skip', surfacecolor=np.ones((50,50)), showlegend=False
    )

CLS_COLOR = {'friendly': '#2F80ED', 'adversary': '#EB5757', 'unknown': '#9CA3AF'}

# --- UPGRADED BASE LAYOUT FOR HIGH CONTRAST & READABILITY ---
BASE_LAYOUT = dict(
    paper_bgcolor='#050B18', plot_bgcolor='#050B18',
    font=dict(color='#FFFFFF', family='Share Tech Mono', size=14),
    margin=dict(l=2, r=2, t=35, b=2), showlegend=True,
    legend=dict(bgcolor='#06111E', bordercolor='#0E2040', borderwidth=1, font=dict(size=13, color='#FFFFFF')),
)

SCENE = dict(
    bgcolor='#020810',
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, showbackground=False),
    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, showbackground=False),
    zaxis=dict(showgrid=False, zeroline=False, showticklabels=False, showbackground=False),
    aspectmode='cube', camera=dict(eye=dict(x=2.1, y=1.4, z=1.3)),
)

# ─────────────────────────────────────────────────────────────
# HELPER WIDGETS
# ─────────────────────────────────────────────────────────────
def sec(label):
    st.markdown(f'<div class="sec-hdr">◈ {label}</div>', unsafe_allow_html=True)

def kv(label, val, color='#FFFFFF'):
    return (f"<div style='display:flex;justify-content:space-between;"
            f"padding:4px 0;border-bottom:1px solid #060D1E;"
            f"font-family:Share Tech Mono,monospace;font-size:12px;'>"
            f"<span style='color:#8AAED0'>{label}</span>"
            f"<span style='color:{color};font-weight:bold'>{val}</span></div>")

def bar(pct, color):
    return (f"<div style='background:#060D1E;border-radius:2px;height:4px;margin-top:6px;'>"
            f"<div style='background:{color};width:{min(pct,100):.0f}%;height:4px;"
            f"border-radius:2px;box-shadow:0 0 6px {color}88;'></div></div>")

def tile(label, val, sub, color):
    return f"""<div style='background:linear-gradient(145deg,#0A1526,#07101E);
        border:1px solid {color}50;border-top:3px solid {color};
        border-radius:5px;padding:16px 10px;text-align:center;'>
        <div style='font-size:12px;color:#8AAED0;letter-spacing:2px;font-weight:bold'>{label}</div>
        <div style='font-size:32px;color:{color};font-weight:bold;margin:5px 0'>{val}</div>
        <div style='font-size:11px;color:#C8D8EE'>{sub}</div>
    </div>"""

# ─────────────────────────────────────────────────────────────
# TAB 0 — HOME (RESTORED PLAY/PAUSE ANIMATION & SLIDERS)
# ─────────────────────────────────────────────────────────────
def home_3d():
    traces = [earth_surface(), atmo_sphere()]
    t = np.linspace(0, 2*np.pi, 300)
    for alt, col, name in [(550, '#2F80ED', 'LEO Band'),(20200, '#27AE60', 'MEO Band'),(35786, '#F2C94C', 'GEO Belt')]:
        r = R_E + alt2r(alt)
        traces.append(go.Scatter3d(x=r*np.cos(t), y=r*np.sin(t), z=np.zeros(300), mode='lines',
            line=dict(color=col, width=1, dash='dot'), opacity=0.2, showlegend=True, name=name, hoverinfo='skip'))

    for cls in ['friendly', 'adversary', 'unknown']:
        sub = DF[DF['cls'] == cls]
        col = CLS_COLOR[cls]
        xs, ys, zs, htexts = [], [], [], []
        for _, s in sub.iterrows():
            x, y, z = orbit_pos(s.altitude_km, s.inclination, s.raan, s.true_anom)
            xs.append(x); ys.append(y); zs.append(z)
            htexts.append(f"<b>{s['id']}</b><br>{s['flag']} {s['fullname']}<br>Type: {s['sat_type']}<br>Orbit: {s['orbit_type']}<br>Alt: {s.altitude_km:,.0f} km<br>Vel: {s.velocity_kms:.3f} km/s<br>Threat: {s.threat_score:.4f}")
        
        sym = 'diamond' if cls == 'adversary' else 'circle'
        traces.append(go.Scatter3d(x=xs, y=ys, z=zs, mode='markers',
            marker=dict(size=4, color=col, opacity=0.9, symbol=sym, line=dict(width=0.5, color='white')),
            name=cls.upper(), text=htexts, hovertemplate='%{text}<extra></extra>'))
        
        for _, s in sub.head(6).iterrows():
            tx, ty, tz = orbit_trail(s.altitude_km, s.inclination, s.raan, s.true_anom)
            traces.append(go.Scatter3d(x=tx, y=ty, z=tz, mode='lines', line=dict(color=col, width=1), opacity=0.18, showlegend=False, hoverinfo='skip'))

    # RESTORED: Animation frames for rotation
    frames = []
    for k in range(72):
        ang = k * 5
        ex = 2.3 * math.cos(math.radians(ang))
        ey = 2.3 * math.sin(math.radians(ang))
        frames.append(go.Frame(layout=dict(scene=dict(camera=dict(eye=dict(x=ex, y=ey, z=1.2)))), name=str(k)))

    fig = go.Figure(data=traces, frames=frames)
    
    # RESTORED: updatemenus (Play/Pause) and sliders
    fig.update_layout(BASE_LAYOUT, height=640, title=dict(text='LIVE ORBITAL PICTURE — ECI FRAME (J2000)', font=dict(size=14, color='#00E5FF'), x=0.5), scene=SCENE,
        updatemenus=[dict(type='buttons', showactive=False, y=-0.04, x=0.5, xanchor='center', bgcolor='#060D1E', bordercolor='#0E2040', font=dict(color='#00E5FF', size=12, family='Share Tech Mono'),
            buttons=[
                dict(label='▶ ORBIT', method='animate', args=[None, dict(frame=dict(duration=60, redraw=True), fromcurrent=True, mode='immediate', transition=dict(duration=0))]),
                dict(label='⏹ HOLD', method='animate', args=[[None], dict(mode='immediate', frame=dict(duration=0, redraw=False), transition=dict(duration=0))])
            ])],
        sliders=[dict(active=0, x=0, y=-0.02, len=1.0, currentvalue=dict(visible=False), bgcolor='#060D1E', bordercolor='#0E2040', tickcolor='#0E2040', font=dict(color='#3A7AB8', size=9), transition=dict(duration=0),
            steps=[dict(method='animate', args=[[str(k)], dict(mode='immediate', frame=dict(duration=0, redraw=True), transition=dict(duration=0))], label='') for k in range(72)]
        )])
    return fig

def home_donut():
    oc = DF['orbit_type'].value_counts()
    fig = go.Figure(go.Pie(
        labels=oc.index, values=oc.values, hole=0.55,
        marker=dict(colors=['#2F80ED','#F2C94C','#EB5757','#27AE60'], line=dict(color='#050B18', width=2)),
        textfont=dict(size=14, family='Share Tech Mono', color='white'),
        hovertemplate='<b>%{label}</b><br>%{value} objects<br>%{percent}<extra></extra>',
    ))
    fig.update_layout(BASE_LAYOUT, height=250, margin=dict(l=5,r=5,t=20,b=5), annotations=[dict(text='ORBITS', x=0.5, y=0.5, font=dict(size=15, color='#FFFFFF', family='Share Tech Mono'), showarrow=False)])
    return fig

def home_threat_line():
    hrs = list(range(-24, 1))
    vals = [3,2,4,5,3,2,3,4,6,8,7,5,4,3,5,7,9,11,8,7,9,12,15,18,23]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hrs, y=vals, mode='lines+markers', line=dict(color='#EB5757', width=3),
        fill='tozeroy', fillcolor='rgba(235,87,87,0.1)', marker=dict(size=6, color='#EB5757'), hovertemplate='T%{x}h → Level %{y}<extra></extra>'))
    fig.update_layout(BASE_LAYOUT, height=250, margin=dict(l=35,r=5,t=20,b=35), showlegend=False,
                      xaxis=dict(showgrid=True, gridcolor='#060D1E', color='#FFFFFF', tickfont=dict(size=12)), yaxis=dict(showgrid=True, gridcolor='#060D1E', color='#FFFFFF', tickfont=dict(size=12)))
    return fig

def home_cls_bar():
    cc = DF['cls'].value_counts()
    cols = [CLS_COLOR.get(c, '#9CA3AF') for c in cc.index]
    fig = go.Figure(go.Bar(
        x=cc.index.str.upper(), y=cc.values,
        marker=dict(color=cols, line=dict(color='#050B18', width=1)),
        text=cc.values, textposition='outside', textfont=dict(size=14, color='white', family='Share Tech Mono'),
        hovertemplate='<b>%{x}</b><br>%{y} objects<extra></extra>'
    ))
    fig.update_layout(BASE_LAYOUT, height=250, margin=dict(l=25,r=5,t=20,b=35), showlegend=False,
                      xaxis=dict(showgrid=False, color='#FFFFFF', tickfont=dict(size=12)), yaxis=dict(showgrid=True, gridcolor='#060D1E', color='#FFFFFF', tickfont=dict(size=12)))
    return fig

def render_home():
    st.markdown("""
    <div style='text-align:center;padding:10px 0 20px'>
        <div style='font-family:Rajdhani,sans-serif;font-size:36px;color:#00E5FF; letter-spacing:10px;font-weight:700;text-shadow:0 0 20px #00E5FF60'>
            ⚡ SPACE OPERATIONS COMMAND ⚡
        </div>
        <div style='font-family:Share Tech Mono,monospace;font-size:14px; color:#56CCF2;letter-spacing:5px;margin-top:5px'>
            SPACE OPERATIONAL PICTURE · REAL-TIME · v4.2
        </div>
    </div>""", unsafe_allow_html=True)

    cols = st.columns(6)
    tiles = [
        ('🛰️ TRACKED',   '847',  '+12 24H',       '#56CCF2'),
        ('🔴 ADVERSARY', '127',  '8 ACTIVE',       '#EB5757'),
        ('⚠️ HIGH RISK',  '23',  'CONJUNCTIONS',   '#F2C94C'),
        ('🔵 FRIENDLY',  '312',  'NOMINAL',         '#27AE60'),
        ('❓ UNKNOWN',   '408',  'MONITORING',      '#9CA3AF'),
        ('🗑️ DEBRIS',    '2847', 'CATALOGUED',      '#AAB8C2'),
    ]
    for col, (lbl, v, sub, c) in zip(cols, tiles):
        col.markdown(tile(lbl, v, sub, c), unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)

    col_earth, col_right = st.columns([2.6, 1])
    with col_earth:
        sec('ANIMATED 3D ORBITAL PICTURE — HOVER OBJECTS FOR FULL INFO')
        st.plotly_chart(home_3d(), use_container_width=True)

    with col_right:
        sec('ACTIVE ALERTS')
        alerts = [
            ('🔴 CRITICAL', 'SAT-40023 CHN-ISR', 'TCA: 14:23 UTC | Miss: 142 m', '#EB5757'),
            ('🔴 CRITICAL', 'SAT-40051 RUS-RECON', 'Manoeuvre | Δv: 2.3 m/s', '#EB5757'),
            ('🟡 WARNING',  'SAT-40089 UNKNOWN', 'Proximity ops | Range: 890 m', '#F2C94C'),
            ('🟡 WARNING',  'SAT-40012 CHN-SIGINT', 'Orbit deviation | +0.8 m/s', '#F2C94C'),
            ('🟡 WARNING',  'CLUSTER ALPHA-3', 'Coordinated behaviour × 3', '#F2C94C'),
            ('🔵 INFO',     'GEO-ZONE-2', 'Congestion ↑15%', '#56CCF2'),
        ]
        for level, title, detail, c in alerts:
            st.markdown(f"""<div style='background:{c}15;border-left:4px solid {c}; padding:10px 12px;margin:6px 0;border-radius:0 4px 4px 0'>
                <div style='font-family:Share Tech Mono,monospace;font-size:12px; color:{c};font-weight:bold'>{level} — {title}</div>
                <div style='font-family:Share Tech Mono,monospace;font-size:11px; color:#E6EDF3;margin-top:3px'>{detail}</div>
            </div>""", unsafe_allow_html=True)

        sec('SYSTEM STATUS')
        for sys, stat, c in [('TRACKING NET', 'OPERATIONAL', '#27AE60'),('SENSOR FUSION', 'OPERATIONAL', '#27AE60'),('THREAT ENGINE', 'OPERATIONAL', '#27AE60'),('COMMS UPLINK', 'DEGRADED', '#F2C94C'),('DATA LATENCY', '2.3 s', '#27AE60'),('COVERAGE', '94.7%', '#27AE60')]:
            st.markdown(f"""<div style='display:flex;justify-content:space-between; padding:6px 0;border-bottom:1px solid #060D1E; font-family:Share Tech Mono,monospace;font-size:12px;'>
                <span style='color:#AAB8C2'>{sys}</span>
                <span style='color:{c};font-weight:bold'>{stat}</span>
            </div>""", unsafe_allow_html=True)

        sec('UTC CLOCK')
        now = datetime.utcnow()
        st.markdown(f"""<div style='font-family:Share Tech Mono,monospace;text-align:center; background:#06111E;padding:15px;border:1px solid #0E2040;border-radius:4px'>
            <div style='font-size:14px;color:#56CCF2'>{now.strftime('%Y-%m-%d')}</div>
            <div style='font-size:28px;color:#FFFFFF;font-weight:bold;'>{now.strftime('%H:%M:%S')} UTC</div>
            <div style='font-size:11px;color:#8AAED0'>J2000 EPOCH</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        sec('ORBIT DISTRIBUTION')
        st.plotly_chart(home_donut(), use_container_width=True)
    with c2:
        sec('THREAT LEVEL — 24H TIMELINE')
        st.plotly_chart(home_threat_line(), use_container_width=True)
    with c3:
        sec('CLASSIFICATION BREAKDOWN')
        st.plotly_chart(home_cls_bar(), use_container_width=True)

# ─────────────────────────────────────────────────────────────
# TAB 1 — OBJECT CLASSIFICATION
# ─────────────────────────────────────────────────────────────
def cls_3d(fdf):
    traces = [earth_surface(), atmo_sphere()]
    t = np.linspace(0, 2*np.pi, 300)
    geo_r = R_E + alt2r(35786)
    traces.append(go.Scatter3d(x=geo_r*np.cos(t), y=geo_r*np.sin(t), z=np.zeros(300), mode='lines', line=dict(color='#F2C94C', width=1, dash='dot'), opacity=0.25, showlegend=True, name='GEO Belt', hoverinfo='skip'))
    leo_r = R_E + alt2r(2000)
    traces.append(go.Scatter3d(x=leo_r*np.cos(t), y=leo_r*np.sin(t), z=np.zeros(300), mode='lines', line=dict(color='#2F80ED', width=1, dash='dot'), opacity=0.15, showlegend=True, name='LEO Boundary', hoverinfo='skip'))

    for cls in ['friendly', 'adversary', 'unknown']:
        sub = fdf[fdf['cls'] == cls]
        if sub.empty: continue
        col = CLS_COLOR[cls]
        xs, ys, zs, ht, szs = [], [], [], [], []
        for _, s in sub.iterrows():
            x, y, z = orbit_pos(s.altitude_km, s.inclination, s.raan, s.true_anom)
            xs.append(x); ys.append(y); zs.append(z)
            szs.append(5 + s.threat_score * 6)
            ht.append(f"<b>{s['id']}</b><br>{s['flag']} {s['fullname']}<br>Orbit: {s['orbit_type']} | Alt: {s.altitude_km:,.0f} km")
        sym = 'diamond' if cls == 'adversary' else 'square' if cls == 'unknown' else 'circle'
        traces.append(go.Scatter3d(x=xs, y=ys, z=zs, mode='markers', marker=dict(size=szs, color=col, opacity=0.88, symbol=sym, line=dict(width=1, color='white')), name=cls.upper(), text=ht, hovertemplate='%{text}<extra></extra>'))

    fig = go.Figure(data=traces)
    fig.update_layout(BASE_LAYOUT, height=600, scene=SCENE, title=dict(text='OBJECT CLASSIFICATION — 3D ORBITAL VIEW (ECI)', font=dict(size=14, color='#00E5FF'), x=0.5))
    return fig

def telemetry_spark(sat):
    t = np.linspace(0, 24, 120)
    alt_v = sat.altitude_km + np.cumsum(np.random.normal(0, 0.3, 120))
    vel_v = sat.velocity_kms + np.cumsum(np.random.normal(0, 0.001, 120))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=alt_v, mode='lines', name='Alt (km)', line=dict(color='#56CCF2', width=2), fill='tozeroy', fillcolor='rgba(47,128,237,0.1)'))
    fig.add_trace(go.Scatter(x=t, y=vel_v * 100, mode='lines', name='Vel×100', line=dict(color='#27AE60', width=2), yaxis='y2'))
    fig.update_layout(BASE_LAYOUT, height=180, margin=dict(l=40, r=40, t=10, b=30), showlegend=True,
        legend=dict(font=dict(size=11, color='#FFFFFF'), x=0, y=1.2, orientation='h'),
        xaxis=dict(showgrid=False, color='#FFFFFF', tickfont=dict(size=11)),
        yaxis=dict(showgrid=True, gridcolor='#060D1E', color='#56CCF2', tickfont=dict(size=11)),
        yaxis2=dict(overlaying='y', side='right', color='#27AE60', tickfont=dict(size=11)))
    return fig

def render_classification():
    st.markdown("""<div style='font-family:Rajdhani,sans-serif;font-size:24px;color:#56CCF2; letter-spacing:5px;font-weight:600;border-bottom:1px solid #0E2040; padding-bottom:10px;margin-bottom:18px'>
        🛰️ OBJECT CLASSIFICATION DASHBOARD</div>""", unsafe_allow_html=True)

    col_f, col_m, col_d = st.columns([1, 2.4, 1.4])

    with col_f:
        sec('FILTERS')
        orb_f  = st.multiselect('ORBIT TYPE', ['LEO','MEO','GEO','HEO'], default=['LEO','MEO','GEO','HEO'], key='c_orb')
        cls_f  = st.multiselect('CLASSIFICATION', ['friendly','adversary','unknown'], default=['friendly','adversary','unknown'], key='c_cls')
        stat_f = st.multiselect('STATUS', ['OPERATIONAL','DEGRADED','UNKNOWN'], default=['OPERATIONAL','DEGRADED','UNKNOWN'], key='c_sta')
        alt_r  = st.slider('ALTITUDE (km)', 200, 40000, (200, 40000), step=200, key='c_alt')

        mask = (DF['orbit_type'].isin(orb_f) & DF['cls'].isin(cls_f) & DF['status'].isin(stat_f) & (DF['altitude_km'] >= alt_r[0]) & (DF['altitude_km'] <= alt_r[1]))
        filtered = DF[mask]

        sec(f'OBJECT LIST  [{len(filtered)}/{len(DF)}]')
        for _, s in filtered.head(22).iterrows():
            c = CLS_COLOR[s['cls']]
            st.markdown(f"""<div style='background:{c}15;border-left:3px solid {c}; padding:6px 10px;margin:4px 0;border-radius:0 3px 3px 0'>
                <span style='color:{c};font-size:12px;font-weight:bold'>{s['id']}</span>
                <span style='color:#E6EDF3;font-size:11px'> {s['flag']} {s['orbit_type']}</span><br>
                <span style='color:#8AAED0;font-size:10px'>{s.altitude_km:.0f}km · {s.velocity_kms:.2f}km/s · {s.status}</span>
            </div>""", unsafe_allow_html=True)

    with col_m:
        sec('3D ORBITAL VISUALIZATION')
        st.plotly_chart(cls_3d(filtered), use_container_width=True)

        sec('TIMELINE SCRUBBER — ORBITAL PROPAGATION')
        toff = st.slider('TIME OFFSET (min)', -180, 180, 0, step=5, key='c_time')
        c1, c2, c3 = st.columns(3)
        for col, lbl, val, c in [
            (c1, 'EPOCH', (datetime.utcnow()+timedelta(minutes=toff)).strftime('%H:%M UTC'), '#00E5FF'),
            (c2, 'PROPAGATOR', 'SGP4', '#27AE60'),
            (c3, 'FRAME', 'ECI J2000', '#F2C94C'),
        ]:
            col.markdown(f"""<div style='background:#06111E;border:1px solid #0E2040; border-radius:4px;padding:10px;text-align:center; font-family:Share Tech Mono,monospace;font-size:12px;'>
                <span style='color:#8AAED0'>{lbl}</span><br><span style='color:{c};font-weight:bold;font-size:16px;'>{val}</span>
            </div>""", unsafe_allow_html=True)

    with col_d:
        sec('OBJECT DETAILS')
        ids = filtered['id'].tolist()
        if ids:
            sel_id = st.selectbox('SELECT OBJECT', ids, key='c_sel')
            s = filtered[filtered['id'] == sel_id].iloc[0]
            c = CLS_COLOR[s['cls']]
            ts_color = '#EB5757' if s.threat_score > 0.7 else '#F2C94C' if s.threat_score > 0.4 else '#27AE60'
            kvs = ''.join([
                kv('COUNTRY',   f"{s['flag']} {s['fullname']}"), kv('NORAD ID',  str(s.norad)), kv('TYPE',      s.sat_type),
                kv('CLASS',     s['cls'].upper(), c), kv('ORBIT',     s.orbit_type), kv('STATUS',    s.status),
                kv('ALTITUDE',  f"{s.altitude_km:,.1f} km"), kv('VELOCITY',  f"{s.velocity_kms:.3f} km/s"),
                kv('INCL',      f"{s.inclination}°"), kv('RAAN',      f"{s.raan}°"), kv('TRUE ANOM', f"{s.true_anom}°"),
                kv('LAT/LON',   f"{s.latitude}° / {s.longitude}°"), kv('THREAT',    f"{s.threat_score:.4f}", ts_color), kv('LAST MAN',  s.last_maneuver or 'NONE'),
            ])
            st.markdown(f"""<div style='background:{c}10;border:1px solid {c}50; border-radius:6px;padding:16px'>
                <div style='color:{c};font-size:18px;font-weight:bold'>{s['id']}</div>
                <div style='color:#E6EDF3;font-size:12px;margin-bottom:12px'>{s['name']}</div>
                {kvs} {bar(s.threat_score*100, ts_color)}
            </div>""", unsafe_allow_html=True)

            sec('TELEMETRY — 24H')
            st.plotly_chart(telemetry_spark(s), use_container_width=True)

# ─────────────────────────────────────────────────────────────
# TAB 2 — PROXIMITY ALERTS
# ─────────────────────────────────────────────────────────────
@st.cache_data
def gen_conjunctions(n=24):
    events = []
    ids = DF['id'].tolist()
    for _ in range(n):
        o1, o2 = random.sample(ids, 2)
        prob = float(np.random.exponential(0.012))
        prob = min(prob, 0.28)
        md = max(50.0, float(np.random.exponential(600)))
        hours = float(np.random.uniform(0.5, 72))
        events.append({'obj1':o1, 'obj2':o2, 'prob':prob, 'miss_dist':md, 'rel_v':float(np.random.uniform(0.5,14)), 'tca_hours':hours, 'tca':(datetime.utcnow()+timedelta(hours=hours)).strftime('%H:%M UTC')})
    return sorted(events, key=lambda x: x['prob'], reverse=True)

def conj_3d():
    traces = [earth_surface(), atmo_sphere()]
    for cls in ['friendly','adversary','unknown']:
        sub = DF[DF['cls']==cls].sample(frac=0.6, random_state=2)
        col = CLS_COLOR[cls]
        xs, ys, zs = [], [], []
        for _, s in sub.iterrows():
            x,y,z = orbit_pos(s.altitude_km, s.inclination, s.raan, s.true_anom)
            xs.append(x); ys.append(y); zs.append(z)
        traces.append(go.Scatter3d(x=xs,y=ys,z=zs, mode='markers', marker=dict(size=3,color=col,opacity=0.5), name=cls.upper(), hoverinfo='skip'))

    pairs = [(DF.iloc[5], DF.iloc[22]), (DF.iloc[11], DF.iloc[40]), (DF.iloc[7], DF.iloc[62])]
    rcols = ['#EB5757','#EB5757','#F2C94C']
    for (s1,s2), rc in zip(pairs, rcols):
        x1,y1,z1 = orbit_pos(s1.altitude_km, s1.inclination, s1.raan, s1.true_anom)
        x2,y2,z2 = orbit_pos(s2.altitude_km, s2.inclination, s2.raan, s2.true_anom)
        traces.append(go.Scatter3d(x=[x1,x2], y=[y1,y2], z=[z1,z2], mode='lines', line=dict(color=rc, width=4, dash='dash'), opacity=0.9, showlegend=False, hoverinfo='skip'))
        for xi,yi,zi,s in [(x1,y1,z1,s1),(x2,y2,z2,s2)]:
            traces.append(go.Scatter3d(x=[xi],y=[yi],z=[zi], mode='markers', marker=dict(size=14, color=rc, opacity=1.0, line=dict(width=2, color='white')), showlegend=False, hovertemplate=f"<b>{s['id']}</b><br>{s.altitude_km:.0f} km<extra></extra>"))
            u=np.linspace(0,2*np.pi,20); v=np.linspace(0,np.pi,20); U,V=np.meshgrid(u,v); sc=0.04
            traces.append(go.Surface(x=xi+sc*np.cos(U)*np.sin(V), y=yi+sc*np.sin(U)*np.sin(V), z=zi+sc*0.4*np.cos(V), colorscale=[[0,rc],[1,rc]], showscale=False, opacity=0.14, hoverinfo='skip', showlegend=False))

    fig = go.Figure(data=traces)
    fig.update_layout(BASE_LAYOUT, height=600, scene=SCENE, title=dict(text='CONJUNCTION VISUALIZATION — HIGHLIGHTED PAIRS', font=dict(size=14,color='#FFFFFF'), x=0.5))
    return fig

def collision_heatmap():
    alts = np.linspace(200, 40000, 70)
    incs = np.linspace(0, 100, 60)
    Z = np.zeros((60,70))
    for j,inc in enumerate(incs):
        for i,alt in enumerate(alts):
            Z[j,i] += 0.8*np.exp(-((inc-51.6)**2/300+(alt-420)**2/8000))
            Z[j,i] += 0.9*np.exp(-((inc-98)**2/100+(alt-600)**2/3000))
            Z[j,i] += 0.5*np.exp(-((inc-53)**2/500+(alt-550)**2/5000))
            if 35000<=alt<=36500: Z[j,i] += 0.4*np.exp(-((inc-0)**2/30))
    Z += np.abs(np.random.normal(0,0.03,(60,70)))
    Z = np.clip(Z,0,1)

    fig = go.Figure(go.Heatmap(x=alts, y=incs, z=Z, colorscale=[[0.0,'#020810'],[0.15,'#051830'],[0.35,'#0A2D5E'],[0.55,'#1565C0'],[0.72,'#F2C94C'],[0.88,'#EB5757'],[1.0,'#FF2020']], colorbar=dict(title=dict(text='Risk Density', font=dict(size=12,color='#FFFFFF',family='Share Tech Mono')), tickfont=dict(size=11, color='#FFFFFF')), hovertemplate='Alt: %{x:.0f} km<br>Inc: %{y:.0f}°<br>Density: %{z:.3f}<extra></extra>'))
    for x_ann, y_ann, label in [(420, 51.6, 'ISS ORBIT'), (600, 98, 'SUN-SYNC'), (550, 53, 'STARLINK'), (35786, 0, 'GEO BELT')]:
        fig.add_annotation(x=x_ann, y=y_ann, text=label, font=dict(color='#000000', size=12, family='Share Tech Mono', weight='bold'), bgcolor='#F2C94C', bordercolor='#FFFFFF', showarrow=True, arrowcolor='#FFFFFF', arrowsize=1)
    fig.update_layout(BASE_LAYOUT, height=600, xaxis=dict(title=dict(text='ALTITUDE (km)',font=dict(size=13,color='#FFFFFF',family='Share Tech Mono')), color='#FFFFFF', tickfont=dict(size=12), type='log', showgrid=False), yaxis=dict(title=dict(text='INCLINATION (°)',font=dict(size=13,color='#FFFFFF',family='Share Tech Mono')), color='#FFFFFF', tickfont=dict(size=12), showgrid=False), title=dict(text='COLLISION PROBABILITY DENSITY', font=dict(size=14,color='#FFFFFF'), x=0.5))
    return fig

def miss_dist_chart(conjs):
    dists = [c['miss_dist'] for c in conjs]
    probs = [c['prob'] for c in conjs]
    labels = [c['obj1'][-5:] for c in conjs]
    cols = ['#EB5757' if p>0.05 else '#F2C94C' if p>0.01 else '#27AE60' for p in probs]
    fig = go.Figure(go.Bar(x=labels, y=dists, marker=dict(color=cols, line=dict(color='#050B18',width=1)), text=[f"{d:.0f}m" for d in dists], textposition='outside', textfont=dict(size=11,color='white'), hovertemplate='%{x}<br>Miss: %{y:.0f} m<extra></extra>'))
    fig.add_hline(y=1000, line_dash='dash', line_color='#EB5757', line_width=2, annotation_text='1 km THRESHOLD', annotation_font=dict(size=12,color='#EB5757',family='Share Tech Mono'))
    fig.update_layout(BASE_LAYOUT, height=300, margin=dict(l=40,r=5,t=20,b=50), showlegend=False, xaxis=dict(showgrid=False,color='#FFFFFF',tickfont=dict(size=11),tickangle=45), yaxis=dict(showgrid=True,gridcolor='#060D1E',color='#FFFFFF',tickfont=dict(size=11), title=dict(text='Miss Dist (m)',font=dict(size=12))))
    return fig

def tca_scatter(conjs):
    hrs = [c['tca_hours'] for c in conjs]
    probs = [c['prob'] for c in conjs]
    cols = ['#EB5757' if p>0.05 else '#F2C94C' if p>0.01 else '#27AE60' for p in probs]
    szs = [10+p*120 for p in probs]
    fig = go.Figure(go.Scatter(x=hrs, y=probs, mode='markers', marker=dict(size=szs, color=cols, opacity=0.8, line=dict(width=1,color='white')), hovertemplate='TCA in %{x:.1f}h<br>Prob: %{y:.4f}<extra></extra>'))
    fig.add_hline(y=0.05, line_dash='dash', line_color='#EB5757', line_width=2, annotation_text='HIGH RISK', annotation_font=dict(size=12,color='#EB5757',family='Share Tech Mono'))
    fig.add_hline(y=0.01, line_dash='dot', line_color='#F2C94C', line_width=2, annotation_text='WARNING', annotation_font=dict(size=12,color='#F2C94C',family='Share Tech Mono'))
    fig.update_layout(BASE_LAYOUT, height=300, margin=dict(l=50,r=5,t=20,b=40), showlegend=False, xaxis=dict(showgrid=True,gridcolor='#060D1E',color='#FFFFFF',tickfont=dict(size=11), title=dict(text='Hours to TCA',font=dict(size=12))), yaxis=dict(showgrid=True,gridcolor='#060D1E',color='#FFFFFF',tickfont=dict(size=11), type='log', title=dict(text='Collision Prob',font=dict(size=12))))
    return fig

def render_proximity():
    st.markdown("""<div style='font-family:Rajdhani,sans-serif;font-size:24px;color:#EB5757; letter-spacing:5px;font-weight:600;border-bottom:1px solid #0E2040; padding-bottom:10px;margin-bottom:18px'>
        ⚠️ PROXIMITY ALERTS & COLLISION RISK DASHBOARD</div>""", unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    for col, (lbl,val,c) in zip([c1,c2,c3,c4],[('ACTIVE ALERTS','47','#EB5757'),('HIGH RISK >10%','6','#EB5757'),('WARNING 1-10%','18','#F2C94C'),('MONITORING <1%','23','#27AE60')]):
        col.markdown(tile(lbl, val, '⚡ REAL-TIME', c), unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)
    col_viz, col_alerts = st.columns([2.2, 1])

    with col_viz:
        v1, v2 = st.tabs(['3D CONJUNCTION VIEW', '2D RISK HEATMAP'])
        with v1: st.plotly_chart(conj_3d(), use_container_width=True)
        with v2: st.plotly_chart(collision_heatmap(), use_container_width=True)

    conjs = gen_conjunctions()
    with col_alerts:
        sec('RANKED BY COLLISION PROBABILITY')
        for conj in conjs[:12]:
            rc = '#EB5757' if conj['prob']>0.05 else '#F2C94C' if conj['prob']>0.01 else '#27AE60'
            flash = '⚡ ' if conj['prob']>0.05 else ''
            st.markdown(f"""<div style='background:{rc}15;border:1px solid {rc}40; border-radius:5px;padding:12px;margin:6px 0'>
                <div style='display:flex;justify-content:space-between'>
                    <span style='color:{rc};font-size:12px;font-weight:bold'>{flash}{conj['obj1'][-8:]}</span>
                    <span style='color:{rc};font-size:14px;font-weight:bold'>{conj['prob']*100:.2f}%</span>
                </div>
                <div style='color:#FFFFFF;font-size:11px'>× {conj['obj2'][-8:]}</div>
                <div style='display:flex;justify-content:space-between; color:#AAB8C2;font-size:10px;margin-top:6px'>
                    <span>TCA: {conj['tca']}</span><span>Miss: {conj['miss_dist']:.0f} m</span>
                </div>
                <div style='color:#AAB8C2;font-size:10px'>Rel V: {conj['rel_v']:.1f} km/s</div>
                {bar(min(conj['prob']*1000,100), rc)}
            </div>""", unsafe_allow_html=True)

    st.markdown('<br>', unsafe_allow_html=True)
    bc1, bc2 = st.columns(2)
    with bc1: st.plotly_chart(miss_dist_chart(conjs), use_container_width=True)
    with bc2: st.plotly_chart(tca_scatter(conjs), use_container_width=True)

# ─────────────────────────────────────────────────────────────
# TAB 3 — SDIZ (RESTORED 6 FULL ZONES)
# ─────────────────────────────────────────────────────────────
# RESTORED: All 6 SDIZ Zones, including HEO and XGEO
ZONES = [
    {'name':'SDIZ-1 LEO-LOW',  'range':'200–600 km',   'alt':(200,600),    'col':'#EB5757','obj':312,'risk':0.72,'act':'HIGH'},
    {'name':'SDIZ-2 LEO-HIGH', 'range':'600–2000 km',  'alt':(600,2000),   'col':'#F2C94C','obj':187,'risk':0.55,'act':'MED'},
    {'name':'SDIZ-3 MEO',      'range':'2K–20K km',    'alt':(2000,20000), 'col':'#27AE60','obj':94, 'risk':0.30,'act':'LOW'},
    {'name':'SDIZ-4 GEO',      'range':'35.7–36K km',  'alt':(35000,36500),'col':'#2F80ED','obj':167,'risk':0.44,'act':'MED'},
    {'name':'SDIZ-5 HEO',      'range':'2K–50K km',    'alt':(500,50000),  'col':'#9B59B6','obj':43, 'risk':0.21,'act':'LOW'},
    {'name':'SDIZ-6 XGEO',     'range':'>36K km',      'alt':(36500,60000),'col':'#34495E','obj':12, 'risk':0.14,'act':'MIN'},
]

def sdiz_3d():
    traces = [earth_surface(), atmo_sphere()]
    u=np.linspace(0,2*np.pi,40); v=np.linspace(0,np.pi,40); U,V=np.meshgrid(u,v)
    for zone in ZONES[:4]: # Only render first 4 shells for performance visibility
        R_shell = R_E + alt2r(zone['alt'][1])
        traces.append(go.Surface(x=R_shell*np.cos(U)*np.sin(V), y=R_shell*np.sin(U)*np.sin(V), z=R_shell*np.cos(V), colorscale=[[0,zone['col']],[1,zone['col']]], showscale=False, opacity=0.08, hoverinfo='skip', name=zone['name'], showlegend=True))
    for cls in ['friendly','adversary','unknown']:
        sub = DF[DF['cls']==cls]
        col = CLS_COLOR[cls]
        xs,ys,zs,ht=[],[],[],[]
        for _,s in sub.iterrows():
            x,y,z=orbit_pos(s.altitude_km,s.inclination,s.raan,s.true_anom)
            xs.append(x);ys.append(y);zs.append(z)
            ht.append(f"<b>{s['id']}</b><br>{s['flag']} {s['country']}<br>{s.orbit_type}<br>{s.altitude_km:.0f} km")
        traces.append(go.Scatter3d(x=xs,y=ys,z=zs,mode='markers', marker=dict(size=4,color=col,opacity=0.8), name=cls.upper(), text=ht, hovertemplate='%{text}<extra></extra>'))
    
    iss_pts = [orbit_pos(420, 51.6+random.uniform(-2,2), random.uniform(0,360), random.uniform(0,360)) for _ in range(12)]
    traces.append(go.Scatter3d(x=[p[0] for p in iss_pts], y=[p[1] for p in iss_pts], z=[p[2] for p in iss_pts], mode='markers', marker=dict(size=10, color='#FF6600', opacity=0.9, symbol='diamond', line=dict(width=2, color='#FFFFFF')), name='CP-ALPHA (ISS)', hovertemplate='CHOKE POINT ALPHA<br>ISS Vicinity ~420 km<extra></extra>'))
    g_ang = np.linspace(np.radians(100), np.radians(135), 25)
    geo_r = R_E + alt2r(35786)
    traces.append(go.Scatter3d(x=[geo_r*math.cos(a) for a in g_ang], y=[geo_r*math.sin(a) for a in g_ang], z=[random.uniform(-0.015,0.015) for _ in g_ang], mode='markers+lines', marker=dict(size=6, color='#F2C94C', opacity=0.9), line=dict(color='#F2C94C', width=4), name='CP-GAMMA (GEO Arc)', hovertemplate='CHOKE POINT GAMMA<br>GEO Arc 100–135°E<extra></extra>'))
    
    fig = go.Figure(data=traces)
    fig.update_layout(BASE_LAYOUT, height=600, scene=SCENE, title=dict(text='SPACE DEFENSE IDENTIFICATION ZONES — SDIZ OVERLAY', font=dict(size=14,color='#FFFFFF'), x=0.5))
    return fig

def density_heat():
    alts = np.linspace(200, 40000, 80)
    raans = np.linspace(0, 360, 72)
    Z = np.zeros((72,80))
    for _,s in DF.iterrows():
        ai = min(int((s.altitude_km-200)/(40000-200)*80),79)
        ri = min(int(s.raan/360*72),71)
        Z[ri,ai] += 2
    Z += np.random.uniform(0,0.2,(72,80))
    fig = go.Figure(go.Heatmap(x=alts, y=raans, z=Z, colorscale=[[0,'#020810'],[0.1,'#051830'],[0.3,'#083D6E'],[0.55,'#1565C0'],[0.72,'#F2C94C'],[0.9,'#EB5757'],[1.0,'#FF2020']], colorbar=dict(title=dict(text='Object Density',font=dict(size=12,color='#FFFFFF')), tickfont=dict(size=11,color='#FFFFFF')), hovertemplate='Alt: %{x:.0f} km<br>RAAN: %{y:.0f}°<br>Density: %{z:.2f}<extra></extra>'))
    fig.update_layout(BASE_LAYOUT, height=600, xaxis=dict(title=dict(text='ALTITUDE (km)',font=dict(size=13,color='#FFFFFF')), type='log', color='#FFFFFF', tickfont=dict(size=12), showgrid=False), yaxis=dict(title=dict(text='RAAN (°)',font=dict(size=13,color='#FFFFFF')), color='#FFFFFF', tickfont=dict(size=12), showgrid=False), title=dict(text='OBJECT DENSITY', font=dict(size=14,color='#FFFFFF'), x=0.5))
    return fig

def traffic_flow():
    fig = go.Figure()
    for cls in ['friendly','adversary','unknown']:
        sub = DF[DF['cls']==cls]
        fig.add_trace(go.Scatter(x=sub.altitude_km, y=sub.inclination, mode='markers', marker=dict(size=6+sub.threat_score*10, color=CLS_COLOR[cls], opacity=0.8, line=dict(width=1,color='white')), name=cls.upper(), text=sub['id'], hovertemplate='<b>%{text}</b><br>Alt: %{x:.0f} km<br>Inc: %{y:.1f}°<extra></extra>'))
    for alt, inc, lbl, c in [(420, 51.6, 'ISS', '#27AE60'), (550, 97.6, 'SUN-SYNC', '#F2C94C'), (20200,55.0, 'GPS', '#2F80ED'), (35786, 0.0, 'GEO BELT', '#9B59B6')]:
        fig.add_annotation(x=alt, y=inc, text=lbl, font=dict(size=12,color='#000000',family='Share Tech Mono', weight='bold'), bgcolor=c, bordercolor=c, showarrow=True, arrowcolor=c, arrowsize=1, arrowwidth=2)
    fig.update_layout(BASE_LAYOUT, height=600, xaxis=dict(title=dict(text='ALTITUDE (km)',font=dict(size=13,color='#FFFFFF')), color='#FFFFFF', tickfont=dict(size=12), type='log', showgrid=True, gridcolor='#06111E'), yaxis=dict(title=dict(text='INCLINATION (°)',font=dict(size=13,color='#FFFFFF')), color='#FFFFFF', tickfont=dict(size=12), showgrid=True, gridcolor='#06111E'), title=dict(text='ORBITAL TRAFFIC FLOW', font=dict(size=14,color='#FFFFFF'), x=0.5))
    return fig

def render_sdiz():
    st.markdown("""<div style='font-family:Rajdhani,sans-serif;font-size:24px;color:#F2C94C; letter-spacing:5px;font-weight:600;border-bottom:1px solid #0E2040; padding-bottom:10px;margin-bottom:18px'>
        🛡️ SDIZ & CHOKE POINT VISUALIZATION</div>""", unsafe_allow_html=True)

    col_m, col_s = st.columns([2.5, 1])
    with col_m:
        t1,t2,t3 = st.tabs(['3D SDIZ VIEW','DENSITY HEATMAP','TRAFFIC FLOW'])
        with t1: st.plotly_chart(sdiz_3d(), use_container_width=True)
        with t2: st.plotly_chart(density_heat(), use_container_width=True)
        with t3: st.plotly_chart(traffic_flow(), use_container_width=True)

    with col_s:
        sec('ZONE STATISTICS')
        for z in ZONES:
            c = z['col']
            st.markdown(f"""<div style='background:{c}15;border:1px solid {c}50; border-radius:5px;padding:14px;margin:8px 0'>
                <div style='color:{c};font-size:12px;font-weight:bold'>{z['name']}</div>
                <div style='color:#FFFFFF;font-size:11px'>{z['range']}</div>
                <div style='display:flex;justify-content:space-between;margin-top:10px'>
                    <div style='text-align:center'>
                        <div style='color:#FFFFFF;font-size:16px;font-weight:bold'>{z['obj']}</div>
                        <div style='color:#AAB8C2;font-size:9px'>OBJECTS</div>
                    </div>
                    <div style='text-align:center'>
                        <div style='color:{c};font-size:16px;font-weight:bold'>{z['risk']:.2f}</div>
                        <div style='color:#AAB8C2;font-size:9px'>RISK</div>
                    </div>
                    <div style='text-align:center'>
                        <div style='color:{c};font-size:14px;font-weight:bold'>{z['act']}</div>
                        <div style='color:#AAB8C2;font-size:9px'>ACTIVITY</div>
                    </div>
                </div>
                {bar(z['risk']*100, c)}
            </div>""", unsafe_allow_html=True)

        sec('CHOKE POINTS')
        for cp,desc,lvl,c in [('CP-ALPHA','ISS Vicinity ~420 km','CRITICAL','#EB5757'), ('CP-BETA', 'Sun-Sync Belt 98°',  'HIGH',    '#EB5757'), ('CP-GAMMA','GEO Arc 105–130°E',  'HIGH',    '#F2C94C'), ('CP-DELTA','GNSS Shell ~20K km', 'MED',     '#F2C94C')]:
            st.markdown(f"""<div style='background:{c}15;border-left:4px solid {c}; padding:10px 12px;margin:6px 0;border-radius:0 4px 4px 0'>
                <div style='color:{c};font-size:12px;font-weight:bold'>{cp} — {lvl}</div>
                <div style='color:#FFFFFF;font-size:11px'>{desc}</div>
            </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# TAB 4 — SAW THREAT (RESTORED CLUSTER ANALYSIS)
# ─────────────────────────────────────────────────────────────
def saw_3d():
    traces = [earth_surface(), atmo_sphere()]
    for cls in ['friendly','unknown']:
        sub = DF[DF['cls']==cls]
        col = CLS_COLOR[cls]
        xs,ys,zs=[],[],[]
        for _,s in sub.iterrows():
            x,y,z=orbit_pos(s.altitude_km,s.inclination,s.raan,s.true_anom)
            xs.append(x);ys.append(y);zs.append(z)
        traces.append(go.Scatter3d(x=xs,y=ys,z=zs,mode='markers', marker=dict(size=3,color=col,opacity=0.35), name=cls.upper(), hoverinfo='skip'))

    adv = DF[DF['cls']=='adversary']
    for _,s in adv.iterrows():
        x,y,z=orbit_pos(s.altitude_km,s.inclination,s.raan,s.true_anom)
        ts = s.threat_score
        c  = '#EB5757' if ts>0.7 else '#FF8C00' if ts>0.4 else '#F2C94C'
        sz = 8+ts*10
        traces.append(go.Scatter3d(x=[x],y=[y],z=[z], mode='markers', marker=dict(size=sz,color=c,opacity=0.9, symbol='diamond' if ts>0.7 else 'circle', line=dict(width=2,color='white')), showlegend=False, hovertemplate=(f"<b>{s['id']}</b><br>{s['flag']} {s['fullname']}<br>Threat: {ts:.4f}<br>Alt: {s.altitude_km:.0f} km<extra></extra>")))
        if ts > 0.45:
            u=np.linspace(0,2*np.pi,12);v=np.linspace(0,np.pi,12); U,V=np.meshgrid(u,v); hr=0.03+ts*0.05
            traces.append(go.Surface(x=x+hr*np.cos(U)*np.sin(V), y=y+hr*np.sin(U)*np.sin(V), z=z+hr*np.cos(V), colorscale=[[0,c],[1,c]], showscale=False, opacity=0.15, hoverinfo='skip', showlegend=False))
        if s.last_maneuver:
            vx,vy,vz = random.uniform(-1,1),random.uniform(-1,1),random.uniform(-0.4,0.4)
            norm = math.sqrt(vx**2+vy**2+vz**2); sc = 0.2
            traces.append(go.Scatter3d(x=[x,x+vx/norm*sc], y=[y,y+vy/norm*sc], z=[z,z+vz/norm*sc], mode='lines', line=dict(color='#EB5757',width=4), opacity=0.9, showlegend=False, hoverinfo='skip'))

    fig = go.Figure(data=traces)
    fig.update_layout(BASE_LAYOUT, height=600, scene=SCENE, title=dict(text='SAW THREAT OVERLAY', font=dict(size=14,color='#EB5757'), x=0.5))
    return fig

def maneuver_chart():
    t = np.linspace(-48, 0, 200)
    fig = go.Figure()
    adv = DF[DF['cls']=='adversary'].head(8)
    for _,s in adv.iterrows():
        ts = s.threat_score
        c  = '#EB5757' if ts>0.7 else '#FF8C00' if ts>0.4 else '#F2C94C'
        y  = np.zeros(200)
        if s.last_maneuver:
            mt = -random.uniform(4,40)
            mv = ts * random.uniform(1.5,5)
            y  = y + mv * np.exp(-((t-mt)**2/80))
        y += np.random.normal(0,0.04,200)
        fig.add_trace(go.Scatter(x=t, y=y, mode='lines', line=dict(color=c,width=2), name=s['id'][:12], fill='tozeroy', fillcolor=f"rgba({int(c[1:3], 16)}, {int(c[3:5], 16)}, {int(c[5:7], 16)}, 0.05)", hovertemplate=f"<b>{s['id']}</b><br>T: %{{x:.1f}}h<br>Dev: %{{y:.3f}} km<extra></extra>"))
    fig.add_hline(y=1.0, line_dash='dash', line_color='#F2C94C', line_width=2, annotation_text='ANOMALY', annotation_font=dict(size=12,color='#F2C94C',family='Share Tech Mono'))
    fig.add_hline(y=2.5, line_dash='dash', line_color='#EB5757', line_width=2, annotation_text='MANOEUVRE', annotation_font=dict(size=12,color='#EB5757',family='Share Tech Mono'))
    fig.update_layout(BASE_LAYOUT, height=600, xaxis=dict(showgrid=True,gridcolor='#06111E',color='#FFFFFF',tickfont=dict(size=12),title=dict(text='TIME (hours)',font=dict(size=13,color='#FFFFFF'))), yaxis=dict(showgrid=True,gridcolor='#06111E',color='#FFFFFF',tickfont=dict(size=12),title=dict(text='ORBIT DEVIATION (km)',font=dict(size=13,color='#FFFFFF'))), title=dict(text='MANOEUVRE DETECTION', font=dict(size=14,color='#EB5757'), x=0.5))
    return fig

def escalation_timeline():
    hrs = list(range(-48, 1, 4))[:13]
    data = {'ACTIVE':[0,0,0,0,0,1,1,1,2,2,3,4,5], 'PRE-CONFLICT': [2,2,3,3,3,4,5,6,7,8,9,10,11], 'ANOMALOUS': [8,9,8,10,11,12,14,16,18,17,19,21,22], 'NOMINAL': [40,38,41,39,42,40,38,35,32,30,28,27,25]}
    colors = {'ACTIVE':'#EB5757','PRE-CONFLICT':'#F2C94C','ANOMALOUS':'#FF8C00','NOMINAL':'#27AE60'}
    fig = go.Figure()
    for name, vals in data.items():
        fig.add_trace(go.Scatter(x=hrs[:len(vals)], y=vals, mode='lines', line=dict(color=colors[name], width=2), name=name, fill='tonexty' if name!='NOMINAL' else 'tozeroy', fillcolor=f"rgba({int(colors[name][1:3], 16)}, {int(colors[name][3:5], 16)}, {int(colors[name][5:7], 16)}, 0.1)", hovertemplate=f'{name}: %{{y}}<extra></extra>'))
    fig.update_layout(BASE_LAYOUT, height=220, margin=dict(l=30,r=5,t=5,b=25), xaxis=dict(showgrid=True,gridcolor='#06111E',color='#FFFFFF',tickfont=dict(size=11)), yaxis=dict(showgrid=True,gridcolor='#06111E',color='#FFFFFF',tickfont=dict(size=11)), legend=dict(font=dict(size=11, color='white'),x=0,y=1,orientation='h'))
    return fig

def threat_radar(sat):
    cats = ['PROXIMITY','MANOEUVRE','DEVIATION','CLUSTERING','LOITER','SHADOW']
    ts   = sat.threat_score
    vals = [min(round(ts*random.uniform(0.5,1.2),3),1) for _ in cats]
    fig = go.Figure(go.Scatterpolar(r=vals+[vals[0]], theta=cats+[cats[0]], fill='toself', fillcolor='rgba(235,87,87,0.2)', line=dict(color='#EB5757', width=3), hovertemplate='%{theta}: %{r:.3f}<extra></extra>'))
    fig.update_layout(BASE_LAYOUT, height=250, margin=dict(l=30,r=30,t=30,b=30), polar=dict(bgcolor='#06111E', radialaxis=dict(visible=True,range=[0,1],color='#FFFFFF',tickfont=dict(size=10)), angularaxis=dict(color='#FFFFFF',tickfont=dict(size=11))), showlegend=False)
    return fig

def render_saw():
    st.markdown("""<div style='font-family:Rajdhani,sans-serif;font-size:24px;color:#EB5757; letter-spacing:5px;font-weight:600;border-bottom:1px solid #0E2040; padding-bottom:10px;margin-bottom:18px'>
        🔴 SAW — SATELLITE ATTACK WARNING DASHBOARD</div>""", unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 2, 1])
    adv = DF[DF['cls']=='adversary'].sort_values('threat_score', ascending=False)

    with col_l:
        sec('THREAT INDICATORS')
        for _,s in adv.head(9).iterrows():
            ts = s.threat_score
            c  = '#EB5757' if ts>0.7 else '#FF8C00' if ts>0.4 else '#F2C94C'
            lvl= 'HIGH THREAT' if ts>0.7 else 'ANOMALOUS' if ts>0.4 else 'SUSPICIOUS'
            st.markdown(f"""<div style='background:{c}15;border-left:4px solid {c}; padding:10px 12px;margin:6px 0;border-radius:0 4px 4px 0'>
                <div style='display:flex;justify-content:space-between'>
                    <span style='color:{c};font-size:11px;font-weight:bold'>{lvl}</span>
                    <span style='color:{c};font-size:12px;font-weight:bold'>{ts:.4f}</span>
                </div>
                <div style='color:#FFFFFF;font-size:13px;font-weight:bold;'>{s['id']}</div>
                <div style='color:#AAB8C2;font-size:10px'>{s['flag']} {s.country} | {s.orbit_type} | {s.altitude_km:.0f}km</div>
                {bar(ts*100, c)}
            </div>""", unsafe_allow_html=True)

    with col_m:
        t1,t2 = st.tabs(['3D THREAT OVERLAY','MANOEUVRE VECTORS'])
        with t1: st.plotly_chart(saw_3d(), use_container_width=True)
        with t2: st.plotly_chart(maneuver_chart(), use_container_width=True)

    with col_r:
        sec('ESCALATION LADDER')
        esc_data = [('NOMINAL', len(DF[DF.threat_score<0.3]), '#27AE60'), ('ANOMALOUS', len(DF[(DF.threat_score>=0.3)&(DF.threat_score<0.5)]), '#FF8C00'), ('PRE-CONFLICT', len(DF[(DF.threat_score>=0.5)&(DF.threat_score<0.7)]), '#F2C94C'), ('ACTIVE', len(DF[DF.threat_score>=0.7]), '#EB5757')]
        for lvl, cnt, c in esc_data:
            st.markdown(f"""<div style='background:{c}15;border:1px solid {c}40; border-radius:5px;padding:12px;margin:6px 0;text-align:center'>
                <div style='color:{c};font-size:11px;letter-spacing:2px;font-weight:bold;'>{lvl}</div>
                <div style='color:{c};font-size:28px;font-weight:bold'>{cnt}</div>
            </div>""", unsafe_allow_html=True)

        sec('ESCALATION TIMELINE — 48H')
        st.plotly_chart(escalation_timeline(), use_container_width=True)

        sec('THREAT RADAR — SELECT OBJECT')
        adv_ids = adv['id'].tolist()
        if adv_ids:
            sel = st.selectbox('ADVERSARY OBJECT', adv_ids, key='saw_sel')
            s = adv[adv['id']==sel].iloc[0]
            st.plotly_chart(threat_radar(s), use_container_width=True)

        # RESTORED: CLUSTER ANALYSIS SECTION
        sec('CLUSTER ANALYSIS')
        for cn, desc, beh, c in [
            ('CLUSTER ALPHA','3 adv objects','COORDINATED APPROACH','#EB5757'),
            ('CLUSTER BETA', '2 unk objects','PROXIMITY OPERATIONS', '#F2C94C'),
            ('CLUSTER GAMMA','4 adv objects','FORMATION FLIGHT',     '#EB5757'),
        ]:
            st.markdown(f"""<div style='background:{c}15;border-left:3px solid {c}; padding:8px 10px;margin:4px 0;'>
                <div style='color:{c};font-size:11px;font-weight:bold'>{cn}</div>
                <div style='color:#FFFFFF;font-size:10px'>{desc}</div>
                <div style='color:#AAB8C2;font-size:9px'>{beh}</div>
            </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# TOP BAR + MAIN
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div style='background:linear-gradient(90deg,#06111E,#08162A,#06111E);
    border-bottom:1px solid #0E2040;padding:8px 20px; display:flex;justify-content:space-between;align-items:center;margin-bottom:10px'>
    <span style='font-family:Share Tech Mono,monospace;font-size:12px;color:#8AAED0;letter-spacing:2px'>⬡ CLASSIFIED // EYES ONLY // SCI-TK SPECIAL ACCESS</span>
    <span style='font-family:Share Tech Mono,monospace;font-size:12px;color:#8AAED0;letter-spacing:2px'>SPACE OPS CMD · SOP DASHBOARD v4.2 · UNCLASSIFIED DEMO</span>
    <span style='font-family:Share Tech Mono,monospace;font-size:12px;color:#27AE60;letter-spacing:2px;font-weight:bold;'>SYSTEM ● OPERATIONAL &nbsp; UPLINK ● NOMINAL</span>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs(["🌍  HOME", "🛰️  CLASSIFICATION", "⚠️  PROXIMITY ALERTS", "🛡️  SDIZ & CHOKE POINTS", "🔴  SAW THREAT"])
with tabs[0]: render_home()
with tabs[1]: render_classification()
with tabs[2]: render_proximity()
with tabs[3]: render_sdiz()
with tabs[4]: render_saw()