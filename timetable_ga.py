"""College Timetable Generator - Genetic Algorithm + constraints.

Run:  python timetable_ga.py            (terminal output)
      python timetable_ga.py --live     (live matplotlib graph, needs matplotlib)
"""
import random
import sys

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]
PERIODS = 6
SLOTS = len(DAYS) * PERIODS                      # 30 slots per class
CLASSES = ["CSE-A", "CSE-B", "AI&DS-A"]
SUBJECTS = [("AI", "Dr. Meena"), ("DBMS", "Mr. Arun"), ("OS", "Ms. Priya"),
            ("Maths", "Dr. Raj"), ("Networks", "Mr. Vel"), ("Lab", "Ms. Kavi")]
HOURS = 4                                        # hours per subject per week

POP, GENS, MUT_RATE, ELITE, TOURN = 80, 500, 0.3, 2, 3
W_CLASH, W_REPEAT, W_GAP = 100, 3, 2             # penalty weights


def random_class():
    """One class timetable: each subject HOURS times, rest free (-1)."""
    genes = [s for s in range(len(SUBJECTS)) for _ in range(HOURS)]
    genes += [-1] * (SLOTS - len(genes))
    random.shuffle(genes)
    return genes


def random_individual():
    return [random_class() for _ in CLASSES]


def evaluate(ind):
    """Return (total_penalty, clashes, soft_penalty). Lower is better."""
    clashes = 0
    for slot in range(SLOTS):                    # hard: teacher in 2 classes at once
        seen = set()
        for table in ind:
            s = table[slot]
            if s >= 0:
                if s in seen:
                    clashes += 1
                seen.add(s)
    soft = 0
    for table in ind:                            # soft: repeats and gaps per day
        for d in range(len(DAYS)):
            day = table[d * PERIODS:(d + 1) * PERIODS]
            lessons = [s for s in day if s >= 0]
            soft += W_REPEAT * (len(lessons) - len(set(lessons)))
            if lessons:
                first = next(i for i, s in enumerate(day) if s >= 0)
                last = PERIODS - 1 - next(i for i, s in enumerate(reversed(day)) if s >= 0)
                soft += W_GAP * (last - first + 1 - len(lessons))
    return W_CLASH * clashes + soft, clashes, soft


def crossover(a, b):
    return [list(random.choice((ta, tb))) for ta, tb in zip(a, b)]


def mutate(ind):
    for table in ind:
        if random.random() < MUT_RATE:
            for _ in range(random.randint(1, 3)):
                i, j = random.randrange(SLOTS), random.randrange(SLOTS)
                table[i], table[j] = table[j], table[i]


def select(ranked):
    return min(random.sample(ranked, TOURN), key=lambda x: x[0][0])[1]


def show(ind):
    for name, table in zip(CLASSES, ind):
        print(f"\n{name}")
        print("      " + "".join(f"{d:<10}" for d in DAYS))
        for p in range(PERIODS):
            row = [SUBJECTS[table[d * PERIODS + p]][0] if table[d * PERIODS + p] >= 0 else "-"
                   for d in range(len(DAYS))]
            print(f"  P{p + 1}  " + "".join(f"{c:<10}" for c in row))
    print("\nTeachers:", ", ".join(f"{s}={t}" for s, t in SUBJECTS))


def run(live=False):
    pop = [random_individual() for _ in range(POP)]
    history = []
    plt = None
    if live:
        import matplotlib.pyplot as plt
        plt.ion()
        fig, ax = plt.subplots()
        line, = ax.plot([], [])
        ax.set_xlabel("Generation")
        ax.set_ylabel("Best penalty")
    for gen in range(GENS + 1):
        ranked = sorted(((evaluate(i), i) for i in pop), key=lambda x: x[0][0])
        (pen, clashes, soft), best = ranked[0]
        history.append(pen)
        if gen % 10 == 0:
            print(f"Gen {gen:4d} | penalty {pen:4d} | clashes {clashes} | soft {soft}")
            if live:
                line.set_data(range(len(history)), history)
                ax.relim(); ax.autoscale_view(); plt.pause(0.01)
        if clashes == 0 and soft <= 6:
            print(f"\nSolved at generation {gen} (penalty {pen})")
            break
        nxt = [i for _, i in ranked[:ELITE]]
        while len(nxt) < POP:
            child = crossover(select(ranked), select(ranked))
            mutate(child)
            nxt.append(child)
        pop = nxt
    show(best)
    if live:
        plt.ioff(); plt.show()


if __name__ == "__main__":
    run(live="--live" in sys.argv)
