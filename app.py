import streamlit as st
import requests
import json

# API Configuration
API_URL = "http://127.0.0.1:8000"

# Page config
st.set_page_config(
    page_title="Debate Scoring System",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Debate Scoring System")
st.markdown("---")

# Initialize session state
if "speaker1_args" not in st.session_state:
    st.session_state.speaker1_args = []
if "speaker2_args" not in st.session_state:
    st.session_state.speaker2_args = []
if "results" not in st.session_state:
    st.session_state.results = None

# Topic input
topic = st.text_input("📌 Debate Topic", placeholder="e.g. Should universities offer free education")

st.markdown("---")

# Speaker name inputs
col1, col2 = st.columns(2)
with col1:
    speaker1_name = st.text_input("Speaker 1 Name", placeholder="e.g. Team A")
with col2:
    speaker2_name = st.text_input("Speaker 2 Name", placeholder="e.g. Team B")

st.markdown("---")

# Argument input area
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"💬 {speaker1_name or 'Speaker 1'} Arguments")
    arg1_input = st.text_area(
        "Type argument here",
        key="arg1_input",
        placeholder="Enter an argument...",
        height=100
    )
    if st.button("➕ Add Argument", key="add_arg1"):
        if arg1_input.strip():
            st.session_state.speaker1_args.append(arg1_input.strip())
            st.rerun()

    # Show added arguments
    if st.session_state.speaker1_args:
        st.markdown("**Added Arguments:**")
        for i, arg in enumerate(st.session_state.speaker1_args):
            col_arg, col_del = st.columns([5, 1])
            with col_arg:
                st.markdown(f"**{i+1}.** {arg}")
            with col_del:
                if st.button("🗑️", key=f"del1_{i}"):
                    st.session_state.speaker1_args.pop(i)
                    st.rerun()

with col2:
    st.subheader(f"💬 {speaker2_name or 'Speaker 2'} Arguments")
    arg2_input = st.text_area(
        "Type argument here",
        key="arg2_input",
        placeholder="Enter an argument...",
        height=100
    )
    if st.button("➕ Add Argument", key="add_arg2"):
        if arg2_input.strip():
            st.session_state.speaker2_args.append(arg2_input.strip())
            st.rerun()

    # Show added arguments
    if st.session_state.speaker2_args:
        st.markdown("**Added Arguments:**")
        for i, arg in enumerate(st.session_state.speaker2_args):
            col_arg, col_del = st.columns([5, 1])
            with col_arg:
                st.markdown(f"**{i+1}.** {arg}")
            with col_del:
                if st.button("🗑️", key=f"del2_{i}"):
                    st.session_state.speaker2_args.pop(i)
                    st.rerun()

st.markdown("---")

# Live scoring section
if st.session_state.speaker1_args or st.session_state.speaker2_args:
    st.subheader("📊 Live Scores")
    score_col1, score_col2 = st.columns(2)

    def get_live_score(speaker_name, args, topic):
        if not args or not topic:
            return None
        try:
            transcript = ". ".join(args)
            response = requests.post(f"{API_URL}/score", json={
                "topic": topic,
                "speaker": speaker_name,
                "transcript": transcript
            })
            return response.json()
        except:
            return None

    with score_col1:
        if st.session_state.speaker1_args and topic:
            score1 = get_live_score(
                speaker1_name or "Speaker 1",
                st.session_state.speaker1_args,
                topic
            )
            if score1:
                st.metric("Coverage", f"{score1.get('coverage', 0) * 100:.0f}%")
                st.metric("Quality", f"{score1.get('quality', 0):.2f}")
                st.metric("Final Score", f"{score1.get('final_score', 0):.2f}")

    with score_col2:
        if st.session_state.speaker2_args and topic:
            score2 = get_live_score(
                speaker2_name or "Speaker 2",
                st.session_state.speaker2_args,
                topic
            )
            if score2:
                st.metric("Coverage", f"{score2.get('coverage', 0) * 100:.0f}%")
                st.metric("Quality", f"{score2.get('quality', 0):.2f}")
                st.metric("Final Score", f"{score2.get('final_score', 0):.2f}")

st.markdown("---")

# Evaluate button
col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 2])
with col_btn2:
    evaluate_btn = st.button("🚀 Evaluate Debate", type="primary", use_container_width=True)

if evaluate_btn:
    if not topic:
        st.error("Please enter a debate topic!")
    elif not speaker1_name or not speaker2_name:
        st.error("Please enter both speaker names!")
    elif not st.session_state.speaker1_args:
        st.error(f"Please add at least one argument for {speaker1_name}!")
    elif not st.session_state.speaker2_args:
        st.error(f"Please add at least one argument for {speaker2_name}!")
    else:
        with st.spinner("🤔 Evaluating debate..."):
            try:
                response = requests.post(f"{API_URL}/debate", json={
                    "topic": topic,
                    "teams": [
                        {
                            "speaker": speaker1_name,
                            "transcript": ". ".join(st.session_state.speaker1_args)
                        },
                        {
                            "speaker": speaker2_name,
                            "transcript": ". ".join(st.session_state.speaker2_args)
                        }
                    ]
                })
                st.session_state.results = response.json()
            except Exception as e:
                st.error(f"Error connecting to API: {e}")

# Results tabs
if st.session_state.results:
    results = st.session_state.results
    scorecards = results.get("scorecards", [])
    winner_data = results.get("winner", {})
    rebuttals = results.get("rebuttals", [])
    llm_assessment = results.get("llm_assessment", "")

    st.markdown("---")
    st.subheader("📋 Results")

    # Create tabs
    if len(scorecards) >= 2:
        tab1, tab2, tab3 = st.tabs([
            f"🗣️ {scorecards[0]['speaker']}",
            f"🗣️ {scorecards[1]['speaker']}",
            "⚖️ Comparison & Winner"
        ])

        def show_scorecard(tab, scorecard):
            with tab:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Coverage", f"{scorecard.get('coverage', 0) * 100:.0f}%")
                with col2:
                    st.metric("Quality", f"{scorecard.get('quality', 0):.2f}")
                with col3:
                    st.metric("Final Score", f"{scorecard.get('final_score', 0):.2f}")

                st.markdown("**Extracted Arguments:**")
                for arg in scorecard.get("extracted_arguments", []):
                    with st.expander(f"📌 {arg['argument']}"):
                        st.write(f"**Best Match:** {arg.get('best_match', 'N/A')}")
                        st.write(f"**Quality Score:** {arg.get('quality_score', 0)}")

        show_scorecard(tab1, scorecards[0])
        show_scorecard(tab2, scorecards[1])

        with tab3:
            # Winner announcement
            overall_winner = winner_data.get("overall_winner", "Unknown")
            st.markdown(f"## 🏆 Winner: {overall_winner}")

            # Score comparison
            st.markdown("### 📊 Score Comparison")
            comp_col1, comp_col2 = st.columns(2)
            with comp_col1:
                s1 = scorecards[0]
                st.markdown(f"**{s1['speaker']}**")
                st.progress(s1.get("final_score", 0))
                st.write(f"Score: {s1.get('final_score', 0):.2f}")
            with comp_col2:
                s2 = scorecards[1]
                st.markdown(f"**{s2['speaker']}**")
                st.progress(s2.get("final_score", 0))
                st.write(f"Score: {s2.get('final_score', 0):.2f}")

            # Winner strategies
            st.markdown("### 🎯 Winner by Strategy")
            strategies = winner_data.get("strategies", {})
            for strategy_name, strategy_data in strategies.items():
                st.write(f"**{strategy_name.replace('_', ' ').title()}:** {strategy_data['winner']} — {strategy_data['reasoning']}")

            # Rebuttals
            if rebuttals:
                st.markdown("### ⚔️ Rebuttals Detected")
                for r in rebuttals:
                    with st.expander(f"🔄 {r['from_speaker']} → {r['to_speaker']} ({r['relation']})"):
                        st.write(f"**Argument:** {r['argument']}")
                        st.write(f"**Targets:** {r['targets']}")
                        st.write(f"**Confidence:** {r['confidence']}")
                        st.write(f"**Reasoning:** {r['reasoning']}")

            # LLM Assessment
            if llm_assessment:
                st.markdown("### 🤖 AI Assessment")
                st.info(llm_assessment)

    # Reset button
    st.markdown("---")
    if st.button("🔄 Start New Debate"):
        st.session_state.speaker1_args = []
        st.session_state.speaker2_args = []
        st.session_state.results = None
        st.rerun()