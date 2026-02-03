import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import json
import math
import time
from datetime import datetime

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Psychometric User Manual",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Progress bar styling */
    .trait-bar-container {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 6px 0;
    }
    .trait-label {
        width: 200px;
        min-width: 120px;
        font-size: 14px;
        font-weight: 500;
        color: #cbd5e1;
    }
    .trait-bar-bg {
        flex: 1;
        height: 12px;
        background: #334155;
        border-radius: 6px;
        overflow: hidden;
    }
    .trait-bar-fill {
        height: 100%;
        border-radius: 6px;
        transition: width 0.5s ease;
    }
    .trait-score {
        width: 30px;
        text-align: right;
        font-weight: 700;
        font-size: 14px;
        color: #f1f5f9;
    }
    
    /* Mobile responsive trait bars */
    @media (max-width: 640px) {
        .trait-bar-container {
            gap: 8px;
        }
        .trait-label {
            width: 110px;
            min-width: 110px;
            font-size: 12px;
        }
        .trait-score {
            width: 24px;
            font-size: 12px;
        }
    }
    
    /* Option buttons */
    .option-card {
        padding: 20px;
        border-radius: 12px;
        border: 2px solid #334155;
        cursor: pointer;
        transition: all 0.2s;
        margin-bottom: 8px;
    }
    .option-card:hover {
        border-color: #6366f1;
        background: #1e293b;
    }
    .option-selected-a {
        border-color: #3b82f6 !important;
        background: #1e3a5f !important;
    }
    .option-selected-b {
        border-color: #8b5cf6 !important;
        background: #2e1065 !important;
    }
    
    /* Intensity buttons */
    .intensity-btn {
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        border: 2px solid;
        transition: all 0.2s;
    }
    
    /* Category badge */
    .category-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    /* Table styling */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        margin: 12px 0;
        table-layout: fixed;
    }
    .styled-table th, .styled-table td {
        padding: 10px 14px;
        border: 1px solid #334155;
        text-align: left;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    .styled-table th {
        background: #1e293b;
        font-weight: 600;
        color: #94a3b8;
    }
    .styled-table td {
        color: #cbd5e1;
    }
    
    /* Mobile responsive tables */
    @media (max-width: 640px) {
        .styled-table th, .styled-table td {
            padding: 6px 8px;
            font-size: 12px;
        }
        .styled-table th:first-child, .styled-table td:first-child {
            width: 28%;
        }
    }
    
    /* Deep analysis text - ensure readable on all devices */
    .stMarkdown p, .stMarkdown li, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #f1f5f9 !important;
    }
    .stMarkdown a {
        color: #60a5fa !important;
    }
    
    /* Section headers */
    .section-header {
        font-size: 20px;
        font-weight: 700;
        color: #f1f5f9;
        padding-bottom: 8px;
        border-bottom: 2px solid #334155;
        margin: 24px 0 16px;
    }
    
    /* Scenario box */
    .scenario-box {
        background: #1e293b;
        border-left: 3px solid #f59e0b;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 12px;
        color: #e2e8f0;
    }
    
    /* Context box */
    .context-box {
        background: #1e293b;
        border-left: 3px solid #10b981;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 12px;
        color: #94a3b8;
        font-size: 14px;
    }
    
    /* Stacked button fix */
    div.stButton > button {
        width: 100%;
    }
    
    /* Pulse animation for follow-up indicator */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
</style>
""", unsafe_allow_html=True)

# Scroll to top helper - use session state to create unique key
if "scroll_key" not in st.session_state:
    st.session_state.scroll_key = 0

# Increment on each rerun to force script re-execution
st.session_state.scroll_key += 1

# Use components.html for reliable script execution
# Random string ensures no caching
unique_id = f"{st.session_state.scroll_key}_{int(time.time() * 1000)}"
components.html(f"""
<div id="scroll-trigger-{unique_id}"></div>
<script>
    (function() {{
        function scrollToTop() {{
            // Try all possible scroll containers
            var targets = [
                window.parent.document.querySelector('section.main'),
                window.parent.document.querySelector('.main'),
                window.parent.document.querySelector('[data-testid="stAppViewContainer"]'),
                window.parent.document.querySelector('.stApp'),
                window.parent.document.body,
                window.parent.document.documentElement
            ];
            targets.forEach(function(el) {{
                if (el) {{
                    el.scrollTop = 0;
                    if (el.scrollTo) el.scrollTo({{top: 0, left: 0, behavior: 'instant'}});
                }}
            }});
            window.parent.scrollTo(0, 0);
        }}
        // Multiple attempts with delays for mobile
        scrollToTop();
        setTimeout(scrollToTop, 100);
        setTimeout(scrollToTop, 250);
        setTimeout(scrollToTop, 500);
        
        // Focus trick: find first header and scroll into view
        setTimeout(function() {{
            var header = window.parent.document.querySelector('h1, h2, h3, .stMarkdown');
            if (header) header.scrollIntoView({{behavior: 'instant', block: 'start'}});
        }}, 200);
    }})();
</script>
""", height=0)

# ============================================================
# TRANSLATIONS
# ============================================================
TRANSLATIONS = {
    "en": {
        "title": "Psychometric User Manual",
        "subtitle": "Build a high-resolution profile of your personality architecture",
        "phase1Title": "Phase 1: Discovery",
        "phase1Desc": "20 questions mapping your baseline traits and drivers",
        "phase2Title": "Phase 2: Stress Testing",
        "phase2Desc": '15 high-pressure scenarios to reveal your "Dark Side"',
        "phase3Title": "Phase 3: Solution Design",
        "phase3Desc": "8 questions to co-create operational rules for blind spots",
        "formatNote": "Format:",
        "formatDesc": "You'll see two options (A vs B) for each question. Choose the one that resonates more strongly—even if neither is perfect. Then rate how strongly it fits. There are no right answers.",
        "beginBtn": "Begin Assessment",
        "choosePrompt": "Choose A or B",
        "slightly": "Slightly",
        "clearly": "Clearly",
        "strongly": "Strongly",
        "howStrongly": "How strongly?",
        "back": "← Back",
        "next": "Next →",
        "pdfTitle": "Psychometric User Manual",
        "pdfGenerated": "Generated on",
        "architecture": "1. The Architecture",
        "hardwareTitle": "Hardware (Temperament) — Big Five Profile",
        "osTitle": "Operating System — Action Mode Profile",
        "driversTitle": "Drivers (Motivation)",
        "openness": "Openness to Experience",
        "conscientiousness": "Conscientiousness",
        "extraversion": "Extraversion",
        "agreeableness": "Agreeableness",
        "stability": "Emotional Stability",
        "factFinder": "Research Drive",
        "followThru": "Systems Drive",
        "quickStart": "Launch Drive",
        "implementor": "Build Drive",
        "autonomy": "Autonomy",
        "mastery": "Mastery",
        "power": "Power",
        "affiliation": "Affiliation",
        "contextualContrasts": "2. Contextual Contrasts",
        "trait": "Trait",
        "closeButNot": "Close But Not You",
        "clearlyNot": "Clearly Not You",
        "decisionSpeed": "Decision Speed",
        "riskProfile": "Risk Profile",
        "conflictStyle": "Conflict Style",
        "learningMode": "Learning Mode",
        "darkSide": "3. Dark Side — Stress Patterns",
        "identifiedDerailers": "Identified Derailers:",
        "environmentFit": "4. Environment Fit",
        "thrivesIn": "Thrives In",
        "failsIn": "Fails In",
        "operationalRules": "5. Operational Rules",
        "rulesIntro": "Self-imposed rules to manage identified friction points:",
        "disclaimer": "This assessment is for self-reflection purposes. For clinical or hiring decisions, consult validated instruments administered by qualified professionals.",
        "impulsive": "Impulsive without data", "methodical": "Methodical planner",
        "paralysis": "Analysis paralysis", "gambler": "Shoot-from-hip gambler",
        "calcRisk": "Calculated risk-taker", "steadyOpt": "Steady optimizer",
        "riskAverse": "Risk-averse preserver", "thrillSeek": "Thrill-seeking gambler",
        "diplomatic": "Diplomatic challenger", "harmonious": "Harmonious mediator",
        "avoider": "Conflict avoider", "aggressive": "Aggressive confronter",
        "experimental": "Experimental learner", "studious": "Studious observer",
        "theoretical": "Theoretical academic", "trialByFire": "Trial-by-fire improviser",
        "highAutonomy": "High autonomy environments", "structured": "Structured team environments",
        "micromanaged": "Micromanaged bureaucracies", "unstructured": "Unstructured chaos",
        "fastMoving": "Fast-moving startups", "methodicalOrg": "Methodical organizations",
        "slowMoving": "Slow-moving institutions", "moveFast": "Move-fast-break-things cultures",
        "collaborative": "Collaborative, social settings", "deepWork": "Deep work, focus-driven cultures",
        "isolated": "Isolated individual work", "constantMeetings": "Constant meetings and interruptions",
        "learningFocused": "Learning-focused organizations", "executionFocused": "Execution-focused organizations",
        "stagnant": "Stagnant, no-growth environments", "constantReinvention": "Constant reinvention chaos",
        "confrontational": "Confrontational under pressure", "withdrawing": "Withdrawing under pressure",
        "taskFocused": "Task-focused in emotional situations", "ruleBending": "Rule-bending when stakes are high",
        "perfectionism": "Perfectionism under deadline", "selfSacrifice": "Self-sacrifice pattern",
        "spreadingThin": "Spreading thin under chaos",
        "rule1a": "Implement non-negotiable calendar blocks for recovery and deep work",
        "rule1b": "Designate a trusted advisor with veto power over new commitments",
        "rule2a": "Set 48-hour decision deadlines to prevent analysis paralysis",
        "rule2b": "Institute 24-hour cooling-off periods for major decisions",
        "rule3a": "Schedule monthly structured feedback sessions with key stakeholders",
        "rule4a": "Apply 1.5x multiplier to all time estimates",
        "rule4b": "Challenge yourself to act before feeling 'ready'",
        "summaryTab": "📊 Summary",
        "deepTab": "📖 Deep Analysis",
        "generateBtn": "Generate Deep Analysis",
        "generating": "Generating deep analysis...",
        "downloadMd": "Download .md",
        "downloadHtml": "Download .html (for PDF print)",
        "startOver": "Start Over",
        "completeForAnalysis": "Complete the full assessment for detailed analysis",
        "completePhase3": "Complete Phase 3 for personalized rules.",
    },
    "de": {
        "title": "Psychometrisches Benutzerhandbuch",
        "subtitle": "Erstellen Sie ein hochauflösendes Profil Ihrer Persönlichkeitsarchitektur",
        "phase1Title": "Phase 1: Entdeckung",
        "phase1Desc": "20 Fragen zur Erfassung Ihrer grundlegenden Eigenschaften und Antriebe",
        "phase2Title": "Phase 2: Stresstest",
        "phase2Desc": '15 Hochdruckszenarien zur Enthüllung Ihrer "Schattenseite"',
        "phase3Title": "Phase 3: Lösungsdesign",
        "phase3Desc": "8 Fragen zur gemeinsamen Erstellung von Regeln für blinde Flecken",
        "formatNote": "Format:",
        "formatDesc": "Sie sehen zwei Optionen (A vs B) für jede Frage. Wählen Sie die, die stärker resoniert—auch wenn keine perfekt ist. Dann bewerten Sie, wie stark sie passt. Es gibt keine richtigen Antworten.",
        "beginBtn": "Assessment Starten",
        "choosePrompt": "Wählen Sie A oder B",
        "slightly": "Leicht",
        "clearly": "Klar",
        "strongly": "Stark",
        "howStrongly": "Wie stark?",
        "back": "← Zurück",
        "next": "Weiter →",
        "pdfTitle": "Psychometrisches Benutzerhandbuch",
        "pdfGenerated": "Erstellt am",
        "architecture": "1. Die Architektur",
        "hardwareTitle": "Hardware (Temperament) — Big Five Profil",
        "osTitle": "Betriebssystem — Handlungsmodus-Profil",
        "driversTitle": "Antriebe (Motivation)",
        "openness": "Offenheit für Erfahrungen",
        "conscientiousness": "Gewissenhaftigkeit",
        "extraversion": "Extraversion",
        "agreeableness": "Verträglichkeit",
        "stability": "Emotionale Stabilität",
        "factFinder": "Recherche-Antrieb",
        "followThru": "System-Antrieb",
        "quickStart": "Start-Antrieb",
        "implementor": "Bau-Antrieb",
        "autonomy": "Autonomie",
        "mastery": "Meisterschaft",
        "power": "Macht",
        "affiliation": "Zugehörigkeit",
        "contextualContrasts": "2. Kontextuelle Kontraste",
        "trait": "Eigenschaft",
        "closeButNot": "Ähnlich aber nicht Sie",
        "clearlyNot": "Eindeutig nicht Sie",
        "decisionSpeed": "Entscheidungsgeschwindigkeit",
        "riskProfile": "Risikoprofil",
        "conflictStyle": "Konfliktstil",
        "learningMode": "Lernmodus",
        "darkSide": "3. Schattenseite — Stressmuster",
        "identifiedDerailers": "Identifizierte Entgleiser:",
        "environmentFit": "4. Umgebungspassung",
        "thrivesIn": "Blüht auf in",
        "failsIn": "Scheitert in",
        "operationalRules": "5. Operationelle Regeln",
        "rulesIntro": "Selbstauferlegte Regeln zur Bewältigung identifizierter Reibungspunkte:",
        "disclaimer": "Dieses Assessment dient der Selbstreflexion. Für klinische oder Personalentscheidungen konsultieren Sie validierte Instrumente von qualifizierten Fachleuten.",
        "impulsive": "Impulsiv ohne Daten", "methodical": "Methodischer Planer",
        "paralysis": "Analyse-Paralyse", "gambler": "Bauchentscheider",
        "calcRisk": "Kalkulierter Risikoträger", "steadyOpt": "Stetiger Optimierer",
        "riskAverse": "Risikoaverser Bewahrer", "thrillSeek": "Nervenkitzel-Sucher",
        "diplomatic": "Diplomatischer Herausforderer", "harmonious": "Harmonischer Vermittler",
        "avoider": "Konfliktvermeider", "aggressive": "Aggressiver Konfrontierer",
        "experimental": "Experimenteller Lerner", "studious": "Fleißiger Beobachter",
        "theoretical": "Theoretischer Akademiker", "trialByFire": "Feuertaufe-Improvisator",
        "highAutonomy": "Hohe Autonomie-Umgebungen", "structured": "Strukturierte Team-Umgebungen",
        "micromanaged": "Mikromanagte Bürokratien", "unstructured": "Unstrukturiertes Chaos",
        "fastMoving": "Schnelllebige Startups", "methodicalOrg": "Methodische Organisationen",
        "slowMoving": "Langsame Institutionen", "moveFast": "Schnell-handeln-Kulturen",
        "collaborative": "Kollaborative, soziale Umgebungen", "deepWork": "Deep-Work, fokusgetriebene Kulturen",
        "isolated": "Isolierte Einzelarbeit", "constantMeetings": "Ständige Meetings und Unterbrechungen",
        "learningFocused": "Lernorientierte Organisationen", "executionFocused": "Umsetzungsorientierte Organisationen",
        "stagnant": "Stagnierende Umgebungen ohne Wachstum", "constantReinvention": "Ständiges Neuerfindungs-Chaos",
        "confrontational": "Konfrontativ unter Druck", "withdrawing": "Rückzug unter Druck",
        "taskFocused": "Aufgabenorientiert in emotionalen Situationen",
        "ruleBending": "Regelbeugung bei hohen Einsätzen",
        "perfectionism": "Perfektionismus unter Zeitdruck", "selfSacrifice": "Selbstaufopferungsmuster",
        "spreadingThin": "Verzetteln im Chaos",
        "rule1a": "Implementieren Sie nicht verhandelbare Kalenderblöcke für Erholung und Deep Work",
        "rule1b": "Bestimmen Sie einen vertrauenswürdigen Berater mit Vetorecht über neue Verpflichtungen",
        "rule2a": "Setzen Sie 48-Stunden-Entscheidungsfristen gegen Analyse-Paralyse",
        "rule2b": "Führen Sie 24-Stunden-Abkühlungsperioden für wichtige Entscheidungen ein",
        "rule3a": "Planen Sie monatliche strukturierte Feedback-Sitzungen mit wichtigen Stakeholdern",
        "rule4a": "Wenden Sie einen 1,5x Multiplikator auf alle Zeitschätzungen an",
        "rule4b": "Fordern Sie sich heraus zu handeln, bevor Sie sich 'bereit' fühlen",
        "summaryTab": "📊 Kurzübersicht",
        "deepTab": "📖 Tiefenanalyse",
        "generateBtn": "Tiefenanalyse generieren",
        "generating": "Tiefenanalyse wird erstellt...",
        "downloadMd": "Herunterladen .md",
        "downloadHtml": "Herunterladen .html (für PDF-Druck)",
        "startOver": "Neu Starten",
        "completeForAnalysis": "Vervollständigen Sie das Assessment für detaillierte Analyse",
        "completePhase3": "Vervollständigen Sie Phase 3 für personalisierte Regeln.",
    }
}

# ============================================================
# QUESTION BANKS
# ============================================================
QUESTIONS = {
    "en": {
        "discovery": [
            {"id": 1, "category": "Big Five - Openness", "questionA": "You'd rather know everything about one topic", "questionB": "You'd rather know a bit about many topics"},
            {"id": 2, "category": "Big Five - Conscientiousness", "questionA": "You finish things, even when they get boring", "questionB": "You move on when something better comes along"},
            {"id": 3, "category": "Big Five - Extraversion", "questionA": "You think better when you talk to others", "questionB": "You think better when you're alone"},
            {"id": 4, "category": "Big Five - Agreeableness", "questionA": "You say hard things, even if people don't like it", "questionB": "You keep the peace, even if it costs you"},
            {"id": 5, "category": "Big Five - Neuroticism", "questionA": "A bit of stress helps you focus", "questionB": "You work best when you feel relaxed"},
            {"id": 6, "category": "Action Mode - Research", "questionA": "You need data before you decide", "questionB": "You go with your gut and look things up later"},
            {"id": 7, "category": "Action Mode - Systems", "questionA": "You like making lists and processes", "questionB": "Lists and processes slow you down"},
            {"id": 8, "category": "Action Mode - Launch", "questionA": "You'd rather start now and fix later", "questionB": "You'd rather wait until it's ready"},
            {"id": 9, "category": "Action Mode - Build", "questionA": "You understand things by building them", "questionB": "You understand things by thinking them through"},
            {"id": 10, "category": "Core Driver - Autonomy", "questionA": "Freedom at work matters more than money", "questionB": "You'd give up some freedom for better pay"},
            {"id": 11, "category": "Core Driver - Mastery", "questionA": "You want to be the best at one thing", "questionB": "You want to be good at many things"},
            {"id": 12, "category": "Core Driver - Power", "questionA": "You like being in charge", "questionB": "You'd rather influence from the side"},
            {"id": 13, "category": "Core Driver - Affiliation", "questionA": "Who you work with matters more than what you do", "questionB": "What you do matters more than who you work with"},
            {"id": 14, "category": "Decision Making", "questionA": "You decide quickly and adjust if needed", "questionB": "You take your time to get it right the first time"},
            {"id": 15, "category": "Risk Orientation", "questionA": "Big risks excite you", "questionB": "You prefer steady progress"},
            {"id": 16, "category": "Conflict Style", "questionA": "You address problems directly", "questionB": "You find ways around confrontation"},
            {"id": 17, "category": "Time Orientation", "questionA": "You plan for the future", "questionB": "You focus on today"},
            {"id": 18, "category": "Learning Style", "questionA": "You learn by trying", "questionB": "You learn by watching first"},
            {"id": 19, "category": "Success Definition", "questionA": "Success means building something that lasts", "questionB": "Success means living how you want"},
            {"id": 20, "category": "Feedback Response", "questionA": "Criticism motivates you right away", "questionB": "Criticism needs time to sink in"},
        ],
        "stressTesting": [
            {"id": 21, "category": "Stress - Volatility", "scenario": "Someone made an important decision without asking you.", "questionA": "You confront them right away", "questionB": "You step back and think before reacting"},
            {"id": 22, "category": "Stress - Skepticism", "scenario": "A new colleague wants to change something you built.", "questionA": "You question their idea openly", "questionB": "You first check if they know what they're talking about"},
            {"id": 23, "category": "Stress - Caution", "scenario": "A competitor just launched what you're working on.", "questionA": "You rush to launch, even if it's not perfect", "questionB": "You slow down to do it differently"},
            {"id": 24, "category": "Stress - Detachment", "scenario": "Your team got bad news and people are upset.", "questionA": "You focus on fixing the problem", "questionB": "You first take care of how people feel"},
            {"id": 25, "category": "Stress - Passive Resistance", "scenario": "Your boss wants you to do something you think is wrong.", "questionA": "You do it, but slowly", "questionB": "You say openly that you disagree"},
            {"id": 26, "category": "Stress - Overconfidence", "scenario": "You present right after someone who did really well.", "questionA": "You try harder to match them", "questionB": "You stay calm and do your thing"},
            {"id": 27, "category": "Stress - Risk-Taking", "scenario": "A shortcut would help your numbers but breaks the rules a bit.", "questionA": "You take it — results count", "questionB": "You skip it and miss the target"},
            {"id": 28, "category": "Stress - Attention-Seeking", "scenario": "In a meeting, you should stay quiet and let others talk.", "questionA": "That's hard for you", "questionB": "That's easy for you"},
            {"id": 29, "category": "Stress - Eccentricity", "scenario": "Someone calls your idea unrealistic.", "questionA": "You stick with it — they don't get it yet", "questionB": "You adjust to something more normal"},
            {"id": 30, "category": "Stress - Perfectionism", "scenario": "80% done today or 100% in three weeks?", "questionA": "You wait for 100%", "questionB": "You go with 80%"},
            {"id": 31, "category": "Stress - Compliance", "scenario": "Someone you trust gives you advice you don't agree with.", "questionA": "You follow it — they've earned your trust", "questionB": "You thank them and do your own thing"},
            {"id": 32, "category": "Burnout Pattern", "scenario": "You're exhausted. Vacation is booked. A crisis comes up.", "questionA": "You cancel the vacation", "questionB": "You go anyway"},
            {"id": 33, "category": "Failure Response", "scenario": "Your project just failed publicly.", "questionA": "You analyze what went wrong right away", "questionB": "You need distance first"},
            {"id": 34, "category": "Trust Repair", "scenario": "Someone took credit for your work.", "questionA": "You talk to them directly first", "questionB": "You make sure others know the truth first"},
            {"id": 35, "category": "Control Under Chaos", "scenario": "Everything goes wrong at once — people, money, product.", "questionA": "You pick what matters most and let the rest burn", "questionB": "You try to fix everything"},
        ],
        "solutionDesign": [
            {"id": 36, "category": "Rule Design - Boundaries", "context": "You tend to take on too much when stressed.", "questionA": "You need blocked time that nobody can touch", "questionB": "You need someone who can say no for you"},
            {"id": 37, "category": "Rule Design - Decision Making", "context": "You either think too much or too little before deciding.", "questionA": "You need deadlines to stop overthinking", "questionB": "You need waiting time to stop rushing"},
            {"id": 38, "category": "Rule Design - Feedback", "context": "How you get feedback affects what you do with it.", "questionA": "You need scheduled feedback meetings", "questionB": "You need feedback right when things happen"},
            {"id": 39, "category": "Rule Design - Energy Management", "context": "Your energy level affects your work quality.", "questionA": "You do hard things first, when you're fresh", "questionB": "You start with easy things to get going"},
            {"id": 40, "category": "Rule Design - Relationships", "context": "Your style creates friction with certain people.", "questionA": "You need more patience with slower people", "questionB": "You need to push back more against loud people"},
            {"id": 41, "category": "Rule Design - Blind Spots", "context": "Everyone has patterns they don't see.", "questionA": "You take on too much and underestimate time", "questionB": "You underestimate yourself and prepare too much"},
            {"id": 42, "category": "Rule Design - Recovery", "context": "How you recover from setbacks matters.", "questionA": "You recover by doing something", "questionB": "You recover by resting"},
            {"id": 43, "category": "Rule Design - Accountability", "context": "How you stay on track affects what you finish.", "questionA": "You need someone checking on you", "questionB": "Outside pressure makes it worse — you need your own system"},
        ],
    },
    "de": {
        "discovery": [
            {"id": 1, "category": "Big Five - Offenheit", "questionA": "Du willst ein Thema richtig durchdringen", "questionB": "Du willst überall mitreden können"},
            {"id": 2, "category": "Big Five - Gewissenhaftigkeit", "questionA": "Was du anfängst, machst du fertig", "questionB": "Wenn was Besseres kommt, wechselst du"},
            {"id": 3, "category": "Big Five - Extraversion", "questionA": "Im Gespräch kommen dir die besten Ideen", "questionB": "Alleine denkst du am klarsten"},
            {"id": 4, "category": "Big Five - Verträglichkeit", "questionA": "Du sagst, was Sache ist, auch wenn's unbequem ist", "questionB": "Du hältst die Gruppe zusammen, auch wenn du dafür zurücksteckst"},
            {"id": 5, "category": "Big Five - Neurotizismus", "questionA": "Mit etwas Druck läufst du besser", "questionB": "Ohne Stress arbeitest du besser"},
            {"id": 6, "category": "Handlungsmodus - Recherche", "questionA": "Ohne Fakten entscheidest du nicht", "questionB": "Du entscheidest aus dem Bauch"},
            {"id": 7, "category": "Handlungsmodus - Systeme", "questionA": "Du machst dir gerne Systeme und Abläufe", "questionB": "Zu viel Struktur nervt dich"},
            {"id": 8, "category": "Handlungsmodus - Umsetzung", "questionA": "Du legst einfach los und schaust, was passiert", "questionB": "Du planst erstmal gründlich durch"},
            {"id": 9, "category": "Handlungsmodus - Bau", "questionA": "Du verstehst was, indem du es anfasst oder baust", "questionB": "Du verstehst was, indem du es im Kopf durchgehst"},
            {"id": 10, "category": "Kernantrieb - Autonomie", "questionA": "Hauptsache selbstbestimmt arbeiten", "questionB": "Für gutes Geld nimmst du auch Vorgaben in Kauf"},
            {"id": 11, "category": "Kernantrieb - Meisterschaft", "questionA": "In einer Sache richtig gut sein", "questionB": "In vielen Sachen brauchbar sein"},
            {"id": 12, "category": "Kernantrieb - Macht", "questionA": "Du übernimmst gerne das Ruder", "questionB": "Du ziehst lieber im Hintergrund die Fäden"},
            {"id": 13, "category": "Kernantrieb - Zugehörigkeit", "questionA": "Das Team ist wichtiger als die Aufgabe", "questionB": "Die Aufgabe ist wichtiger als das Team"},
            {"id": 14, "category": "Entscheidungsfindung", "questionA": "Schnell entscheiden, notfalls korrigieren", "questionB": "Lieber einmal richtig entscheiden"},
            {"id": 15, "category": "Risikoorientierung", "questionA": "Hohe Einsätze machen dir Spaß", "questionB": "Lieber stetig vorankommen"},
            {"id": 16, "category": "Konfliktstil", "questionA": "Probleme sprichst du direkt an", "questionB": "Du suchst den Weg ohne Konfrontation"},
            {"id": 17, "category": "Zeitorientierung", "questionA": "Du denkst an morgen", "questionB": "Du lebst im Jetzt"},
            {"id": 18, "category": "Lernstil", "questionA": "Ausprobieren ist dein Weg zu lernen", "questionB": "Erstmal zugucken, dann selber machen"},
            {"id": 19, "category": "Erfolgsdefinition", "questionA": "Erfolg heißt: was aufbauen, das bleibt", "questionB": "Erfolg heißt: leben wie du willst"},
            {"id": 20, "category": "Feedback-Reaktion", "questionA": "Kritik bringt dich sofort in Bewegung", "questionB": "Kritik muss erstmal sacken"},
        ],
        "stressTesting": [
            {"id": 21, "category": "Stress - Volatilität", "scenario": "Jemand hat über deinen Kopf hinweg entschieden.", "questionA": "Du gehst ihn sofort an", "questionB": "Du wartest ab und überlegst erstmal"},
            {"id": 22, "category": "Stress - Skepsis", "scenario": "Der Neue will was ändern, das du aufgebaut hast.", "questionA": "Du stellst seine Idee vor allen in Frage", "questionB": "Du schaust dir erstmal an, was er drauf hat"},
            {"id": 23, "category": "Stress - Vorsicht", "scenario": "Die Konkurrenz hat euch überholt.", "questionA": "Ihr haut schnell was raus, auch wenn's wackelt", "questionB": "Ihr macht es anders statt nur schneller"},
            {"id": 24, "category": "Stress - Distanzierung", "scenario": "Im Team ist dicke Luft nach schlechten Nachrichten.", "questionA": "Du kümmerst dich ums Problem", "questionB": "Du kümmerst dich um die Leute"},
            {"id": 25, "category": "Stress - Passiver Widerstand", "scenario": "Der Chef will was von dir, das du falsch findest.", "questionA": "Du machst mit, aber ohne Elan", "questionB": "Du sagst ihm, dass du das anders siehst"},
            {"id": 26, "category": "Stress - Überschätzung", "scenario": "Vor dir hat jemand richtig abgeliefert.", "questionA": "Du legst noch eine Schippe drauf", "questionB": "Du machst einfach dein Ding"},
            {"id": 27, "category": "Stress - Risikobereitschaft", "scenario": "Eine Abkürzung würde die Zahlen retten, ist aber grenzwertig.", "questionA": "Du nimmst sie — am Ende zählt das Ergebnis", "questionB": "Du lässt es und nimmst die schlechten Zahlen"},
            {"id": 28, "category": "Stress - Aufmerksamkeit", "scenario": "Du sollst zuhören und dich zurückhalten.", "questionA": "Das fällt dir schwer", "questionB": "Das ist kein Problem"},
            {"id": 29, "category": "Stress - Exzentrizität", "scenario": "Deine Idee wird als unrealistisch abgetan.", "questionA": "Du bleibst dabei — die anderen kapieren es noch nicht", "questionB": "Du schwenkst auf was Machbareres um"},
            {"id": 30, "category": "Stress - Perfektionismus", "scenario": "80% jetzt oder 100% in drei Wochen?", "questionA": "Du wartest auf die 100%", "questionB": "Du nimmst die 80%"},
            {"id": 31, "category": "Stress - Konformität", "scenario": "Jemand, dem du vertraust, rät dir was, das du falsch findest.", "questionA": "Du machst es trotzdem — er hat sich das Vertrauen verdient", "questionB": "Du gehst deinen eigenen Weg"},
            {"id": 32, "category": "Burnout-Muster", "scenario": "Du bist platt. Urlaub steht an. Eine Krise kommt dazwischen.", "questionA": "Du bleibst und sagst den Urlaub ab", "questionB": "Du fährst trotzdem"},
            {"id": 33, "category": "Misserfolgsreaktion", "scenario": "Dein Projekt ist gerade vor allen gescheitert.", "questionA": "Du gehst sofort in die Analyse", "questionB": "Du brauchst erstmal Abstand"},
            {"id": 34, "category": "Vertrauensreparatur", "scenario": "Jemand hat sich mit deiner Arbeit geschmückt.", "questionA": "Du klärst das erstmal unter vier Augen", "questionB": "Du sorgst erstmal dafür, dass andere Bescheid wissen"},
            {"id": 35, "category": "Kontrolle im Chaos", "scenario": "Alles brennt gleichzeitig — Team, Geld, Produkt.", "questionA": "Du konzentrierst dich auf das Wichtigste und lässt anderes liegen", "questionB": "Du versuchst, alles gleichzeitig zu retten"},
        ],
        "solutionDesign": [
            {"id": 36, "category": "Regeldesign - Grenzen", "context": "Unter Druck nimmst du zu viel auf dich.", "questionA": "Du brauchst feste Zeiten, die keiner antastet", "questionB": "Du brauchst jemanden, der für dich bremst"},
            {"id": 37, "category": "Regeldesign - Entscheidungsfindung", "context": "Du grübelst entweder zu lang oder entscheidest zu schnell.", "questionA": "Du brauchst Fristen, die dich zum Entscheiden zwingen", "questionB": "Du brauchst Pausen, die dich vom Schnellschuss abhalten"},
            {"id": 38, "category": "Regeldesign - Feedback", "context": "Wie Feedback bei dir ankommt, entscheidet, was du damit machst.", "questionA": "Du brauchst feste Termine dafür", "questionB": "Du brauchst es sofort, wenn was ist"},
            {"id": 39, "category": "Regeldesign - Energiemanagement", "context": "Deine Energie über den Tag beeinflusst deine Arbeit.", "questionA": "Das Schwere machst du morgens", "questionB": "Du brauchst Anlauf mit kleinen Sachen"},
            {"id": 40, "category": "Regeldesign - Beziehungen", "context": "Mit bestimmten Leuten hakt es bei dir.", "questionA": "Du musst geduldiger mit den Langsamen sein", "questionB": "Du musst mehr Kontra geben bei den Lauten"},
            {"id": 41, "category": "Regeldesign - Blinde Flecken", "context": "Jeder hat Muster, die er selbst nicht sieht.", "questionA": "Du unterschätzt, wie lang Dinge dauern", "questionB": "Du unterschätzt, was du kannst"},
            {"id": 42, "category": "Regeldesign - Erholung", "context": "Wie du dich von Rückschlägen erholst.", "questionA": "Indem du was tust", "questionB": "Indem du Ruhe findest"},
            {"id": 43, "category": "Regeldesign - Verantwortlichkeit", "context": "Wie du dich selbst bei der Stange hältst.", "questionA": "Jemand muss nachhaken", "questionB": "Druck von außen macht es schlimmer — du brauchst dein eigenes System"},
        ],
    }
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def format_date(lang):
    """Format current date properly for German/English."""
    now = datetime.now()
    if lang == "de":
        months_de = ["Januar", "Februar", "März", "April", "Mai", "Juni", 
                     "Juli", "August", "September", "Oktober", "November", "Dezember"]
        return f"{now.day}. {months_de[now.month - 1]} {now.year}"
    else:
        return now.strftime("%B %d, %Y")

def get_all_questions(lang):
    """Get all questions as a flat list."""
    qs = QUESTIONS[lang]
    return qs["discovery"] + qs["stressTesting"] + qs["solutionDesign"]

def get_choice(q_id):
    """Get the choice (A or B) for a question."""
    a = st.session_state.answers.get(q_id)
    if a is None:
        return None
    return a.get("choice")

def get_intensity(q_id):
    """Get the intensity (1-3) for a question."""
    a = st.session_state.answers.get(q_id)
    if a is None:
        return 0
    return a.get("intensity", 2)

def analyze_results():
    """Compute trait scores, stress patterns, and operational rules."""
    lang = st.session_state.language
    t = TRANSLATIONS[lang]
    
    raw = {
        "openness": 5, "conscientiousness": 5, "extraversion": 5,
        "agreeableness": 5, "stability": 5,
        "factFinder": 5, "followThru": 5, "quickStart": 5, "implementor": 5,
        "autonomy": 5, "mastery": 5, "power": 5, "affiliation": 5,
    }
    
    def pri(q_id, trait, a_dir, b_dir):
        c = get_choice(q_id)
        if not c:
            return
        w = get_intensity(q_id)
        raw[trait] += a_dir * w if c == "A" else b_dir * w
    
    def sec(q_id, trait, a_dir, b_dir=0):
        c = get_choice(q_id)
        if not c:
            return
        w = math.ceil(get_intensity(q_id) / 2)
        raw[trait] += a_dir * w if c == "A" else b_dir * w
    
    # Phase 1: Primary
    pri(1, "openness", -1, 1)
    pri(2, "conscientiousness", 1, -1)
    pri(3, "extraversion", 1, -1)
    pri(4, "agreeableness", -1, 1)
    pri(5, "stability", -1, 1)
    pri(6, "factFinder", 1, -1)
    pri(7, "followThru", 1, -1)
    pri(8, "quickStart", 1, -1)
    pri(9, "implementor", 1, -1)
    pri(10, "autonomy", 1, -1)
    pri(11, "mastery", 1, -1)
    pri(12, "power", 1, -1)
    pri(13, "affiliation", 1, -1)
    
    # Phase 1: Secondary
    sec(14, "quickStart", 1, -1)
    sec(15, "quickStart", 1, 0)
    sec(15, "stability", -1, 1)
    sec(16, "extraversion", 1, -1)
    sec(16, "agreeableness", -1, 1)
    sec(17, "openness", 1, -1)
    sec(18, "quickStart", 1, 0)
    sec(18, "implementor", 1, -1)
    sec(19, "power", 1, -1)
    sec(19, "mastery", 1, 0)
    sec(20, "stability", 1, -1)
    sec(20, "conscientiousness", 1, 0)
    
    # Phase 2: Secondary
    sec(21, "extraversion", 1, -1)
    sec(22, "agreeableness", -1, 0)
    sec(23, "quickStart", 1, -1)
    sec(24, "agreeableness", -1, 1)
    sec(26, "extraversion", 1, 0)
    sec(29, "openness", 1, -1)
    sec(30, "conscientiousness", 1, -1)
    sec(30, "followThru", 1, 0)
    sec(31, "autonomy", -1, 1)
    sec(31, "affiliation", 1, 0)
    
    # Clamp
    traits = {}
    for key, val in raw.items():
        traits[key] = max(1, min(10, round(val)))
    
    # Stress patterns
    stress = []
    if get_choice(21) == "A": stress.append(t["confrontational"])
    if get_choice(21) == "B": stress.append(t["withdrawing"])
    if get_choice(24) == "A": stress.append(t["taskFocused"])
    if get_choice(27) == "A": stress.append(t["ruleBending"])
    if get_choice(30) == "A": stress.append(t["perfectionism"])
    if get_choice(32) == "A": stress.append(t["selfSacrifice"])
    if get_choice(35) == "B": stress.append(t["spreadingThin"])
    
    # Rules
    rules = []
    if get_choice(36) == "A": rules.append(t["rule1a"])
    if get_choice(36) == "B": rules.append(t["rule1b"])
    if get_choice(37) == "A": rules.append(t["rule2a"])
    if get_choice(37) == "B": rules.append(t["rule2b"])
    if get_choice(38) == "A": rules.append(t["rule3a"])
    if get_choice(41) == "A": rules.append(t["rule4a"])
    if get_choice(41) == "B": rules.append(t["rule4b"])
    
    return {"traits": traits, "stressPatterns": stress, "operationalRules": rules}

def render_trait_bar(label, value, color="#3b82f6"):
    """Render a colored progress bar for a trait."""
    pct = value * 10
    st.markdown(f"""
    <div class="trait-bar-container">
        <span class="trait-label">{label}</span>
        <div class="trait-bar-bg">
            <div class="trait-bar-fill" style="width:{pct}%;background:{color};"></div>
        </div>
        <span class="trait-score">{value}</span>
    </div>
    """, unsafe_allow_html=True)

def get_summary_markdown(analysis, t, lang):
    """Build the summary as a markdown string."""
    date_str = format_date(lang)
    
    def bar(v):
        filled = round(v)
        return "█" * filled + "░" * (10 - filled) + f" **{v}/10**"
    
    tr = analysis["traits"]
    md = f"# {t['pdfTitle']}\n\n*{t['pdfGenerated']} {date_str}*\n\n---\n\n"
    md += f"## {t['architecture']}\n\n### {t['hardwareTitle']}\n\n"
    for key, label in [("openness", t["openness"]), ("conscientiousness", t["conscientiousness"]),
                       ("extraversion", t["extraversion"]), ("agreeableness", t["agreeableness"]),
                       ("stability", t["stability"])]:
        md += f"- {label}: {bar(tr[key])}\n"
    
    md += f"\n### {t['osTitle']}\n\n"
    for key, label in [("factFinder", t["factFinder"]), ("followThru", t["followThru"]),
                       ("quickStart", t["quickStart"]), ("implementor", t["implementor"])]:
        md += f"- {label}: {bar(tr[key])}\n"
    
    md += f"\n### {t['driversTitle']}\n\n"
    for key, label in [("autonomy", t["autonomy"]), ("mastery", t["mastery"]),
                       ("power", t["power"]), ("affiliation", t["affiliation"])]:
        md += f"- {label}: {bar(tr[key])}\n"
    
    md += f"\n---\n\n## {t['darkSide']}\n\n"
    if analysis["stressPatterns"]:
        for p in analysis["stressPatterns"]:
            md += f"- ⚠️ {p}\n"
    
    md += f"\n---\n\n## {t['operationalRules']}\n\n{t['rulesIntro']}\n\n"
    for i, r in enumerate(analysis["operationalRules"]):
        md += f"### Rule {i+1}\n\n{r}\n\n"
    
    md += f"\n---\n\n*{t['disclaimer']}*"
    return md

def get_summary_html(analysis, t, lang):
    """Build a print-ready HTML document for the summary."""
    date_str = format_date(lang)
    tr = analysis["traits"]
    
    def bar_html(label, value, color):
        pct = value * 10
        return f'''<div style="display:flex;align-items:center;gap:12px;padding:5px 0;">
            <span style="width:180px;font-size:10pt;font-weight:500;color:#374151;">{label}</span>
            <div style="flex:1;height:10px;background:#e5e7eb;border-radius:5px;overflow:hidden;">
                <div style="height:100%;width:{pct}%;background:{color};border-radius:5px;"></div>
            </div>
            <span style="width:24px;text-align:right;font-weight:700;font-size:10pt;color:#111827;">{value}</span>
        </div>'''
    
    big5 = "".join([bar_html(t[k], tr[k], "#3b82f6") for k in ["openness","conscientiousness","extraversion","agreeableness","stability"]])
    modes = "".join([bar_html(t[k], tr[k], "#a855f7") for k in ["factFinder","followThru","quickStart","implementor"]])
    drivers = "".join([bar_html(t[k], tr[k], "#ec4899") for k in ["autonomy","mastery","power","affiliation"]])
    
    stress_html = ""
    if analysis["stressPatterns"]:
        stress_html = "<ul>" + "".join([f"<li style='margin:4px 0;'>⚠️ {p}</li>" for p in analysis["stressPatterns"]]) + "</ul>"
    else:
        stress_html = f"<p>{t['completeForAnalysis']}</p>"
    
    env_rows = ""
    pairs = [
        (tr["autonomy"] >= 6, t["highAutonomy"], t["structured"], t["micromanaged"], t["unstructured"]),
        (tr["quickStart"] >= 6, t["fastMoving"], t["methodicalOrg"], t["slowMoving"], t["moveFast"]),
        (tr["extraversion"] >= 6, t["collaborative"], t["deepWork"], t["isolated"], t["constantMeetings"]),
        (tr["mastery"] >= 6, t["learningFocused"], t["executionFocused"], t["stagnant"], t["constantReinvention"]),
    ]
    for cond, thrive_hi, thrive_lo, fail_hi, fail_lo in pairs:
        thrive = thrive_hi if cond else thrive_lo
        fail = fail_hi if cond else fail_lo
        env_rows += f'<tr><td style="padding:6px 12px;border:1px solid #e5e7eb;color:#059669;">✅ {thrive}</td><td style="padding:6px 12px;border:1px solid #e5e7eb;color:#dc2626;">❌ {fail}</td></tr>'
    
    rules_html = ""
    if analysis["operationalRules"]:
        rules_html = "".join([f"<p><strong>Rule {i+1}:</strong> {r}</p>" for i, r in enumerate(analysis["operationalRules"])])
    else:
        rules_html = f'<p style="color:#9ca3af;font-style:italic;">{t["completePhase3"]}</p>'
    
    return f'''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>{t["pdfTitle"]}</title>
    <style>
        @page {{ margin: 20mm 18mm; size: A4; }}
        body {{ font-family: 'Helvetica Neue','Arial',sans-serif; font-size: 10pt; color: #1a1a1a; line-height: 1.5; max-width: 700px; margin: 0 auto; padding: 20px; }}
        @media print {{ body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }} }}
    </style></head><body>
    <h1 style="font-size:22pt;color:#111827;margin:0 0 4px;">{t["pdfTitle"]}</h1>
    <p style="color:#6b7280;margin:0 0 24px;">{t["pdfGenerated"]} {date_str}</p>
    <h2 style="font-size:14pt;border-bottom:2px solid #e5e7eb;padding-bottom:6px;">{t["architecture"]}</h2>
    <h3 style="font-size:11pt;color:#374151;margin-top:16px;">{t["hardwareTitle"]}</h3>{big5}
    <h3 style="font-size:11pt;color:#374151;margin-top:16px;">{t["osTitle"]}</h3>{modes}
    <h3 style="font-size:11pt;color:#374151;margin-top:16px;">{t["driversTitle"]}</h3>{drivers}
    <h2 style="font-size:14pt;border-bottom:2px solid #e5e7eb;padding-bottom:6px;margin-top:28px;">{t["darkSide"]}</h2>
    <p style="font-weight:600;">{t["identifiedDerailers"]}</p>{stress_html}
    <h2 style="font-size:14pt;border-bottom:2px solid #e5e7eb;padding-bottom:6px;margin-top:28px;">{t["environmentFit"]}</h2>
    <table style="border-collapse:collapse;width:100%;margin:8px 0;">
    <tr style="background:#f9fafb;"><th style="padding:8px 12px;border:1px solid #e5e7eb;text-align:left;">{t["thrivesIn"]}</th><th style="padding:8px 12px;border:1px solid #e5e7eb;text-align:left;">{t["failsIn"]}</th></tr>
    {env_rows}</table>
    <h2 style="font-size:14pt;border-bottom:2px solid #e5e7eb;padding-bottom:6px;margin-top:28px;">{t["operationalRules"]}</h2>
    <p style="color:#6b7280;">{t["rulesIntro"]}</p>{rules_html}
    <div style="margin-top:32px;padding-top:12px;border-top:1px solid #e5e7eb;">
    <p style="font-size:8pt;color:#9ca3af;font-style:italic;">{t["disclaimer"]}</p>
    </div></body></html>'''

def generate_deep_analysis(analysis):
    """Call Gemini API to generate the deep analysis."""
    lang_name = "German" if st.session_state.language == "de" else "English"
    lang = st.session_state.language
    t = TRANSLATIONS[lang]
    
    # Build answer summary
    all_qs = get_all_questions(lang)
    lines = []
    for q in all_qs:
        c = get_choice(q["id"])
        if not c:
            continue
        intensity = get_intensity(q["id"])
        i_label = "slightly" if intensity == 1 else ("clearly" if intensity == 2 else "strongly")
        scenario = f'Scenario: {q["scenario"]} | ' if q.get("scenario") else ""
        context = f'Context: {q["context"]} | ' if q.get("context") else ""
        lines.append(f'Q{q["id"]} [{q["category"]}]: {scenario}{context}A: "{q["questionA"]}" | B: "{q["questionB"]}" | CHOSE: {c} ({i_label})')
    answer_summary = "\n".join(lines)
    
    tr = analysis["traits"]
    trait_summary = f"""Big Five (1-10): Openness={tr["openness"]}, Conscientiousness={tr["conscientiousness"]}, Extraversion={tr["extraversion"]}, Agreeableness={tr["agreeableness"]}, Stability={tr["stability"]}
Action Modes (1-10): ResearchDrive={tr["factFinder"]}, SystemsDrive={tr["followThru"]}, LaunchDrive={tr["quickStart"]}, BuildDrive={tr["implementor"]}
Drivers (1-10): Autonomy={tr["autonomy"]}, Mastery={tr["mastery"]}, Power={tr["power"]}, Affiliation={tr["affiliation"]}
Stress Patterns: {', '.join(analysis['stressPatterns']) or 'None'}
Rules: {' | '.join(analysis['operationalRules']) or 'None'}"""

    base_context = f"""You are a world-class Psychometric Analyst. Write in {lang_name}. Be personal, reference specific answers. No filler, no generic advice. Direct style like a trusted advisor. HARD LIMIT: Stay under 300 words. Complete every sentence.

IMPORTANT: Never use trademarked assessment names. Never write "Kolbe", "Hogan", "HDS", "NEO-PI-R", "MBTI", "Myers-Briggs", "DISC", "StrengthsFinder", "CliftonStrengths", or "Enneagram" as product names. Use our own terms: "Research Drive", "Systems Drive", "Launch Drive", "Build Drive" for action modes. Say "Big Five" or "Five Factor" for temperament (these are academic, not trademarked). Say "action modes" not "Kolbe modes". Say "stress derailers" not "HDS scales".

DATA:
{answer_summary}

SCORES:
{trait_summary}{get_followup_data_for_prompt()}"""

    chapters = [
        f"""{base_context}

Write ONLY (max 300 words):

# Deep Psychometric Analysis

## 1. Executive Summary
2 paragraphs: who this person is, their central paradox, what makes their combination unique. Bold and specific.""",

        f"""{base_context}

Write ONLY (max 300 words). No title/summary.

## 2. Temperament: Openness & Conscientiousness

1 focused paragraph per trait: score meaning, how they interact, "close but not you". No fluff.""",

        f"""{base_context}

Write ONLY (max 300 words). No prior sections.

## (continued) Extraversion, Agreeableness & Stability

1 focused paragraph per trait: score meaning, interactions, "close but not you".""",

        f"""{base_context}

Write ONLY (max 300 words). No prior sections.

## 3. Operating System: Action Modes

1 paragraph covering all four action mode dimensions (Research Drive, Systems Drive, Launch Drive, Build Drive): their instinctive approach, what happens when forced against it, how it connects to temperament.""",

        f"""{base_context}

Write ONLY (max 300 words). No prior sections.

## 4. The Drivers: What Fuels and What Drains

Dominant driver, key tension between drivers, what happens when starved. Concrete, no theory.""",

        f"""{base_context}

Write ONLY (max 300 words). No prior sections.

## 5. The Dark Side: Derailers Under Pressure

Name the pattern, trigger sequence, how it manifests, the cost, one early warning sign.""",

        f"""{base_context}

Write ONLY (max 300 words). No prior sections.

## 6. Core Paradoxes

2 paradoxes max. Name each, explain friction, show superpower vs liability. Brief.""",

        f"""{base_context}

Write ONLY (max 300 words). No prior sections.

## 7. Environment Fit

Ideal org/role, 3 red flags, boss type, team dynamics. Bullet-style density, no padding.""",

        f"""{base_context}

Write ONLY (max 300 words). No prior sections.

## 8. Operational Rules

3 rules. Each: bold name, one sentence why, one sentence implementation, circuit breaker phrase. Tight.""",

        f"""{base_context}

Write ONLY (max 250 words). No prior sections.

## 9. Who You Are at Your Best

1-2 paragraphs: peak performance portrait. What it looks like when all systems align. End strong. FINISH the final sentence completely.""",
    ]
    
    # Configure Gemini
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    except Exception as e:
        return f"Error: Could not configure API. Make sure GEMINI_API_KEY is set in secrets. ({e})"
    
    model = genai.GenerativeModel("gemini-2.5-flash")
    full_report = ""
    
    # Create container for live output
    output_container = st.container()
    status_text = st.empty()
    
    for i, prompt in enumerate(chapters):
        status_text.markdown(f"**{'Generiere Kapitel' if lang == 'de' else 'Generating chapter'} {i+1}/{len(chapters)}...**")
        
        try:
            response = model.generate_content(prompt)
            chapter_text = response.text
            full_report += ("\n\n" if full_report else "") + chapter_text
            
            # Show chapter immediately as it's ready
            with output_container:
                st.markdown(chapter_text)
                
        except Exception as e:
            error_msg = f"\n\n> ⚠️ Error in chapter {i+1}: {e}"
            full_report += error_msg
            with output_container:
                st.warning(f"Chapter {i+1} error: {e}")
    
    status_text.empty()
    
    return full_report

def generate_followup_questions():
    """Generate 5 personalized follow-up questions based on all 43 answers."""
    lang = st.session_state.language
    lang_name = "German" if lang == "de" else "English"
    analysis = analyze_results()
    tr = analysis["traits"]
    
    # Build answer summary from ALL questions
    all_qs = get_all_questions(lang)
    lines = []
    for q in all_qs:
        c = get_choice(q["id"])
        if not c:
            continue
        intensity = get_intensity(q["id"])
        i_label = "slightly" if intensity == 1 else ("clearly" if intensity == 2 else "strongly")
        scenario = f'Scenario: {q["scenario"]} | ' if q.get("scenario") else ""
        context = f'Context: {q["context"]} | ' if q.get("context") else ""
        lines.append(f'Q{q["id"]} [{q["category"]}]: {scenario}{context}A: "{q["questionA"]}" | B: "{q["questionB"]}" | CHOSE: {c} ({i_label})')
    answer_summary = "\n".join(lines)
    
    # Stress patterns for prompt
    stress_patterns = []
    if get_choice(21) == "A": stress_patterns.append("Confrontational under pressure")
    if get_choice(21) == "B": stress_patterns.append("Withdrawing under pressure")
    if get_choice(24) == "A": stress_patterns.append("Task-focused in emotional situations")
    if get_choice(27) == "A": stress_patterns.append("Rule-bending when stakes are high")
    if get_choice(30) == "A": stress_patterns.append("Perfectionism under deadline")
    if get_choice(32) == "A": stress_patterns.append("Self-sacrifice pattern")
    if get_choice(35) == "B": stress_patterns.append("Spreading thin under chaos")
    
    prompt = f"""You are a world-class psychometric analyst. Based on the following COMPLETE assessment data (43 questions including stress scenarios and self-designed rules), identify the 5 most interesting TENSIONS or PARADOXES in this person's profile. For each tension, generate a personalized follow-up question with exactly 3 options (A, B, C).

WRITE IN {lang_name}.

TRAIT SCORES (1-10):
Big Five: Openness={tr["openness"]}, Conscientiousness={tr["conscientiousness"]}, Extraversion={tr["extraversion"]}, Agreeableness={tr["agreeableness"]}, Stability={tr["stability"]}
Action Modes: ResearchDrive={tr["factFinder"]}, SystemsDrive={tr["followThru"]}, LaunchDrive={tr["quickStart"]}, BuildDrive={tr["implementor"]}
Drivers: Autonomy={tr["autonomy"]}, Mastery={tr["mastery"]}, Power={tr["power"]}, Affiliation={tr["affiliation"]}
Stress Patterns: {', '.join(stress_patterns) or 'None identified'}

ALL 43 ANSWERS:
{answer_summary}

RULES:
- Generate EXACTLY 5 questions in this order:
  1. TRAIT PARADOX: Two personality traits that create unusual tension
  2. TRAIT PARADOX: A second trait combination that seems contradictory or rare
  3. STRESS PATTERN: How a specific stress behavior contradicts their baseline personality
  4. STRESS PATTERN: A second stress reaction that reveals something unexpected
  5. RULE CONTRADICTION: A mismatch between the rules they chose (Q36-Q43) and their actual behavior in earlier answers
- Each question should reference the SPECIFIC tension you found
- Options A, B, C should represent genuinely different ways the person might experience this tension
- Questions should feel like a coach who just noticed something about you
- Be concrete: reference their actual scores and answer patterns
- Never use trademarked assessment names (no Kolbe, Hogan, MBTI, etc.)

Respond with ONLY a JSON array, no markdown fences, no explanation. Format:
[
  {{"tension": "Short label", "question": "The question text", "optionA": "First option", "optionB": "Second option", "optionC": "Third option"}}
]

Return exactly 5 questions."""

    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        if not api_key:
            return None, "No API key configured"
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Clean markdown fences if present
        text = text.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(text)
        if isinstance(parsed, list) and len(parsed) > 0:
            return parsed, None
        return None, "Invalid response format"
    except Exception as e:
        return None, str(e)

def get_followup_data_for_prompt():
    """Build follow-up answer data string for the deep analysis prompt."""
    fqs = st.session_state.followup_questions
    fas = st.session_state.followup_answers
    if not fqs or not fas:
        return ""
    
    lines = []
    for i, q in enumerate(fqs):
        a = fas.get(i)
        if not a or not a.get("choice"):
            continue
        chosen = q["optionA"] if a["choice"] == "A" else q["optionB"] if a["choice"] == "B" else q["optionC"]
        user_text = f' | USER ADDED: "{a["text"]}"' if a.get("text") else ""
        lines.append(f'TENSION: {q["tension"]}\nQUESTION: {q["question"]}\nCHOSE {a["choice"]}: "{chosen}"{user_text}')
    
    if not lines:
        return ""
    return "\n\nPERSONALIZED FOLLOW-UP ANSWERS (these reveal how the person experiences their core tensions — reference these heavily in your analysis):\n" + "\n\n".join(lines)

def generate_pdf(analysis, t, lang, deep_text=None):
    """Generate a real PDF with trait bars, tables, and optional deep analysis."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor, white, black
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT
    from reportlab.graphics.shapes import Drawing, Rect, String
    from reportlab.graphics import renderPDF
    import io
    
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=20*mm, bottomMargin=20*mm)
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    style_title = ParagraphStyle('Title2', parent=styles['Title'], fontSize=20, textColor=HexColor('#111827'), spaceAfter=4)
    style_subtitle = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=10, textColor=HexColor('#6b7280'), spaceAfter=16)
    style_section = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=13, textColor=HexColor('#111827'), spaceBefore=20, spaceAfter=8, borderWidth=0)
    style_subsection = ParagraphStyle('SubSec', parent=styles['Heading3'], fontSize=10, textColor=HexColor('#374151'), spaceBefore=12, spaceAfter=6)
    style_body = ParagraphStyle('Body2', parent=styles['Normal'], fontSize=9, textColor=HexColor('#374151'), leading=14, spaceAfter=4)
    style_small = ParagraphStyle('Small', parent=styles['Normal'], fontSize=7, textColor=HexColor('#9ca3af'), leading=10)
    style_rule = ParagraphStyle('Rule', parent=styles['Normal'], fontSize=9, textColor=HexColor('#374151'), leading=13, leftIndent=8)
    
    story = []
    tr = analysis["traits"]
    date_str = format_date(lang)
    
    # Title
    story.append(Paragraph(t["pdfTitle"], style_title))
    story.append(Paragraph(f'{t["pdfGenerated"]} {date_str}', style_subtitle))
    
    # Helper: draw trait bar as a Drawing
    def make_bar_drawing(label, value, color_hex):
        d = Drawing(480, 16)
        # Label
        d.add(String(0, 4, label, fontSize=9, fillColor=HexColor('#374151'), fontName='Helvetica'))
        # Bar background
        bar_x = 160
        bar_w = 260
        d.add(Rect(bar_x, 2, bar_w, 10, fillColor=HexColor('#e5e7eb'), strokeColor=None, rx=4, ry=4))
        # Bar fill
        fill_w = max(2, bar_w * value / 10)
        d.add(Rect(bar_x, 2, fill_w, 10, fillColor=HexColor(color_hex), strokeColor=None, rx=4, ry=4))
        # Score
        d.add(String(bar_x + bar_w + 10, 4, str(value), fontSize=9, fillColor=HexColor('#111827'), fontName='Helvetica-Bold'))
        return d
    
    # Architecture section
    story.append(Paragraph(t["architecture"], style_section))
    
    story.append(Paragraph(t["hardwareTitle"], style_subsection))
    for key, label in [("openness", t["openness"]), ("conscientiousness", t["conscientiousness"]),
                       ("extraversion", t["extraversion"]), ("agreeableness", t["agreeableness"]),
                       ("stability", t["stability"])]:
        story.append(make_bar_drawing(label, tr[key], '#3b82f6'))
    
    story.append(Spacer(1, 6))
    story.append(Paragraph(t["osTitle"], style_subsection))
    for key, label in [("factFinder", t["factFinder"]), ("followThru", t["followThru"]),
                       ("quickStart", t["quickStart"]), ("implementor", t["implementor"])]:
        story.append(make_bar_drawing(label, tr[key], '#a855f7'))
    
    story.append(Spacer(1, 6))
    story.append(Paragraph(t["driversTitle"], style_subsection))
    for key, label in [("autonomy", t["autonomy"]), ("mastery", t["mastery"]),
                       ("power", t["power"]), ("affiliation", t["affiliation"])]:
        story.append(make_bar_drawing(label, tr[key], '#ec4899'))
    
    # Contextual Contrasts
    story.append(Paragraph(t["contextualContrasts"], style_section))
    contrast_data = [
        [t["trait"], t["closeButNot"], t["clearlyNot"]],
        [t["decisionSpeed"], t["impulsive"] if get_choice(14)=="A" else t["methodical"], t["paralysis"] if get_choice(14)=="A" else t["gambler"]],
        [t["riskProfile"], t["calcRisk"] if get_choice(15)=="A" else t["steadyOpt"], t["riskAverse"] if get_choice(15)=="A" else t["thrillSeek"]],
        [t["conflictStyle"], t["diplomatic"] if get_choice(16)=="A" else t["harmonious"], t["avoider"] if get_choice(16)=="A" else t["aggressive"]],
        [t["learningMode"], t["experimental"] if get_choice(18)=="A" else t["studious"], t["theoretical"] if get_choice(18)=="A" else t["trialByFire"]],
    ]
    tbl = Table(contrast_data, colWidths=[120, 170, 170])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f9fafb')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#374151')),
        ('TEXTCOLOR', (2, 1), (2, -1), HexColor('#9ca3af')),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e5e7eb')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(tbl)
    
    # Dark Side
    story.append(Paragraph(t["darkSide"], style_section))
    story.append(Paragraph(f'<b>{t["identifiedDerailers"]}</b>', style_body))
    if analysis["stressPatterns"]:
        for p in analysis["stressPatterns"]:
            story.append(Paragraph(f'⚠ {p}', style_rule))
    
    # Environment Fit
    story.append(Paragraph(t["environmentFit"], style_section))
    env_data = [[t["thrivesIn"], t["failsIn"]]]
    pairs = [
        (tr["autonomy"] >= 6, t["highAutonomy"], t["structured"], t["micromanaged"], t["unstructured"]),
        (tr["quickStart"] >= 6, t["fastMoving"], t["methodicalOrg"], t["slowMoving"], t["moveFast"]),
        (tr["extraversion"] >= 6, t["collaborative"], t["deepWork"], t["isolated"], t["constantMeetings"]),
        (tr["mastery"] >= 6, t["learningFocused"], t["executionFocused"], t["stagnant"], t["constantReinvention"]),
    ]
    for cond, hi, lo, fail_hi, fail_lo in pairs:
        env_data.append([f'✓ {hi if cond else lo}', f'✗ {fail_hi if cond else fail_lo}'])
    
    env_tbl = Table(env_data, colWidths=[230, 230])
    env_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f9fafb')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 1), (0, -1), HexColor('#059669')),
        ('TEXTCOLOR', (1, 1), (1, -1), HexColor('#dc2626')),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#e5e7eb')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(env_tbl)
    
    # Operational Rules
    story.append(Paragraph(t["operationalRules"], style_section))
    story.append(Paragraph(f'<i>{t["rulesIntro"]}</i>', style_body))
    if analysis["operationalRules"]:
        for i, rule in enumerate(analysis["operationalRules"]):
            story.append(Paragraph(f'<b>Rule {i+1}:</b> ✓ {rule}', style_rule))
    
    # Deep Analysis
    if deep_text:
        story.append(PageBreak())
        for line in deep_text.split('\n'):
            stripped = line.strip()
            if not stripped:
                story.append(Spacer(1, 4))
            elif stripped.startswith('# ') and not stripped.startswith('## '):
                story.append(Paragraph(stripped[2:], style_title))
            elif stripped.startswith('## '):
                story.append(Paragraph(stripped[3:], style_section))
            elif stripped.startswith('### '):
                story.append(Paragraph(stripped[4:], style_subsection))
            elif stripped.startswith('> '):
                quote_style = ParagraphStyle('Quote', parent=style_body, leftIndent=12, textColor=HexColor('#374151'), fontName='Helvetica-Oblique', backColor=HexColor('#f5f3ff'))
                story.append(Paragraph(stripped[2:], quote_style))
            elif stripped.startswith('- ') or stripped.startswith('* '):
                story.append(Paragraph(f'• {stripped[2:]}', style_rule))
            elif stripped == '---':
                story.append(Spacer(1, 8))
            else:
                # Handle inline bold
                import re
                cleaned = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', stripped)
                story.append(Paragraph(cleaned, style_body))
    
    # Disclaimer
    story.append(Spacer(1, 20))
    story.append(Paragraph(t["disclaimer"], style_small))
    
    doc.build(story)
    buf.seek(0)
    return buf.getvalue()

# ============================================================
# INITIALIZE SESSION STATE
# ============================================================
if "language" not in st.session_state:
    st.session_state.language = None
if "page" not in st.session_state:
    st.session_state.page = "language"  # language, intro, questions, results
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "pending_choice" not in st.session_state:
    st.session_state.pending_choice = None
if "deep_analysis" not in st.session_state:
    st.session_state.deep_analysis = ""
if "followup_questions" not in st.session_state:
    st.session_state.followup_questions = []
if "followup_answers" not in st.session_state:
    st.session_state.followup_answers = {}
if "followup_index" not in st.session_state:
    st.session_state.followup_index = 0
if "followup_error" not in st.session_state:
    st.session_state.followup_error = None

# ============================================================
# PAGE: LANGUAGE SELECTION
# ============================================================
if st.session_state.page == "language":
    st.markdown("<div style='text-align:center;padding-top:60px;'>", unsafe_allow_html=True)
    st.markdown("# 🧠")
    st.markdown("### Select Your Language / Wählen Sie Ihre Sprache")
    st.markdown("</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🇬🇧  English", use_container_width=True, type="primary"):
            st.session_state.language = "en"
            st.session_state.page = "intro"
            st.rerun()
    with col2:
        if st.button("🇩🇪  Deutsch", use_container_width=True, type="primary"):
            st.session_state.language = "de"
            st.session_state.page = "intro"
            st.rerun()

# ============================================================
# PAGE: INTRO
# ============================================================
elif st.session_state.page == "intro":
    t = TRANSLATIONS[st.session_state.language]
    
    st.markdown(f"# 🧠 {t['title']}")
    st.markdown(f"*{t['subtitle']}*")
    st.markdown("---")
    
    st.markdown(f"### {t['phase1Title']}")
    st.markdown(t['phase1Desc'])
    st.markdown(f"### {t['phase2Title']}")
    st.markdown(t['phase2Desc'])
    st.markdown(f"### {t['phase3Title']}")
    st.markdown(t['phase3Desc'])
    
    st.markdown("---")
    st.markdown(f"**{t['formatNote']}** {t['formatDesc']}")
    
    if st.button(t['beginBtn'], type="primary", use_container_width=True):
        st.session_state.page = "questions"
        st.session_state.current_index = 0
        st.session_state.answers = {}
        st.rerun()

# ============================================================
# PAGE: QUESTIONS
# ============================================================
elif st.session_state.page == "questions":
    lang = st.session_state.language
    t = TRANSLATIONS[lang]
    all_qs = get_all_questions(lang)
    total = len(all_qs)
    idx = st.session_state.current_index
    q = all_qs[idx]
    
    # Determine phase
    disc_len = len(QUESTIONS[lang]["discovery"])
    stress_len = len(QUESTIONS[lang]["stressTesting"])
    if idx < disc_len:
        phase_name = t["phase1Title"]
        phase_color = "#3b82f6"
    elif idx < disc_len + stress_len:
        phase_name = t["phase2Title"]
        phase_color = "#f59e0b"
    else:
        phase_name = t["phase3Title"]
        phase_color = "#10b981"
    
    # Progress bar
    st.progress((idx + 1) / total)
    
    col_phase, col_count = st.columns([3, 1])
    with col_phase:
        st.markdown(f'<span style="color:{phase_color};font-weight:600;font-size:14px;">{phase_name}</span>', unsafe_allow_html=True)
    with col_count:
        st.markdown(f'<span style="color:#94a3b8;font-size:14px;float:right;">{idx+1} / {total}</span>', unsafe_allow_html=True)
    
    # Skip button — tiny, at bottom for dev only
    # (moved to after the question card)
    
    # Category badge
    st.markdown(f'<div class="category-badge" style="background:{phase_color}22;color:{phase_color};">{q["category"]}</div>', unsafe_allow_html=True)
    
    # Scenario or context
    if q.get("scenario"):
        st.markdown(f'<div class="scenario-box">{q["scenario"]}</div>', unsafe_allow_html=True)
    if q.get("context"):
        st.markdown(f'<div class="context-box">{q["context"]}</div>', unsafe_allow_html=True)
    
    pending = st.session_state.pending_choice
    
    # If no choice made yet, show A/B options
    if pending is None:
        st.markdown(f"**{t['choosePrompt']}**")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button(f"🅰️  {q['questionA']}", use_container_width=True, key=f"a_{q['id']}"):
                st.session_state.pending_choice = "A"
                st.rerun()
        with col_b:
            if st.button(f"🅱️  {q['questionB']}", use_container_width=True, key=f"b_{q['id']}"):
                st.session_state.pending_choice = "B"
                st.rerun()
    else:
        # Show selected choice and intensity buttons
        chosen_text = q["questionA"] if pending == "A" else q["questionB"]
        chosen_label = "🅰️" if pending == "A" else "🅱️"
        chosen_color = "#3b82f6" if pending == "A" else "#8b5cf6"
        
        st.markdown(f'<div style="padding:12px 16px;border-radius:8px;border:2px solid {chosen_color};background:{chosen_color}22;color:#e2e8f0;margin-bottom:16px;">{chosen_label} {chosen_text}</div>', unsafe_allow_html=True)
        
        st.markdown(f"**{t['howStrongly']}**")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(f"● {t['slightly']}", use_container_width=True, key="int_1"):
                st.session_state.answers[q["id"]] = {"choice": pending, "intensity": 1}
                st.session_state.pending_choice = None
                if idx + 1 < total:
                    st.session_state.current_index = idx + 1
                else:
                    st.session_state.page = "followup"
                st.rerun()
        with col2:
            if st.button(f"●● {t['clearly']}", use_container_width=True, key="int_2"):
                st.session_state.answers[q["id"]] = {"choice": pending, "intensity": 2}
                st.session_state.pending_choice = None
                if idx + 1 < total:
                    st.session_state.current_index = idx + 1
                else:
                    st.session_state.page = "followup"
                st.rerun()
        with col3:
            if st.button(f"●●● {t['strongly']}", use_container_width=True, key="int_3"):
                st.session_state.answers[q["id"]] = {"choice": pending, "intensity": 3}
                st.session_state.pending_choice = None
                if idx + 1 < total:
                    st.session_state.current_index = idx + 1
                else:
                    st.session_state.page = "followup"
                st.rerun()
    
    # Back button
    st.markdown("---")
    if pending is not None:
        if st.button(t["back"], key="back_intensity"):
            st.session_state.pending_choice = None
            st.rerun()
    elif idx > 0:
        if st.button(t["back"], key="back_question"):
            st.session_state.current_index = idx - 1
            st.session_state.pending_choice = None
            st.rerun()
    
    # Dev skip — almost invisible
    import random
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("skip", key="dev_skip", type="secondary"):
        for qq in all_qs:
            st.session_state.answers[qq["id"]] = {
                "choice": random.choice(["A", "B"]),
                "intensity": random.randint(1, 3)
            }
        st.session_state.page = "followup"
        st.session_state.pending_choice = None
        st.rerun()

# ============================================================
# PAGE: FOLLOW-UP (Phase 1.5)
# ============================================================
elif st.session_state.page == "followup":
    lang = st.session_state.language
    t = TRANSLATIONS[lang]
    fqs = st.session_state.followup_questions
    fi = st.session_state.followup_index
    
    # Generate questions if not yet done
    if not fqs and not st.session_state.followup_error:
        with st.spinner(
            "Etwas ist mir aufgefallen... Basierend auf Ihren Antworten erstelle ich gezielte Nachfragen." if lang == "de"
            else "Something caught my attention... Crafting targeted follow-up questions based on your answers."
        ):
            questions, error = generate_followup_questions()
            if questions:
                st.session_state.followup_questions = questions
                st.session_state.followup_index = 0
                st.rerun()
            else:
                st.session_state.followup_error = error
                st.rerun()
    
    # Error state
    if st.session_state.followup_error:
        st.warning(
            "Persönliche Fragen konnten nicht generiert werden. Bitte versuchen Sie es erneut." if lang == "de"
            else "Could not generate personal questions. Please try again."
        )
        col_back, col_retry, col_skip = st.columns(3)
        with col_back:
            if st.button("← " + ("Zurück" if lang == "de" else "Back"), use_container_width=True):
                st.session_state.page = "questions"
                st.session_state.current_index = 42  # Last question
                st.rerun()
        with col_retry:
            if st.button("🔄 " + ("Erneut" if lang == "de" else "Retry"), use_container_width=True, type="primary"):
                st.session_state.followup_error = None
                st.session_state.followup_questions = []
                st.rerun()
        with col_skip:
            if st.button("→ " + ("Weiter" if lang == "de" else "Skip"), use_container_width=True):
                st.session_state.page = "results"
                st.rerun()
    
    # Show follow-up questions
    elif fqs and fi < len(fqs):
        fuq = fqs[fi]
        fua = st.session_state.followup_answers.get(fi, {})
        
        # Header
        st.markdown(f"""
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
            <div style="display:flex;align-items:center;gap:8px;">
                <div style="width:10px;height:10px;background:#06b6d4;border-radius:50%;animation:pulse 2s infinite;"></div>
                <span style="font-size:13px;font-weight:700;color:#06b6d4;">
                    {"PERSÖNLICHE VERTIEFUNG" if lang == "de" else "PERSONAL DEEP-DIVE"}
                </span>
            </div>
            <span style="font-size:13px;color:#64748b;">{fi + 1} / {len(fqs)}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Tension badge
        st.markdown(f"""
        <div style="background:#0e374a;border:1px solid #164e63;border-radius:10px;padding:10px 14px;margin-bottom:16px;">
            <span style="color:#06b6d4;font-size:13px;font-weight:500;">
                🔍 {"Erkannte Spannung:" if lang == "de" else "Detected tension:"} 
                <strong>{fuq["tension"]}</strong>
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        # Question
        st.markdown(f"**{fuq['question']}**")
        
        # Options A, B, C
        current_choice = fua.get("choice")
        
        options = [
            ("A", fuq["optionA"], "#3b82f6"),
            ("B", fuq["optionB"], "#8b5cf6"),
            ("C", fuq["optionC"], "#10b981"),
        ]
        
        for key, text, color in options:
            is_selected = current_choice == key
            if st.button(
                f"{key})  {text}",
                use_container_width=True,
                key=f"fu_{fi}_{key}",
                type="primary" if is_selected else "secondary"
            ):
                answers = st.session_state.followup_answers.copy()
                answers[fi] = {**answers.get(fi, {}), "choice": key}
                st.session_state.followup_answers = answers
                st.rerun()
        
        # Optional text
        st.markdown("")
        text_val = fua.get("text", "")
        new_text = st.text_area(
            "💬 " + ("Kontext hinzufügen? (optional)" if lang == "de" else "Want to add context? (optional)"),
            value=text_val,
            placeholder="Ihre Erfahrung in 1-2 Sätzen..." if lang == "de" else "Your experience in 1-2 sentences...",
            height=68,
            key=f"fu_text_{fi}"
        )
        if new_text != text_val:
            answers = st.session_state.followup_answers.copy()
            answers[fi] = {**answers.get(fi, {}), "text": new_text}
            st.session_state.followup_answers = answers
        
        # Navigation
        st.markdown("---")
        col_back, col_next = st.columns([1, 3])
        with col_back:
            if fi > 0:
                if st.button("← " + ("Zurück" if lang == "de" else "Back"), key="fu_back", use_container_width=True):
                    st.session_state.followup_index = fi - 1
                    st.rerun()
        with col_next:
            has_choice = bool(st.session_state.followup_answers.get(fi, {}).get("choice"))
            next_label = ("Ergebnisse anzeigen →" if lang == "de" else "View Results →") if fi == len(fqs) - 1 else ("Weiter →" if lang == "de" else "Next →")
            if st.button(next_label, use_container_width=True, type="primary", disabled=not has_choice, key="fu_next"):
                if fi < len(fqs) - 1:
                    st.session_state.followup_index = fi + 1
                else:
                    st.session_state.page = "results"
                st.rerun()
        
        # Skip link
        if st.button(
            "Vertiefung überspringen →" if lang == "de" else "Skip deep-dive →",
            key="fu_skip",
            type="secondary"
        ):
            st.session_state.page = "results"
            st.rerun()

# ============================================================
# PAGE: RESULTS
# ============================================================
elif st.session_state.page == "results":
    lang = st.session_state.language
    t = TRANSLATIONS[lang]
    analysis = analyze_results()
    tr = analysis["traits"]
    
    st.markdown(f"# 🧠 {t['pdfTitle']}")
    date_str = format_date(lang)
    st.markdown(f"*{t['pdfGenerated']} {date_str}*")
    
    # ---- SUMMARY SECTION ----
    # Architecture
    st.markdown(f'<div class="section-header">{t["architecture"]}</div>', unsafe_allow_html=True)
    
    st.markdown(f"**{t['hardwareTitle']}**")
    for key in ["openness", "conscientiousness", "extraversion", "agreeableness", "stability"]:
        render_trait_bar(t[key], tr[key], "#3b82f6")
    
    st.markdown(f"**{t['osTitle']}**")
    for key in ["factFinder", "followThru", "quickStart", "implementor"]:
        render_trait_bar(t[key], tr[key], "#a855f7")
    
    st.markdown(f"**{t['driversTitle']}**")
    for key in ["autonomy", "mastery", "power", "affiliation"]:
        render_trait_bar(t[key], tr[key], "#ec4899")
    
    # Contextual Contrasts
    st.markdown(f'<div class="section-header">{t["contextualContrasts"]}</div>', unsafe_allow_html=True)
    
    contrasts = [
        (t["decisionSpeed"], 
         t["impulsive"] if get_choice(14) == "A" else t["methodical"],
         t["paralysis"] if get_choice(14) == "A" else t["gambler"]),
        (t["riskProfile"],
         t["calcRisk"] if get_choice(15) == "A" else t["steadyOpt"],
         t["riskAverse"] if get_choice(15) == "A" else t["thrillSeek"]),
        (t["conflictStyle"],
         t["diplomatic"] if get_choice(16) == "A" else t["harmonious"],
         t["avoider"] if get_choice(16) == "A" else t["aggressive"]),
        (t["learningMode"],
         t["experimental"] if get_choice(18) == "A" else t["studious"],
         t["theoretical"] if get_choice(18) == "A" else t["trialByFire"]),
    ]
    
    contrast_html = f'<table class="styled-table"><tr><th>{t["trait"]}</th><th>{t["closeButNot"]}</th><th>{t["clearlyNot"]}</th></tr>'
    for trait, close, not_you in contrasts:
        contrast_html += f"<tr><td style='font-weight:600;'>{trait}</td><td>{close}</td><td style='color:#64748b;'>{not_you}</td></tr>"
    contrast_html += "</table>"
    st.markdown(contrast_html, unsafe_allow_html=True)
    
    # Dark Side
    st.markdown(f'<div class="section-header">{t["darkSide"]}</div>', unsafe_allow_html=True)
    if analysis["stressPatterns"]:
        for p in analysis["stressPatterns"]:
            st.markdown(f"⚠️ {p}")
    else:
        st.info(t["completeForAnalysis"])
    
    # Environment Fit
    st.markdown(f'<div class="section-header">{t["environmentFit"]}</div>', unsafe_allow_html=True)
    env_html = f'<table class="styled-table"><tr><th>{t["thrivesIn"]}</th><th>{t["failsIn"]}</th></tr>'
    pairs = [
        (tr["autonomy"] >= 6, t["highAutonomy"], t["structured"], t["micromanaged"], t["unstructured"]),
        (tr["quickStart"] >= 6, t["fastMoving"], t["methodicalOrg"], t["slowMoving"], t["moveFast"]),
        (tr["extraversion"] >= 6, t["collaborative"], t["deepWork"], t["isolated"], t["constantMeetings"]),
        (tr["mastery"] >= 6, t["learningFocused"], t["executionFocused"], t["stagnant"], t["constantReinvention"]),
    ]
    for cond, hi, lo, fail_hi, fail_lo in pairs:
        thrive = hi if cond else lo
        fail = fail_hi if cond else fail_lo
        env_html += f'<tr><td style="color:#10b981;">✅ {thrive}</td><td style="color:#ef4444;">❌ {fail}</td></tr>'
    env_html += "</table>"
    st.markdown(env_html, unsafe_allow_html=True)
    
    # Operational Rules
    st.markdown(f'<div class="section-header">{t["operationalRules"]}</div>', unsafe_allow_html=True)
    st.markdown(f"*{t['rulesIntro']}*")
    if analysis["operationalRules"]:
        for i, rule in enumerate(analysis["operationalRules"]):
            rule_label = "Regel" if lang == "de" else "Rule"
            st.markdown(f"**{rule_label} {i+1}:** {rule}")
    else:
        st.info(t["completePhase3"])
    
    # ---- DEEP ANALYSIS SECTION ----
    st.markdown("---")
    st.markdown("### 🔮 " + ("KI-gestützte Tiefenanalyse" if lang == "de" else "AI-Powered Deep Analysis"))
    
    if not st.session_state.deep_analysis:
        # Auto-start generation with loading message
        st.markdown(
            "*Generiere Ihre persönliche Tiefenanalyse...*" if lang == "de"
            else "*Generating your personalized deep analysis...*"
        )
        result = generate_deep_analysis(analysis)
        st.session_state.deep_analysis = result
        st.rerun()
    else:
        st.markdown(st.session_state.deep_analysis)
        
        # Download buttons (only shown after deep analysis is generated)
        st.markdown("---")
        col_md, col_pdf, col_redo = st.columns(3)
        with col_md:
            # Combined markdown: summary + deep analysis
            combined_md = get_summary_markdown(analysis, t, lang) + "\n\n---\n\n" + st.session_state.deep_analysis
            st.download_button(
                label="📄 .md",
                data=combined_md,
                file_name=f"user-manual-{datetime.now().strftime('%Y-%m-%d')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        with col_pdf:
            pdf_complete = generate_pdf(analysis, t, lang, deep_text=st.session_state.deep_analysis)
            st.download_button(
                label="📕 .pdf",
                data=pdf_complete,
                file_name=f"user-manual-{datetime.now().strftime('%Y-%m-%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        with col_redo:
            if st.button("🔄 " + ("Neu" if lang == "de" else "Redo"), use_container_width=True):
                st.session_state.deep_analysis = ""
                st.rerun()
    
    # Disclaimer + Start Over
    st.markdown("---")
    st.caption(t["disclaimer"])
    
    if st.button(t["startOver"], use_container_width=True):
        st.session_state.language = None
        st.session_state.page = "language"
        st.session_state.current_index = 0
        st.session_state.answers = {}
        st.session_state.pending_choice = None
        st.session_state.deep_analysis = ""
        st.session_state.followup_questions = []
        st.session_state.followup_answers = {}
        st.session_state.followup_index = 0
        st.session_state.followup_error = None
        st.rerun()
