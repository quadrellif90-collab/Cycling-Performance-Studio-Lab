#!/usr/bin/env python3
"""Generate multi-sport ZWO workout files for CPSL.

Categories:
  - running: 5K, 10K, half-marathon, fartlek, tempo, intervals
  - mtb: technical, climbing, XC, enduro, downhill
  - gravel: endurance, mixed-surface, adventure
  - cross_training: strength, core, HIIT
  - gym_functional: heavy compound, power, stability
  - mobility: yoga, stretching, foam rolling

Each file is a valid .zwo XML document compatible with Zwift.
Running workouts use <sportType>run</sportType> with pace-based targets.
"""

import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

WORKOUTS_DIR = os.path.join(os.path.dirname(__file__), "..", "workouts")

# ─── Running Workouts ────────────────────────────────────────────────────────

RUNNING_WORKOUTS = [
    {
        "name": "5K Race Prep - 6x800m",
        "desc": "Interval session for 5K speed. 6x800m at 5K pace with 400m jog recovery. Total ~45min.",
        "category": "Running Intervals",
        "segments": [
            ("Warmup", 600, 0.60, 0.75),
            ("SteadyState", 400, 0.85, 0.85),  # 400m jog
            ("SteadyState", 800, 1.05, 1.05),  # 800m at 5K pace
            ("SteadyState", 400, 0.85, 0.85),
            ("SteadyState", 800, 1.05, 1.05),
            ("SteadyState", 400, 0.85, 0.85),
            ("SteadyState", 800, 1.05, 1.05),
            ("SteadyState", 400, 0.85, 0.85),
            ("SteadyState", 800, 1.05, 1.05),
            ("SteadyState", 400, 0.85, 0.85),
            ("SteadyState", 800, 1.05, 1.05),
            ("SteadyState", 400, 0.85, 0.85),
            ("SteadyState", 800, 1.05, 1.05),
            ("Cooldown", 600, 0.75, 0.60),
        ],
    },
    {
        "name": "10K Tempo Build",
        "desc": "Progressive tempo run for 10K preparation. Build from marathon to 10K pace. Total ~50min.",
        "category": "Running Tempo",
        "segments": [
            ("Warmup", 600, 0.60, 0.70),
            ("SteadyState", 600, 0.75, 0.75),  # marathon pace
            ("SteadyState", 600, 0.80, 0.80),  # half-marathon pace
            ("SteadyState", 600, 0.85, 0.85),  # 10K pace
            ("SteadyState", 600, 0.90, 0.90),  # 10K+ pace
            ("SteadyState", 600, 0.85, 0.85),
            ("SteadyState", 600, 0.80, 0.80),
            ("Cooldown", 600, 0.70, 0.60),
        ],
    },
    {
        "name": "Half Marathon Long Run",
        "desc": "Steady long run with marathon-pace finish. Builds endurance for half marathon distance. Total ~75min.",
        "category": "Running Endurance",
        "segments": [
            ("Warmup", 600, 0.60, 0.70),
            ("SteadyState", 1800, 0.70, 0.70),  # 30min easy
            ("SteadyState", 1200, 0.75, 0.75),  # 20min marathon pace
            ("SteadyState", 600, 0.80, 0.80),   # 10min half pace
            ("SteadyState", 600, 0.75, 0.75),
            ("Cooldown", 600, 0.70, 0.60),
        ],
    },
    {
        "name": "Fartlek City Run",
        "desc": "Unstructured fartlek session. Alternate fast/easy efforts by feel. Total ~40min.",
        "category": "Running Fartlek",
        "segments": [
            ("Warmup", 480, 0.60, 0.70),
            ("SteadyState", 120, 0.90, 0.90),  # hard
            ("SteadyState", 120, 0.70, 0.70),  # easy
            ("SteadyState", 90, 0.95, 0.95),
            ("SteadyState", 90, 0.70, 0.70),
            ("SteadyState", 60, 1.00, 1.00),
            ("SteadyState", 120, 0.70, 0.70),
            ("SteadyState", 90, 0.95, 0.95),
            ("SteadyState", 90, 0.70, 0.70),
            ("SteadyState", 120, 0.90, 0.90),
            ("SteadyState", 120, 0.70, 0.70),
            ("SteadyState", 60, 1.00, 1.00),
            ("SteadyState", 120, 0.70, 0.70),
            ("Cooldown", 480, 0.70, 0.60),
        ],
    },
    {
        "name": "VO2max Run Intervals 5x3min",
        "desc": "High-intensity VO2max session. 5x3min at hard effort with 2min jog recovery. Total ~40min.",
        "category": "Running VO2max",
        "segments": [
            ("Warmup", 600, 0.60, 0.75),
            ("SteadyState", 180, 1.10, 1.10),  # hard
            ("SteadyState", 120, 0.80, 0.80),  # jog
            ("SteadyState", 180, 1.10, 1.10),
            ("SteadyState", 120, 0.80, 0.80),
            ("SteadyState", 180, 1.10, 1.10),
            ("SteadyState", 120, 0.80, 0.80),
            ("SteadyState", 180, 1.10, 1.10),
            ("SteadyState", 120, 0.80, 0.80),
            ("SteadyState", 180, 1.10, 1.10),
            ("Cooldown", 600, 0.75, 0.60),
        ],
    },
    {
        "name": "Easy Recovery Run",
        "desc": "Easy-paced recovery run. Keep heart rate low. Total ~30min.",
        "category": "Running Recovery",
        "segments": [
            ("Warmup", 300, 0.55, 0.65),
            ("SteadyState", 1200, 0.65, 0.65),
            ("Cooldown", 300, 0.65, 0.55),
        ],
    },
]

# ─── MTB Workouts ────────────────────────────────────────────────────────────

MTB_WORKOUTS = [
    {
        "name": "MTB Climbing Repeats",
        "desc": "Simulate repeated climbs. 4x5min at high resistance with coast recovery. Total ~50min.",
        "category": "MTB Climbing",
        "segments": [
            ("Warmup", 480, 0.50, 0.70),
            ("SteadyState", 300, 1.00, 1.00),  # climb
            ("Interval", 180, 0.50, 0.50),     # descent/coast
            ("SteadyState", 300, 1.05, 1.05),
            ("Interval", 180, 0.50, 0.50),
            ("SteadyState", 300, 1.05, 1.05),
            ("Interval", 180, 0.50, 0.50),
            ("SteadyState", 300, 1.05, 1.05),
            ("Cooldown", 480, 0.70, 0.50),
        ],
    },
    {
        "name": "MTB Technical Intervals",
        "desc": "Short punchy efforts simulating technical trail sections. 8x1min hard with 2min easy. Total ~40min.",
        "category": "MTB Technical",
        "segments": [
            ("Warmup", 480, 0.50, 0.70),
            ("SteadyState", 60, 1.10, 1.10),
            ("Interval", 120, 0.55, 0.55),
            ("SteadyState", 60, 1.15, 1.15),
            ("Interval", 120, 0.55, 0.55),
            ("SteadyState", 60, 1.10, 1.10),
            ("Interval", 120, 0.55, 0.55),
            ("SteadyState", 60, 1.15, 1.15),
            ("Interval", 120, 0.55, 0.55),
            ("SteadyState", 60, 1.10, 1.10),
            ("Interval", 120, 0.55, 0.55),
            ("SteadyState", 60, 1.15, 1.15),
            ("Interval", 120, 0.55, 0.55),
            ("SteadyState", 60, 1.10, 1.10),
            ("Interval", 120, 0.55, 0.55),
            ("Cooldown", 480, 0.70, 0.50),
        ],
    },
    {
        "name": "MTB Endurance Ride",
        "desc": "Long steady endurance effort simulating cross-country ride. Total ~60min.",
        "category": "MTB Endurance",
        "segments": [
            ("Warmup", 480, 0.50, 0.65),
            ("SteadyState", 2400, 0.70, 0.70),
            ("SteadyState", 600, 0.75, 0.75),
            ("Cooldown", 480, 0.65, 0.50),
        ],
    },
    {
        "name": "MTB Sprint Starts",
        "desc": "Explosive start intervals for race starts. 6x15s max effort with 3min recovery. Total ~30min.",
        "category": "MTB Sprint",
        "segments": [
            ("Warmup", 480, 0.50, 0.70),
            ("SteadyState", 15, 1.30, 1.30),
            ("Interval", 180, 0.50, 0.50),
            ("SteadyState", 15, 1.35, 1.35),
            ("Interval", 180, 0.50, 0.50),
            ("SteadyState", 15, 1.30, 1.30),
            ("Interval", 180, 0.50, 0.50),
            ("SteadyState", 15, 1.35, 1.35),
            ("Interval", 180, 0.50, 0.50),
            ("SteadyState", 15, 1.30, 1.30),
            ("Interval", 180, 0.50, 0.50),
            ("SteadyState", 15, 1.35, 1.35),
            ("Cooldown", 480, 0.70, 0.50),
        ],
    },
]

# ─── Gravel Workouts ─────────────────────────────────────────────────────────

GRAVEL_WORKOUTS = [
    {
        "name": "Gravel Endurance Builder",
        "desc": "Long mixed-surface endurance ride. Steady effort with gravel-pace surges. Total ~75min.",
        "category": "Gravel Endurance",
        "segments": [
            ("Warmup", 480, 0.50, 0.65),
            ("SteadyState", 1800, 0.70, 0.70),  # 30min base
            ("SteadyState", 300, 0.80, 0.80),   # gravel surge
            ("SteadyState", 600, 0.70, 0.70),
            ("SteadyState", 300, 0.85, 0.85),   # gravel surge
            ("SteadyState", 600, 0.70, 0.70),
            ("SteadyState", 300, 0.80, 0.80),
            ("Cooldown", 480, 0.65, 0.50),
        ],
    },
    {
        "name": "Gravel Race Simulation",
        "desc": "Simulate gravel race effort with mixed terrain. 2x20min at race pace. Total ~60min.",
        "category": "Gravel Race",
        "segments": [
            ("Warmup", 480, 0.50, 0.70),
            ("SteadyState", 1200, 0.85, 0.85),  # 20min race pace
            ("Interval", 300, 0.60, 0.60),       # recovery
            ("SteadyState", 1200, 0.85, 0.85),
            ("Cooldown", 480, 0.70, 0.50),
        ],
    },
    {
        "name": "Gravel Hill Repeats",
        "desc": "Climbing repeats on gravel terrain. 5x3min climb with 2min descent. Total ~45min.",
        "category": "Gravel Climbing",
        "segments": [
            ("Warmup", 480, 0.50, 0.70),
            ("SteadyState", 180, 0.95, 0.95),
            ("Interval", 120, 0.55, 0.55),
            ("SteadyState", 180, 1.00, 1.00),
            ("Interval", 120, 0.55, 0.55),
            ("SteadyState", 180, 1.00, 1.00),
            ("Interval", 120, 0.55, 0.55),
            ("SteadyState", 180, 1.00, 1.00),
            ("Interval", 120, 0.55, 0.55),
            ("SteadyState", 180, 1.00, 1.00),
            ("Cooldown", 480, 0.70, 0.50),
        ],
    },
]

# ─── Cross-Training Workouts ─────────────────────────────────────────────────

CROSS_TRAINING_WORKOUTS = [
    {
        "name": "Cyclist Core Strength",
        "desc": "Core stability workout for cycling performance. Planks, dead bugs, pallof press. Total ~30min.",
        "category": "Cross-Training Core",
        "segments": [
            ("Warmup", 300, 0.50, 0.65),
            ("SteadyState", 60, 0.70, 0.70),   # plank
            ("Interval", 30, 0.50, 0.50),
            ("SteadyState", 60, 0.70, 0.70),   # dead bug
            ("Interval", 30, 0.50, 0.50),
            ("SteadyState", 60, 0.70, 0.70),   # pallof
            ("Interval", 30, 0.50, 0.50),
            ("SteadyState", 60, 0.70, 0.70),
            ("Interval", 30, 0.50, 0.50),
            ("SteadyState", 60, 0.70, 0.70),
            ("Interval", 30, 0.50, 0.50),
            ("SteadyState", 60, 0.70, 0.70),
            ("Cooldown", 300, 0.65, 0.50),
        ],
    },
    {
        "name": "Full Body HIIT for Cyclists",
        "desc": "High-intensity interval training for cross-training. Burpees, mountain climbers, squats. Total ~25min.",
        "category": "Cross-Training HIIT",
        "segments": [
            ("Warmup", 300, 0.50, 0.70),
            ("SteadyState", 45, 1.00, 1.00),   # burpees
            ("Interval", 30, 0.50, 0.50),
            ("SteadyState", 45, 1.05, 1.05),   # mountain climbers
            ("Interval", 30, 0.50, 0.50),
            ("SteadyState", 45, 1.00, 1.00),   # squat jumps
            ("Interval", 30, 0.50, 0.50),
            ("SteadyState", 45, 1.05, 1.05),
            ("Interval", 30, 0.50, 0.50),
            ("SteadyState", 45, 1.00, 1.00),
            ("Interval", 30, 0.50, 0.50),
            ("SteadyState", 45, 1.05, 1.05),
            ("Cooldown", 300, 0.70, 0.50),
        ],
    },
    {
        "name": "Upper Body for Cyclists",
        "desc": "Upper body strength session. Push-ups, rows, shoulder work. Total ~30min.",
        "category": "Cross-Training Strength",
        "segments": [
            ("Warmup", 300, 0.50, 0.65),
            ("SteadyState", 60, 0.70, 0.70),   # push-ups
            ("Interval", 45, 0.50, 0.50),
            ("SteadyState", 60, 0.70, 0.70),   # rows
            ("Interval", 45, 0.50, 0.50),
            ("SteadyState", 60, 0.70, 0.70),   # shoulder press
            ("Interval", 45, 0.50, 0.50),
            ("SteadyState", 60, 0.70, 0.70),
            ("Interval", 45, 0.50, 0.50),
            ("SteadyState", 60, 0.70, 0.70),
            ("Cooldown", 300, 0.65, 0.50),
        ],
    },
]

# ─── Gym/Functional Workouts ─────────────────────────────────────────────────

GYM_FUNCTIONAL_WORKOUTS = [
    {
        "name": "Cyclist Leg Day - Squat Focus",
        "desc": "Heavy compound lower body session. Back squats, lunges, leg press. Total ~45min.",
        "category": "Gym Strength",
        "segments": [
            ("Warmup", 480, 0.50, 0.65),
            ("SteadyState", 120, 0.75, 0.75),  # squat warmup
            ("Interval", 60, 0.50, 0.50),
            ("SteadyState", 120, 0.85, 0.85),  # squat working set
            ("Interval", 90, 0.50, 0.50),
            ("SteadyState", 120, 0.85, 0.85),
            ("Interval", 90, 0.50, 0.50),
            ("SteadyState", 120, 0.85, 0.85),
            ("Interval", 90, 0.50, 0.50),
            ("SteadyState", 90, 0.80, 0.80),   # lunge
            ("Interval", 60, 0.50, 0.50),
            ("SteadyState", 90, 0.80, 0.80),
            ("Cooldown", 480, 0.65, 0.50),
        ],
    },
    {
        "name": "Power & Explosiveness",
        "desc": "Plyometric and power training. Box jumps, kettlebell swings, clean & press. Total ~35min.",
        "category": "Gym Power",
        "segments": [
            ("Warmup", 480, 0.50, 0.70),
            ("SteadyState", 30, 1.10, 1.10),   # box jump
            ("Interval", 60, 0.50, 0.50),
            ("SteadyState", 30, 1.15, 1.15),   # KB swing
            ("Interval", 60, 0.50, 0.50),
            ("SteadyState", 30, 1.10, 1.10),
            ("Interval", 60, 0.50, 0.50),
            ("SteadyState", 30, 1.15, 1.15),
            ("Interval", 60, 0.50, 0.50),
            ("SteadyState", 30, 1.10, 1.10),
            ("Interval", 60, 0.50, 0.50),
            ("SteadyState", 30, 1.15, 1.15),
            ("Cooldown", 480, 0.70, 0.50),
        ],
    },
    {
        "name": "Single-Leg Stability",
        "desc": "Unilateral strength for cycling balance. Bulgarian split squats, step-ups, single-leg deadlift. Total ~40min.",
        "category": "Gym Stability",
        "segments": [
            ("Warmup", 480, 0.50, 0.65),
            ("SteadyState", 90, 0.75, 0.75),   # split squat L
            ("Interval", 45, 0.50, 0.50),
            ("SteadyState", 90, 0.75, 0.75),   # split squat R
            ("Interval", 45, 0.50, 0.50),
            ("SteadyState", 90, 0.80, 0.80),   # step-up L
            ("Interval", 45, 0.50, 0.50),
            ("SteadyState", 90, 0.80, 0.80),   # step-up R
            ("Interval", 45, 0.50, 0.50),
            ("SteadyState", 90, 0.75, 0.75),   # SL deadlift L
            ("Interval", 45, 0.50, 0.50),
            ("SteadyState", 90, 0.75, 0.75),   # SL deadlift R
            ("Cooldown", 480, 0.65, 0.50),
        ],
    },
]

# ─── Mobility Workouts ───────────────────────────────────────────────────────

MOBILITY_WORKOUTS = [
    {
        "name": "Pre-Ride Dynamic Warm-Up",
        "desc": "Dynamic stretching before cycling. Leg swings, hip circles, torso rotation. Total ~15min.",
        "category": "Mobility Warm-Up",
        "segments": [
            ("Warmup", 180, 0.40, 0.55),
            ("SteadyState", 60, 0.55, 0.55),   # leg swings
            ("SteadyState", 60, 0.55, 0.55),   # hip circles
            ("SteadyState", 60, 0.55, 0.55),   # torso rotation
            ("SteadyState", 60, 0.55, 0.55),   # arm circles
            ("SteadyState", 60, 0.55, 0.55),   # walking lunges
            ("Cooldown", 180, 0.55, 0.40),
        ],
    },
    {
        "name": "Post-Ride Cool Down & Stretch",
        "desc": "Static stretching after cycling. Focus on quads, hamstrings, hip flexors, calves. Total ~20min.",
        "category": "Mobility Cool-Down",
        "segments": [
            ("Warmup", 300, 0.50, 0.60),
            ("SteadyState", 60, 0.55, 0.55),   # quad stretch
            ("SteadyState", 60, 0.55, 0.55),   # hamstring stretch
            ("SteadyState", 60, 0.55, 0.55),   # hip flexor
            ("SteadyState", 60, 0.55, 0.55),   # calf stretch
            ("SteadyState", 60, 0.55, 0.55),   # glute stretch
            ("SteadyState", 60, 0.55, 0.55),   # IT band
            ("Cooldown", 300, 0.60, 0.50),
        ],
    },
    {
        "name": "Yoga for Cyclists",
        "desc": "Yoga flow targeting cycling muscle groups. Hip openers, spinal twists, forward folds. Total ~30min.",
        "category": "Mobility Yoga",
        "segments": [
            ("Warmup", 300, 0.45, 0.55),
            ("SteadyState", 120, 0.55, 0.55),  # downward dog
            ("SteadyState", 90, 0.55, 0.55),   # pigeon pose L
            ("SteadyState", 90, 0.55, 0.55),   # pigeon pose R
            ("SteadyState", 90, 0.55, 0.55),   # warrior I
            ("SteadyState", 90, 0.55, 0.55),   # warrior II
            ("SteadyState", 90, 0.55, 0.55),   # triangle
            ("SteadyState", 90, 0.55, 0.55),   # seated twist L
            ("SteadyState", 90, 0.55, 0.55),   # seated twist R
            ("SteadyState", 120, 0.50, 0.50),  # savasana
            ("Cooldown", 300, 0.55, 0.45),
        ],
    },
    {
        "name": "Foam Rolling Recovery",
        "desc": "Self-myofascial release with foam roller. Quads, IT band, glutes, calves, thoracic. Total ~25min.",
        "category": "Mobility Recovery",
        "segments": [
            ("Warmup", 300, 0.40, 0.50),
            ("SteadyState", 90, 0.50, 0.50),   # quad roll
            ("SteadyState", 90, 0.50, 0.50),   # IT band roll
            ("SteadyState", 90, 0.50, 0.50),   # glute roll
            ("SteadyState", 90, 0.50, 0.50),   # calf roll
            ("SteadyState", 90, 0.50, 0.50),   # thoracic roll
            ("SteadyState", 90, 0.50, 0.50),   # lat roll
            ("Cooldown", 300, 0.50, 0.40),
        ],
    },
]


# ─── Triathlon / Brick Workouts ──────────────────────────────────────────────

TRIATHLON_WORKOUTS = [
    {
        "name": "Olympic Distance Brick - Sundried",
        "desc": "Classic Olympic triathlon brick. Bike at Level III/IV then run at race pace. Total ~85min.",
        "category": "Triathlon Brick",
        "segments": [
            ("Warmup", 1800, 0.60, 0.70),   # 30min bike WU
            ("SteadyState", 1200, 0.80, 0.80),  # 20min Level III
            ("SteadyState", 600, 0.70, 0.70),   # 10min Level II
            ("SteadyState", 300, 0.90, 0.90),   # 5min Level IV
            ("SteadyState", 1200, 0.80, 0.80),  # 20min run Level III
            ("Cooldown", 600, 0.70, 0.60),      # 10min run CD
        ],
    },
    {
        "name": "Sprint Triathlon Brick - Torsten Abel",
        "desc": "High-intensity sprint tri brick. 4x mini-brick (run 1km + bike 2mi at Level V). Total ~75min.",
        "category": "Triathlon Brick",
        "segments": [
            ("Warmup", 600, 0.60, 0.70),   # 10min bike WU
            ("Warmup", 1200, 0.60, 0.70),  # 20min run WU
            ("SteadyState", 300, 1.05, 1.05),  # 1km run Level V
            ("SteadyState", 300, 1.05, 1.05),  # 2mi bike Level V
            ("SteadyState", 300, 0.70, 0.70),  # 5min RI
            ("SteadyState", 300, 1.05, 1.05),
            ("SteadyState", 300, 1.05, 1.05),
            ("SteadyState", 300, 0.70, 0.70),
            ("SteadyState", 300, 1.05, 1.05),
            ("SteadyState", 300, 1.05, 1.05),
            ("SteadyState", 300, 0.70, 0.70),
            ("SteadyState", 300, 1.05, 1.05),
            ("SteadyState", 300, 1.05, 1.05),
            ("Cooldown", 600, 0.70, 0.60),  # 10min run CD
        ],
    },
    {
        "name": "Race Replication Brick - Dr Yelling",
        "desc": "Simulate race-day effort. 10mi bike at Level IV then 2mi run at Level IV. Total ~55min.",
        "category": "Triathlon Brick",
        "segments": [
            ("Warmup", 600, 0.60, 0.70),   # 10min bike WU
            ("SteadyState", 1800, 0.90, 0.90),  # 10mi bike Level IV
            ("SteadyState", 960, 0.90, 0.90),   # 2mi run Level IV
            ("Cooldown", 600, 0.70, 0.60),       # 10min CD
        ],
    },
    {
        "name": "Beginner Triathlon - Bike-Run Transition",
        "desc": "Gentle brick for beginners. Easy bike followed by short run. Total ~45min.",
        "category": "Triathlon Brick",
        "segments": [
            ("Warmup", 600, 0.55, 0.65),   # 10min bike WU
            ("SteadyState", 1200, 0.70, 0.70),  # 20min easy bike
            ("SteadyState", 600, 0.75, 0.75),   # 10min easy run
            ("Cooldown", 600, 0.65, 0.55),       # 10min CD
        ],
    },
    {
        "name": "Long Course Ironman Brick",
        "desc": "Ironman simulation. 2hr bike at race pace then 30min run. Total ~2.5hr.",
        "category": "Triathlon Brick",
        "segments": [
            ("Warmup", 1200, 0.55, 0.65),   # 20min bike WU
            ("SteadyState", 3600, 0.75, 0.75),  # 60min bike steady
            ("SteadyState", 1800, 0.80, 0.80),  # 30min race pace
            ("SteadyState", 1200, 0.75, 0.75),  # 20min IM pace
            ("SteadyState", 1800, 0.75, 0.75),  # 30min run
            ("Cooldown", 600, 0.70, 0.60),
        ],
    },
]


# ─── Swim Workouts (bike-sport compatible ZWO) ──────────────────────────────

SWIM_WORKOUTS = [
    {
        "name": "Swim Technique Drill - Catch & Pull",
        "desc": "Technique-focused swim session. Drill sets with catch-up, fingertip drag, fist drill. Total ~40min.",
        "category": "Swim Technique",
        "segments": [
            ("Warmup", 480, 0.50, 0.60),   # 8min easy swim
            ("SteadyState", 120, 0.70, 0.70),  # catch-up drill
            ("Interval", 30, 0.50, 0.50),
            ("SteadyState", 120, 0.70, 0.70),  # fingertip drag
            ("Interval", 30, 0.50, 0.50),
            ("SteadyState", 120, 0.70, 0.70),  # fist drill
            ("Interval", 30, 0.50, 0.50),
            ("SteadyState", 120, 0.70, 0.70),
            ("Interval", 30, 0.50, 0.50),
            ("SteadyState", 120, 0.75, 0.75),  # pull buoy set
            ("Interval", 30, 0.50, 0.50),
            ("SteadyState", 120, 0.75, 0.75),
            ("Cooldown", 480, 0.60, 0.50),
        ],
    },
    {
        "name": "Swim Endurance - 2000m Steady",
        "desc": "Long steady swim for aerobic base. Consistent pace with kick sets. Total ~45min.",
        "category": "Swim Endurance",
        "segments": [
            ("Warmup", 480, 0.50, 0.60),
            ("SteadyState", 600, 0.70, 0.70),  # 10min steady
            ("SteadyState", 300, 0.65, 0.65),  # 5min kick
            ("SteadyState", 600, 0.72, 0.72),  # 10min steady
            ("SteadyState", 300, 0.65, 0.65),  # 5min kick
            ("SteadyState", 600, 0.70, 0.70),  # 10min steady
            ("Cooldown", 480, 0.60, 0.50),
        ],
    },
    {
        "name": "Swim VO2max Intervals",
        "desc": "High-intensity swim intervals. 8x100m at race pace with 20s rest. Total ~35min.",
        "category": "Swim Intervals",
        "segments": [
            ("Warmup", 480, 0.50, 0.65),
            ("SteadyState", 100, 0.95, 0.95),  # 100m hard
            ("Interval", 20, 0.50, 0.50),       # rest
            ("SteadyState", 100, 0.95, 0.95),
            ("Interval", 20, 0.50, 0.50),
            ("SteadyState", 100, 0.95, 0.95),
            ("Interval", 20, 0.50, 0.50),
            ("SteadyState", 100, 0.95, 0.95),
            ("Interval", 20, 0.50, 0.50),
            ("SteadyState", 100, 0.95, 0.95),
            ("Interval", 20, 0.50, 0.50),
            ("SteadyState", 100, 0.95, 0.95),
            ("Interval", 20, 0.50, 0.50),
            ("SteadyState", 100, 0.95, 0.95),
            ("Interval", 20, 0.50, 0.50),
            ("SteadyState", 100, 0.95, 0.95),
            ("Cooldown", 480, 0.60, 0.50),
        ],
    },
]


# ─── Duathlon Workouts (run-bike-run) ────────────────────────────────────────

DUATHLON_WORKOUTS = [
    {
        "name": "Duathlon Standard - Run Bike Run",
        "desc": "Standard duathlon simulation. 5km run + 20km bike + 2.5km run. Total ~80min.",
        "category": "Duathlon",
        "segments": [
            ("Warmup", 480, 0.60, 0.70),   # 8min run WU
            ("SteadyState", 1200, 0.85, 0.85),  # 20min run race pace
            ("SteadyState", 2400, 0.82, 0.82),  # 40min bike race pace
            ("SteadyState", 750, 0.90, 0.90),   # 12.5min run fast
            ("Cooldown", 480, 0.70, 0.60),
        ],
    },
    {
        "name": "Duathlon Sprint - Short & Sharp",
        "desc": "Sprint duathlon. Short run, fast bike, fast run finish. Total ~45min.",
        "category": "Duathlon",
        "segments": [
            ("Warmup", 300, 0.60, 0.70),   # 5min run WU
            ("SteadyState", 600, 0.90, 0.90),  # 10min run
            ("SteadyState", 1200, 0.88, 0.88),  # 20min bike
            ("SteadyState", 600, 0.92, 0.92),   # 10min run
            ("Cooldown", 300, 0.70, 0.60),
        ],
    },
    {
        "name": "Duathlon Bike Focus",
        "desc": "Bike-dominant duathlon. Long bike with short run bookends. Total ~70min.",
        "category": "Duathlon",
        "segments": [
            ("Warmup", 300, 0.60, 0.70),   # 5min run
            ("SteadyState", 300, 0.80, 0.80),   # 5min run moderate
            ("SteadyState", 3000, 0.82, 0.82),  # 50min bike
            ("SteadyState", 600, 0.85, 0.85),   # 10min run
            ("Cooldown", 300, 0.70, 0.60),
        ],
    },
]


# ─── Additional MTB / Enduro / Downhill ──────────────────────────────────────

MTB_ADVANCED_WORKOUTS = [
    {
        "name": "MTB Downhill Technique",
        "desc": "Simulate downhill sections. High power bursts with coast recovery. Total ~35min.",
        "category": "MTB Downhill",
        "segments": [
            ("Warmup", 480, 0.50, 0.70),
            ("SteadyState", 30, 1.20, 1.20),   # descend burst
            ("Interval", 90, 0.45, 0.45),       # climb/recover
            ("SteadyState", 30, 1.25, 1.25),
            ("Interval", 90, 0.45, 0.45),
            ("SteadyState", 30, 1.20, 1.20),
            ("Interval", 90, 0.45, 0.45),
            ("SteadyState", 30, 1.25, 1.25),
            ("Interval", 90, 0.45, 0.45),
            ("SteadyState", 30, 1.20, 1.20),
            ("Interval", 90, 0.45, 0.45),
            ("SteadyState", 30, 1.25, 1.25),
            ("Interval", 90, 0.45, 0.45),
            ("Cooldown", 480, 0.70, 0.50),
        ],
    },
    {
        "name": "MTB Enduro Stage Simulation",
        "desc": "Simulate enduro stages. Mixed intensity with technical sections. Total ~50min.",
        "category": "MTB Enduro",
        "segments": [
            ("Warmup", 480, 0.50, 0.65),
            ("SteadyState", 300, 0.90, 0.90),   # stage 1
            ("Interval", 120, 0.55, 0.55),       # transfer
            ("SteadyState", 300, 0.95, 0.95),   # stage 2
            ("Interval", 120, 0.55, 0.55),
            ("SteadyState", 300, 0.90, 0.90),   # stage 3
            ("Interval", 120, 0.55, 0.55),
            ("SteadyState", 300, 0.95, 0.95),   # stage 4
            ("Cooldown", 480, 0.70, 0.50),
        ],
    },
    {
        "name": "MTB Cross-Country Race Pace",
        "desc": "XC race simulation. Sustained effort with punchy climbs. Total ~55min.",
        "category": "MTB XC",
        "segments": [
            ("Warmup", 480, 0.50, 0.70),
            ("SteadyState", 1800, 0.82, 0.82),  # 30min steady
            ("SteadyState", 120, 1.00, 1.00),   # climb
            ("SteadyState", 600, 0.80, 0.80),
            ("SteadyState", 120, 1.05, 1.05),   # steep climb
            ("SteadyState", 600, 0.82, 0.82),
            ("SteadyState", 120, 1.00, 1.00),
            ("Cooldown", 480, 0.70, 0.50),
        ],
    },
]


# ─── Active Recovery / Rest Day Workouts ─────────────────────────────────────

ACTIVE_RECOVERY_WORKOUTS = [
    {
        "name": "Active Recovery Spin",
        "desc": "Easy recovery spin. Keep HR low, legs spinning. Total ~30min.",
        "category": "Recovery",
        "segments": [
            ("Warmup", 300, 0.40, 0.50),
            ("SteadyState", 1200, 0.50, 0.50),
            ("Cooldown", 300, 0.50, 0.40),
        ],
    },
    {
        "name": "Rest Day Mobility Flow",
        "desc": "Gentle mobility work for recovery day. Stretching and light movement. Total ~20min.",
        "category": "Recovery",
        "segments": [
            ("Warmup", 300, 0.40, 0.50),
            ("SteadyState", 60, 0.50, 0.50),
            ("SteadyState", 60, 0.50, 0.50),
            ("SteadyState", 60, 0.50, 0.50),
            ("SteadyState", 60, 0.50, 0.50),
            ("SteadyState", 60, 0.50, 0.50),
            ("SteadyState", 60, 0.50, 0.50),
            ("Cooldown", 300, 0.50, 0.40),
        ],
    },
]


def build_zwo(name: str, desc: str, category: str, segments: list,
              sport: str = "bike") -> str:
    """Build a valid .zwo XML string."""
    wf = ET.Element("workout_file")
    ET.SubElement(wf, "author").text = "CPSL"
    ET.SubElement(wf, "name").text = name
    ET.SubElement(wf, "description").text = desc
    ET.SubElement(wf, "category").text = category
    ET.SubElement(wf, "sportType").text = sport
    ET.SubElement(wf, "tags").text = ""

    workout = ET.SubElement(wf, "workout")
    for seg_type, duration, pwr_high, pwr_low in segments:
        if seg_type == "Warmup":
            el = ET.SubElement(workout, "Warmup",
                              Duration=str(duration),
                              PowerLow=f"{pwr_low:.4f}",
                              PowerHigh=f"{pwr_high:.4f}")
        elif seg_type == "Cooldown":
            el = ET.SubElement(workout, "Cooldown",
                              Duration=str(duration),
                              PowerLow=f"{pwr_low:.4f}",
                              PowerHigh=f"{pwr_high:.4f}")
        elif seg_type == "Interval":
            el = ET.SubElement(workout, "Interval",
                              Duration=str(duration),
                              PowerLow=f"{pwr_low:.4f}",
                              PowerHigh=f"{pwr_high:.4f}")
        else:  # SteadyState
            ET.SubElement(workout, "SteadyState",
                         Duration=str(duration),
                         Power=f"{pwr_high:.4f}")

    raw = ET.tostring(wf, encoding="unicode")
    return minidom.parseString(raw).toprettyxml(indent="  ", encoding=None)


def sanitize(name: str) -> str:
    """Make a filename-safe string."""
    return "".join(c if c.isalnum() or c in " -_" else "" for c in name).strip().replace(" ", "_")


def main():
    categories = {
        "running": (RUNNING_WORKOUTS, "run"),
        "mtb": (MTB_WORKOUTS, "bike"),
        "mtb_advanced": (MTB_ADVANCED_WORKOUTS, "bike"),
        "gravel": (GRAVEL_WORKOUTS, "bike"),
        "triathlon": (TRIATHLON_WORKOUTS, "bike"),
        "swim": (SWIM_WORKOUTS, "bike"),
        "duathlon": (DUATHLON_WORKOUTS, "bike"),
        "cross_training": (CROSS_TRAINING_WORKOUTS, "bike"),
        "gym_functional": (GYM_FUNCTIONAL_WORKOUTS, "bike"),
        "mobility": (MOBILITY_WORKOUTS, "bike"),
        "active_recovery": (ACTIVE_RECOVERY_WORKOUTS, "bike"),
    }

    total = 0
    for subdir, (workouts, sport) in categories.items():
        out_dir = os.path.join(WORKOUTS_DIR, subdir)
        os.makedirs(out_dir, exist_ok=True)
        for w in workouts:
            xml = build_zwo(w["name"], w["desc"], w["category"],
                           w["segments"], sport)
            fname = f"{sanitize(w['name'])}.zwo"
            fpath = os.path.join(out_dir, fname)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(xml)
            total += 1
            print(f"  [{subdir}] {fname}")

    print(f"\nGenerated {total} multi-sport workout files.")


if __name__ == "__main__":
    main()
