import streamlit as st
import google.generativeai as genai
import json
import math
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
    }
    .styled-table th, .styled-table td {
        padding: 10px 14px;
        border: 1px solid #334155;
        text-align: left;
    }
    .styled-table th {
        background: #1e293b;
        font-weight: 600;
        color: #94a3b8;
    }
    .styled-table td {
        color: #cbd5e1;
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
</style>
""", unsafe_allow_html=True)

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
            {"id": 1, "category": "Big Five - Openness", "questionA": "You prefer to master one domain deeply, becoming the undisputed expert", "questionB": "You prefer to explore many domains broadly, connecting unexpected dots"},
            {"id": 2, "category": "Big Five - Conscientiousness", "questionA": "You finish what you start, even when the project becomes tedious", "questionB": "You pivot quickly when something more promising appears"},
            {"id": 3, "category": "Big Five - Extraversion", "questionA": "Your best ideas come from intense conversations with others", "questionB": "Your best ideas come from solitary deep work"},
            {"id": 4, "category": "Big Five - Agreeableness", "questionA": "You'd rather be respected than liked", "questionB": "You'd rather be liked than respected"},
            {"id": 5, "category": "Big Five - Neuroticism", "questionA": "Anxiety often drives your best work—it keeps you sharp", "questionB": "You perform best when you feel calm and secure"},
            {"id": 6, "category": "Action Mode - Research", "questionA": "Before deciding, you need comprehensive data and research", "questionB": "You trust your gut and gather data only when stuck"},
            {"id": 7, "category": "Action Mode - Systems", "questionA": "You create systems and processes to organize chaos", "questionB": "You resist systems—they feel like constraints"},
            {"id": 8, "category": "Action Mode - Launch", "questionA": "You'd rather launch imperfectly today than perfectly next month", "questionB": "You'd rather delay until the plan is bulletproof"},
            {"id": 9, "category": "Action Mode - Build", "questionA": "You think best with tangible prototypes and physical objects", "questionB": "You think best with abstractions, models, and frameworks"},
            {"id": 10, "category": "Core Driver - Autonomy", "questionA": "You'd take a 30% pay cut for complete control over your work", "questionB": "You'd accept less autonomy for higher compensation and resources"},
            {"id": 11, "category": "Core Driver - Mastery", "questionA": "You'd rather be world-class at one thing than very good at five", "questionB": "You'd rather be versatile across many areas than specialized in one"},
            {"id": 12, "category": "Core Driver - Power", "questionA": "You naturally gravitate toward leading and directing others", "questionB": "You prefer influencing outcomes without formal authority"},
            {"id": 13, "category": "Core Driver - Affiliation", "questionA": "Working with a great team is more important than the work itself", "questionB": "The work itself is more important than who you do it with"},
            {"id": 14, "category": "Decision Making", "questionA": "You decide quickly and correct course later if needed", "questionB": "You decide slowly to minimize the need for corrections"},
            {"id": 15, "category": "Risk Orientation", "questionA": "You're energized by high-stakes, high-reward situations", "questionB": "You prefer steady progress over volatile swings"},
            {"id": 16, "category": "Conflict Style", "questionA": "You address conflicts directly, even if it's uncomfortable", "questionB": "You prefer indirect approaches that preserve harmony"},
            {"id": 17, "category": "Time Orientation", "questionA": "You're primarily motivated by future possibilities", "questionB": "You're primarily motivated by present experiences"},
            {"id": 18, "category": "Learning Style", "questionA": "You learn best by doing and making mistakes", "questionB": "You learn best by studying and observing first"},
            {"id": 19, "category": "Success Definition", "questionA": "Success means building something that outlasts you", "questionB": "Success means maximizing freedom and experiences"},
            {"id": 20, "category": "Feedback Response", "questionA": "Critical feedback energizes you to improve", "questionB": "Critical feedback requires time to process emotionally first"},
        ],
        "stressTesting": [
            {"id": 21, "category": "Stress - Volatility", "scenario": "Your co-founder just pivoted the company strategy without consulting you.", "questionA": "You confront them immediately, risking a heated argument", "questionB": "You withdraw to process, risking them thinking you agree"},
            {"id": 22, "category": "Stress - Skepticism", "scenario": "A new team member's proposal would change your core product.", "questionA": "You challenge their assumptions publicly to stress-test the idea", "questionB": "You privately investigate their background and motives first"},
            {"id": 23, "category": "Stress - Caution", "scenario": "A competitor just launched a feature you were developing.", "questionA": "You rush to ship your version within 48 hours, bugs and all", "questionB": "You pause to differentiate, risking being seen as 'too slow'"},
            {"id": 24, "category": "Stress - Detachment", "scenario": "Your team needs emotional support after a major setback.", "questionA": "You focus on solving the problem—emotions can wait", "questionB": "You put the problem aside to address the team's morale first"},
            {"id": 25, "category": "Stress - Passive Resistance", "scenario": "Leadership demands you implement a policy you disagree with.", "questionA": "You comply visibly but subtly slow down execution", "questionB": "You openly argue against it, risking being labeled 'difficult'"},
            {"id": 26, "category": "Stress - Overconfidence", "scenario": "You're asked to present after a colleague who delivered brilliantly.", "questionA": "You amplify your presence to match their energy", "questionB": "You stay understated, trusting your content to speak"},
            {"id": 27, "category": "Stress - Risk-Taking", "scenario": "You see a shortcut that bends company rules but saves the quarter.", "questionA": "You take it—results matter more than process", "questionB": "You flag the issue and miss the target this quarter"},
            {"id": 28, "category": "Stress - Attention-Seeking", "scenario": "A critical negotiation requires you to be silent and let the other party talk.", "questionA": "You struggle—your instinct is to fill silence with energy", "questionB": "You adapt easily—you can modulate your presence at will"},
            {"id": 29, "category": "Stress - Eccentricity", "scenario": "Your unconventional strategy was just called 'impractical' by the board.", "questionA": "You double down—they just don't see the vision yet", "questionB": "You recalibrate to find a more conventional path to the goal"},
            {"id": 30, "category": "Stress - Perfectionism", "scenario": "A 'good enough' solution exists, but a perfect one needs 3 more weeks.", "questionA": "You push for the 3 weeks—quality is non-negotiable", "questionB": "You ship 'good enough'—momentum beats perfection"},
            {"id": 31, "category": "Stress - Compliance", "scenario": "Your mentor advises a path you believe is wrong for you.", "questionA": "You follow their advice—they've earned that trust", "questionB": "You respectfully disagree and go your own way"},
            {"id": 32, "category": "Burnout Pattern", "scenario": "You've worked 70-hour weeks for a month. A vacation is planned but a crisis emerges.", "questionA": "You cancel the vacation—the team needs you", "questionB": "You delegate and go—you're no good to anyone burned out"},
            {"id": 33, "category": "Failure Response", "scenario": "A project you championed just failed publicly.", "questionA": "You immediately analyze what went wrong and share learnings", "questionB": "You need distance before you can process objectively"},
            {"id": 34, "category": "Trust Repair", "scenario": "Someone you trusted just took credit for your work.", "questionA": "You address it directly with them first", "questionB": "You ensure others know the truth before confronting them"},
            {"id": 35, "category": "Control Under Chaos", "scenario": "Everything is going wrong at once—team conflict, cash crisis, product issues.", "questionA": "You triage ruthlessly, letting some fires burn", "questionB": "You try to address everything, spreading yourself thin"},
        ],
        "solutionDesign": [
            {"id": 36, "category": "Rule Design - Boundaries", "context": "Based on your stress responses, you may over-extend under pressure.", "questionA": "You need hard calendar blocks that are non-negotiable", "questionB": "You need a trusted person who can veto your commitments"},
            {"id": 37, "category": "Rule Design - Decision Making", "context": "Your decision style may lead to either over-analysis or under-analysis.", "questionA": "You need forced deadlines to prevent over-thinking", "questionB": "You need mandatory cooling-off periods to prevent under-thinking"},
            {"id": 38, "category": "Rule Design - Feedback", "context": "Your response to criticism affects your growth trajectory.", "questionA": "You need structured, scheduled feedback sessions", "questionB": "You need real-time, informal feedback loops"},
            {"id": 39, "category": "Rule Design - Energy Management", "context": "Your energy patterns affect your output quality.", "questionA": "You need to front-load difficult work when fresh", "questionB": "You need to warm up with easy wins before tackling hard problems"},
            {"id": 40, "category": "Rule Design - Relationships", "context": "Your interpersonal style has specific friction points.", "questionA": "You need to practice more patience with slower thinkers", "questionB": "You need to practice more assertiveness with dominant personalities"},
            {"id": 41, "category": "Rule Design - Blind Spots", "context": "Everyone has patterns they can't see in themselves.", "questionA": "You tend to overestimate your capacity and underestimate time needed", "questionB": "You tend to underestimate your abilities and over-prepare"},
            {"id": 42, "category": "Rule Design - Recovery", "context": "Your recovery pattern after setbacks affects long-term performance.", "questionA": "You recover through action—doing something productive", "questionB": "You recover through stillness—reflection and rest"},
            {"id": 43, "category": "Rule Design - Accountability", "context": "Your accountability structure affects follow-through.", "questionA": "You need external accountability to stay on track", "questionB": "You need internal systems—external pressure creates resistance"},
        ],
    },
    "de": {
        "discovery": [
            {"id": 1, "category": "Big Five - Offenheit", "questionA": "Sie bevorzugen es, einen Bereich tief zu meistern und der unbestrittene Experte zu werden", "questionB": "Sie bevorzugen es, viele Bereiche breit zu erkunden und unerwartete Verbindungen herzustellen"},
            {"id": 2, "category": "Big Five - Gewissenhaftigkeit", "questionA": "Sie beenden, was Sie beginnen, auch wenn das Projekt mühsam wird", "questionB": "Sie wechseln schnell, wenn etwas Vielversprechenderes auftaucht"},
            {"id": 3, "category": "Big Five - Extraversion", "questionA": "Ihre besten Ideen entstehen aus intensiven Gesprächen mit anderen", "questionB": "Ihre besten Ideen entstehen aus einsamer, tiefer Arbeit"},
            {"id": 4, "category": "Big Five - Verträglichkeit", "questionA": "Sie möchten lieber respektiert als gemocht werden", "questionB": "Sie möchten lieber gemocht als respektiert werden"},
            {"id": 5, "category": "Big Five - Neurotizismus", "questionA": "Angst treibt oft Ihre beste Arbeit an—sie hält Sie scharf", "questionB": "Sie leisten am besten, wenn Sie sich ruhig und sicher fühlen"},
            {"id": 6, "category": "Handlungsmodus - Recherche", "questionA": "Vor Entscheidungen brauchen Sie umfassende Daten und Recherche", "questionB": "Sie vertrauen Ihrem Bauchgefühl und sammeln Daten nur wenn Sie feststecken"},
            {"id": 7, "category": "Handlungsmodus - Systeme", "questionA": "Sie schaffen Systeme und Prozesse, um Chaos zu organisieren", "questionB": "Sie widersetzen sich Systemen—sie fühlen sich wie Einschränkungen an"},
            {"id": 8, "category": "Handlungsmodus - Umsetzung", "questionA": "Sie starten lieber heute unvollkommen als nächsten Monat perfekt", "questionB": "Sie verzögern lieber, bis der Plan kugelsicher ist"},
            {"id": 9, "category": "Handlungsmodus - Bau", "questionA": "Sie denken am besten mit greifbaren Prototypen und physischen Objekten", "questionB": "Sie denken am besten mit Abstraktionen, Modellen und Frameworks"},
            {"id": 10, "category": "Kernantrieb - Autonomie", "questionA": "Sie würden 30% Gehaltskürzung für vollständige Kontrolle über Ihre Arbeit akzeptieren", "questionB": "Sie würden weniger Autonomie für höhere Vergütung und Ressourcen akzeptieren"},
            {"id": 11, "category": "Kernantrieb - Meisterschaft", "questionA": "Sie wären lieber weltklasse in einer Sache als sehr gut in fünf", "questionB": "Sie wären lieber vielseitig in vielen Bereichen als spezialisiert in einem"},
            {"id": 12, "category": "Kernantrieb - Macht", "questionA": "Sie tendieren natürlich dazu, andere zu führen und zu leiten", "questionB": "Sie bevorzugen es, Ergebnisse ohne formale Autorität zu beeinflussen"},
            {"id": 13, "category": "Kernantrieb - Zugehörigkeit", "questionA": "Mit einem großartigen Team zu arbeiten ist wichtiger als die Arbeit selbst", "questionB": "Die Arbeit selbst ist wichtiger als mit wem Sie sie machen"},
            {"id": 14, "category": "Entscheidungsfindung", "questionA": "Sie entscheiden schnell und korrigieren später bei Bedarf", "questionB": "Sie entscheiden langsam, um Korrekturen zu minimieren"},
            {"id": 15, "category": "Risikoorientierung", "questionA": "Sie werden von Hochrisiko-Hochbelohnungs-Situationen angetrieben", "questionB": "Sie bevorzugen stetigen Fortschritt gegenüber volatilen Schwankungen"},
            {"id": 16, "category": "Konfliktstil", "questionA": "Sie sprechen Konflikte direkt an, auch wenn es unangenehm ist", "questionB": "Sie bevorzugen indirekte Ansätze, die Harmonie bewahren"},
            {"id": 17, "category": "Zeitorientierung", "questionA": "Sie werden hauptsächlich von zukünftigen Möglichkeiten motiviert", "questionB": "Sie werden hauptsächlich von gegenwärtigen Erfahrungen motiviert"},
            {"id": 18, "category": "Lernstil", "questionA": "Sie lernen am besten durch Tun und Fehler machen", "questionB": "Sie lernen am besten durch Studieren und Beobachten zuerst"},
            {"id": 19, "category": "Erfolgsdefinition", "questionA": "Erfolg bedeutet, etwas zu bauen, das Sie überdauert", "questionB": "Erfolg bedeutet, Freiheit und Erfahrungen zu maximieren"},
            {"id": 20, "category": "Feedback-Reaktion", "questionA": "Kritisches Feedback motiviert Sie zur Verbesserung", "questionB": "Kritisches Feedback braucht Zeit zur emotionalen Verarbeitung"},
        ],
        "stressTesting": [
            {"id": 21, "category": "Stress - Volatilität", "scenario": "Ihr Mitgründer hat gerade die Unternehmensstrategie ohne Rücksprache geändert.", "questionA": "Sie konfrontieren ihn sofort und riskieren einen hitzigen Streit", "questionB": "Sie ziehen sich zurück zum Verarbeiten und riskieren, dass er denkt Sie stimmen zu"},
            {"id": 22, "category": "Stress - Skepsis", "scenario": "Der Vorschlag eines neuen Teammitglieds würde Ihr Kernprodukt ändern.", "questionA": "Sie hinterfragen ihre Annahmen öffentlich, um die Idee zu testen", "questionB": "Sie recherchieren privat ihren Hintergrund und ihre Motive zuerst"},
            {"id": 23, "category": "Stress - Vorsicht", "scenario": "Ein Wettbewerber hat gerade ein Feature gelauncht, das Sie entwickelten.", "questionA": "Sie beeilen sich, Ihre Version innerhalb von 48 Stunden zu veröffentlichen, mit Bugs", "questionB": "Sie pausieren zur Differenzierung und riskieren, als 'zu langsam' zu gelten"},
            {"id": 24, "category": "Stress - Distanzierung", "scenario": "Ihr Team braucht emotionale Unterstützung nach einem großen Rückschlag.", "questionA": "Sie konzentrieren sich auf die Problemlösung—Emotionen können warten", "questionB": "Sie stellen das Problem zurück, um zuerst die Moral des Teams anzusprechen"},
            {"id": 25, "category": "Stress - Passiver Widerstand", "scenario": "Die Führung verlangt, dass Sie eine Richtlinie umsetzen, der Sie nicht zustimmen.", "questionA": "Sie befolgen sichtbar, aber verlangsamen subtil die Umsetzung", "questionB": "Sie argumentieren offen dagegen und riskieren, als 'schwierig' bezeichnet zu werden"},
            {"id": 26, "category": "Stress - Überschätzung", "scenario": "Sie sollen nach einem Kollegen präsentieren, der brillant abgeliefert hat.", "questionA": "Sie verstärken Ihre Präsenz, um deren Energie zu entsprechen", "questionB": "Sie bleiben zurückhaltend und vertrauen auf Ihren Inhalt"},
            {"id": 27, "category": "Stress - Risikobereitschaft", "scenario": "Sie sehen eine Abkürzung, die Regeln biegt, aber das Quartal rettet.", "questionA": "Sie nehmen sie—Ergebnisse zählen mehr als Prozess", "questionB": "Sie melden das Problem und verfehlen das Ziel dieses Quartal"},
            {"id": 28, "category": "Stress - Aufmerksamkeit", "scenario": "Eine kritische Verhandlung erfordert, dass Sie schweigen und die andere Partei reden lassen.", "questionA": "Sie kämpfen damit—Ihr Instinkt ist, Stille mit Energie zu füllen", "questionB": "Sie passen sich leicht an—Sie können Ihre Präsenz nach Belieben modulieren"},
            {"id": 29, "category": "Stress - Exzentrizität", "scenario": "Ihre unkonventionelle Strategie wurde gerade vom Vorstand als 'unpraktisch' bezeichnet.", "questionA": "Sie verdoppeln—sie sehen die Vision noch nicht", "questionB": "Sie kalibrieren neu, um einen konventionelleren Weg zum Ziel zu finden"},
            {"id": 30, "category": "Stress - Perfektionismus", "scenario": "Eine 'gute genug' Lösung existiert, aber eine perfekte braucht 3 weitere Wochen.", "questionA": "Sie drängen auf die 3 Wochen—Qualität ist nicht verhandelbar", "questionB": "Sie liefern 'gut genug'—Momentum schlägt Perfektion"},
            {"id": 31, "category": "Stress - Konformität", "scenario": "Ihr Mentor rät einen Weg, von dem Sie glauben, dass er falsch für Sie ist.", "questionA": "Sie folgen seinem Rat—er hat dieses Vertrauen verdient", "questionB": "Sie widersprechen respektvoll und gehen Ihren eigenen Weg"},
            {"id": 32, "category": "Burnout-Muster", "scenario": "Sie haben einen Monat lang 70-Stunden-Wochen gearbeitet. Urlaub ist geplant, aber eine Krise entsteht.", "questionA": "Sie stornieren den Urlaub—das Team braucht Sie", "questionB": "Sie delegieren und gehen—Sie nützen niemandem ausgebrannt"},
            {"id": 33, "category": "Misserfolgsreaktion", "scenario": "Ein Projekt, das Sie vertreten haben, ist gerade öffentlich gescheitert.", "questionA": "Sie analysieren sofort, was schief ging und teilen Erkenntnisse", "questionB": "Sie brauchen Abstand, bevor Sie objektiv verarbeiten können"},
            {"id": 34, "category": "Vertrauensreparatur", "scenario": "Jemand, dem Sie vertraut haben, hat sich gerade mit Ihrer Arbeit gerühmt.", "questionA": "Sie sprechen es zuerst direkt mit ihm an", "questionB": "Sie stellen sicher, dass andere die Wahrheit kennen, bevor Sie ihn konfrontieren"},
            {"id": 35, "category": "Kontrolle im Chaos", "scenario": "Alles läuft gleichzeitig schief—Teamkonflikt, Bargeldkrise, Produktprobleme.", "questionA": "Sie priorisieren gnadenlos und lassen einige Feuer brennen", "questionB": "Sie versuchen alles anzusprechen und verzetteln sich"},
        ],
        "solutionDesign": [
            {"id": 36, "category": "Regeldesign - Grenzen", "context": "Basierend auf Ihren Stressreaktionen könnten Sie sich unter Druck überdehnen.", "questionA": "Sie brauchen feste Kalenderblöcke, die nicht verhandelbar sind", "questionB": "Sie brauchen eine vertrauenswürdige Person, die Ihre Verpflichtungen ablehnen kann"},
            {"id": 37, "category": "Regeldesign - Entscheidungsfindung", "context": "Ihr Entscheidungsstil kann zu Über- oder Unteranalyse führen.", "questionA": "Sie brauchen erzwungene Fristen, um Überdenken zu verhindern", "questionB": "Sie brauchen obligatorische Abkühlungsperioden, um Unterdenken zu verhindern"},
            {"id": 38, "category": "Regeldesign - Feedback", "context": "Ihre Reaktion auf Kritik beeinflusst Ihre Wachstumskurve.", "questionA": "Sie brauchen strukturierte, geplante Feedback-Sitzungen", "questionB": "Sie brauchen Echtzeit-, informelle Feedback-Schleifen"},
            {"id": 39, "category": "Regeldesign - Energiemanagement", "context": "Ihre Energiemuster beeinflussen Ihre Outputqualität.", "questionA": "Sie müssen schwierige Arbeit vorne laden, wenn Sie frisch sind", "questionB": "Sie müssen sich mit einfachen Erfolgen aufwärmen, bevor Sie schwere Probleme angehen"},
            {"id": 40, "category": "Regeldesign - Beziehungen", "context": "Ihr zwischenmenschlicher Stil hat spezifische Reibungspunkte.", "questionA": "Sie müssen mehr Geduld mit langsameren Denkern üben", "questionB": "Sie müssen mehr Durchsetzungsvermögen bei dominanten Persönlichkeiten üben"},
            {"id": 41, "category": "Regeldesign - Blinde Flecken", "context": "Jeder hat Muster, die er selbst nicht sehen kann.", "questionA": "Sie neigen dazu, Ihre Kapazität zu überschätzen und benötigte Zeit zu unterschätzen", "questionB": "Sie neigen dazu, Ihre Fähigkeiten zu unterschätzen und sich übervorzubereiten"},
            {"id": 42, "category": "Regeldesign - Erholung", "context": "Ihr Erholungsmuster nach Rückschlägen beeinflusst die langfristige Leistung.", "questionA": "Sie erholen sich durch Aktion—etwas Produktives tun", "questionB": "Sie erholen sich durch Stille—Reflexion und Ruhe"},
            {"id": 43, "category": "Regeldesign - Verantwortlichkeit", "context": "Ihre Verantwortlichkeitsstruktur beeinflusst die Durchführung.", "questionA": "Sie brauchen externe Verantwortlichkeit, um auf Kurs zu bleiben", "questionB": "Sie brauchen interne Systeme—externer Druck erzeugt Widerstand"},
        ],
    }
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

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
    date_str = datetime.now().strftime("%d. %B %Y" if lang == "de" else "%B %d, %Y")
    
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
    date_str = datetime.now().strftime("%d. %B %Y" if lang == "de" else "%B %d, %Y")
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
{trait_summary}"""

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
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, prompt in enumerate(chapters):
        status_text.text(f"{'Kapitel' if lang == 'de' else 'Chapter'} {i+1}/10...")
        progress_bar.progress((i + 1) / len(chapters))
        
        try:
            response = model.generate_content(prompt)
            chapter_text = response.text
            full_report += ("\n\n" if full_report else "") + chapter_text
        except Exception as e:
            full_report += f"\n\n> ⚠️ Error in chapter {i+1}: {e}"
    
    progress_bar.empty()
    status_text.empty()
    
    return full_report

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
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "summary"

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
    
    # Skip button (for testing)
    import random
    if st.button("⚡ SKIP — fill random & jump to results", use_container_width=True):
        for qq in all_qs:
            st.session_state.answers[qq["id"]] = {
                "choice": random.choice(["A", "B"]),
                "intensity": random.randint(1, 3)
            }
        st.session_state.page = "results"
        st.session_state.pending_choice = None
        st.rerun()
    
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
                    st.session_state.page = "results"
                st.rerun()
        with col2:
            if st.button(f"●● {t['clearly']}", use_container_width=True, key="int_2"):
                st.session_state.answers[q["id"]] = {"choice": pending, "intensity": 2}
                st.session_state.pending_choice = None
                if idx + 1 < total:
                    st.session_state.current_index = idx + 1
                else:
                    st.session_state.page = "results"
                st.rerun()
        with col3:
            if st.button(f"●●● {t['strongly']}", use_container_width=True, key="int_3"):
                st.session_state.answers[q["id"]] = {"choice": pending, "intensity": 3}
                st.session_state.pending_choice = None
                if idx + 1 < total:
                    st.session_state.current_index = idx + 1
                else:
                    st.session_state.page = "results"
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

# ============================================================
# PAGE: RESULTS
# ============================================================
elif st.session_state.page == "results":
    lang = st.session_state.language
    t = TRANSLATIONS[lang]
    analysis = analyze_results()
    tr = analysis["traits"]
    
    st.markdown(f"# 🧠 {t['pdfTitle']}")
    date_str = datetime.now().strftime("%d. %B %Y" if lang == "de" else "%B %d, %Y")
    st.markdown(f"*{t['pdfGenerated']} {date_str}*")
    
    # Tab selection
    tab_summary, tab_deep = st.tabs([t["summaryTab"], t["deepTab"]])
    
    # ---- SUMMARY TAB ----
    with tab_summary:
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
                st.markdown(f"**Rule {i+1}:** {rule}")
        else:
            st.info(t["completePhase3"])
        
        # Download buttons
        st.markdown("---")
        col_md, col_html = st.columns(2)
        with col_md:
            md_content = get_summary_markdown(analysis, t, lang)
            st.download_button(
                label=f"📥 {t['downloadMd']}",
                data=md_content,
                file_name=f"user-manual-summary-{datetime.now().strftime('%Y-%m-%d')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        with col_html:
            html_content = get_summary_html(analysis, t, lang)
            st.download_button(
                label=f"📥 {t['downloadHtml']}",
                data=html_content,
                file_name=f"user-manual-summary-{datetime.now().strftime('%Y-%m-%d')}.html",
                mime="text/html",
                use_container_width=True
            )
    
    # ---- DEEP ANALYSIS TAB ----
    with tab_deep:
        if not st.session_state.deep_analysis:
            st.markdown("### 🔮 AI-Powered Deep Analysis")
            st.markdown("Generate a comprehensive 9-chapter psychometric narrative using AI." if lang == "en" 
                       else "Generieren Sie eine umfassende 9-Kapitel psychometrische Analyse mit KI.")
            
            if st.button(t["generateBtn"], type="primary", use_container_width=True):
                result = generate_deep_analysis(analysis)
                st.session_state.deep_analysis = result
                st.rerun()
        else:
            st.markdown(st.session_state.deep_analysis)
            
            st.markdown("---")
            col_md2, col_html2, col_redo = st.columns(3)
            with col_md2:
                st.download_button(
                    label=f"📥 {t['downloadMd']}",
                    data=st.session_state.deep_analysis,
                    file_name=f"deep-analysis-{datetime.now().strftime('%Y-%m-%d')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            with col_html2:
                # Convert deep analysis markdown to simple HTML
                deep_html = st.session_state.deep_analysis
                deep_html = deep_html.replace("### ", "<h3>").replace("\n## ", "\n<h2>").replace("\n# ", "\n<h1>")
                deep_full = f'<!DOCTYPE html><html><head><meta charset="UTF-8"><style>body{{font-family:Arial;max-width:700px;margin:0 auto;padding:20px;line-height:1.6;}}@media print{{body{{-webkit-print-color-adjust:exact;print-color-adjust:exact;}}}}</style></head><body>{deep_html}</body></html>'
                st.download_button(
                    label=f"📥 {t['downloadHtml']}",
                    data=deep_full,
                    file_name=f"deep-analysis-{datetime.now().strftime('%Y-%m-%d')}.html",
                    mime="text/html",
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
        st.session_state.active_tab = "summary"
        st.rerun()
