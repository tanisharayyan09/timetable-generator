# College Timetable Generator

A Streamlit app that generates college timetables using a Genetic Algorithm.
You can watch the timetable evolve live as the algorithm removes teacher clashes.

🔗 **Live app:** https://timetable-generator-09.streamlit.app/

## Features
- Timetables for 3 classes: CSE-A, CSE-B, AI&DS-A
- Adjustable population size, mutation rate and generations
- Live chart of the best penalty per generation
- Red cells highlight teacher double-bookings

## How it works
- Each timetable is an individual in a population.
- Hard constraint: a teacher can't be in two classes at the same time.
- Soft constraints: avoid repeated subjects and gaps within a day.
- The algorithm uses selection, crossover and mutation until a clash-free timetable is found.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Files
- `app.py`: Streamlit user interface
- `timetable_ga.py`: genetic algorithm and constraints
- `requirements.txt`: dependencies
