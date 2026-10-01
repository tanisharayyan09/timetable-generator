"""Streamlit UI. Run:  streamlit run app.py   (keep timetable_ga.py in the same folder)"""
import time

import pandas as pd
import streamlit as st

import timetable_ga as ga

st.set_page_config(page_title="Timetable Evolution", layout="wide")
st.title("College Timetable Generator")
st.caption("Genetic Algorithm + constraints. Watch the timetable evolve live.")

with st.sidebar:
    st.header("GA settings")
    pop_size = st.slider("Population", 20, 200, 80, 10)
    ga.MUT_RATE = st.slider("Mutation rate", 0.05, 0.8, 0.3, 0.05)
    max_gens = st.slider("Max generations", 50, 1000, 500, 50)
    delay = st.slider("Delay per update (sec)", 0.0, 0.5, 0.05, 0.01)
    every = st.slider("Update every N generations", 1, 20, 3)
    start = st.button("Start evolution", type="primary")


def table_df(table):
    rows = []
    for p in range(ga.PERIODS):
        rows.append([ga.SUBJECTS[table[d * ga.PERIODS + p]][0]
                     if table[d * ga.PERIODS + p] >= 0 else ""
                     for d in range(len(ga.DAYS))])
    return pd.DataFrame(rows, columns=ga.DAYS,
                        index=[f"P{p + 1}" for p in range(ga.PERIODS)])


def clash_slots(ind):
    bad = set()
    for slot in range(ga.SLOTS):
        seen = {}
        for c, table in enumerate(ind):
            if table[slot] >= 0:
                seen.setdefault(table[slot], []).append(c)
        for cs in seen.values():
            if len(cs) > 1:
                bad.update((c, slot) for c in cs)
    return bad


def render(ind, c_ph, tab_ph):
    bad = clash_slots(ind)
    for c, ph in enumerate(tab_ph):
        df = table_df(ind[c])
        mask = pd.DataFrame(
            [["background-color:#ffb3b3" if (c, d * ga.PERIODS + p) in bad else ""
              for d in range(len(ga.DAYS))] for p in range(ga.PERIODS)],
            columns=df.columns, index=df.index)
        ph.dataframe(df.style.apply(lambda _: mask, axis=None), use_container_width=True)


m1, m2, m3, m4 = st.columns(4)
gen_ph, clash_ph, soft_ph, status_ph = m1.empty(), m2.empty(), m3.empty(), m4.empty()
chart_ph = st.empty()
cols = st.columns(len(ga.CLASSES))
tab_ph = []
for col, name in zip(cols, ga.CLASSES):
    col.subheader(name)
    tab_ph.append(col.empty())
st.caption("Teachers: " + ", ".join(f"{s} = {t}" for s, t in ga.SUBJECTS) +
           ". Red cells mean a teacher is double-booked.")

if start:
    pop = [ga.random_individual() for _ in range(pop_size)]
    history = []
    for gen in range(max_gens + 1):
        ranked = sorted(((ga.evaluate(i), i) for i in pop), key=lambda x: x[0][0])
        (pen, clashes, soft), best = ranked[0]
        history.append(pen)
        solved = clashes == 0 and soft <= 6
        if gen % every == 0 or solved:
            gen_ph.metric("Generation", gen)
            clash_ph.metric("Teacher clashes", clashes)
            soft_ph.metric("Soft penalty", soft)
            status_ph.metric("Status", "Solved" if solved else "Evolving")
            chart_ph.line_chart(pd.DataFrame({"Best penalty": history}))
            render(best, None, tab_ph)
            time.sleep(delay)
        if solved:
            st.success(f"Solved at generation {gen}.")
            break
        nxt = [i for _, i in ranked[:ga.ELITE]]
        while len(nxt) < pop_size:
            child = ga.crossover(ga.select(ranked), ga.select(ranked))
            ga.mutate(child)
            nxt.append(child)
        pop = nxt
    else:
        st.warning("Max generations reached. Try a higher mutation rate or more generations.")
else:
    st.info("Set the parameters in the sidebar and press Start evolution.")
