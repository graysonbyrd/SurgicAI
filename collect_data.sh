#!/bin/bash

NUM_RUNS=25

# Disable automatic exit on error
set +e

for ((i=1; i<=NUM_RUNS; i++)); do
    echo "=== Starting iteration $i ==="

    # Randomize simulator colors
    echo "Randomizing simulator colors..."
    python randomize_simulator_colors.py
    if [ $? -ne 0 ]; then
        echo "Failed to randomize colors. Skipping iteration $i."
        continue
    fi

    # Launch the simulator
    echo "Launching simulator..."
    setsid vglrun ~/ambf_updated_commit/ambf/bin/lin-x86_64/ambf_simulator \
        --launch_file ~/ambf/surgical_robotics_challenge/launch.yaml \
        -l 0,1,3,4,13,14 \
        -p 200 \
        -t 1 \
        --override_max_comm_freq 120 & VGL_PID=$!

    sleep 1

    # Check if the simulator actually launched
    if ! ps -p $VGL_PID > /dev/null; then
        echo "Simulator failed to start. Skipping iteration $i."
        continue
    fi

    echo "Simulator PID: $VGL_PID"
    pgid=$(ps -o pgid= "$VGL_PID" | grep -o '[0-9]*')

    if [ -z "$pgid" ]; then
        echo "Failed to retrieve PGID. Skipping iteration $i."
        kill -KILL $VGL_PID 2>/dev/null
        continue
    fi

    echo "Process Group ID: $pgid"

    echo "Running data collection..."
    python RL/data_collection_hardcoded_expert.py \
        --config /home/cis2-automated-suturing/Desktop/grayson/grayson_SurgicAI_fork/SurgicAI/RL/configs/domain_randomization_configs/test.yaml
    echo "Data collection exit code: $?"

    # Kill the entire simulation process group
    echo "Terminating simulator process group..."
    kill -TERM -"$pgid"
    sleep 2
    kill -KILL -"$pgid" 2>/dev/null

    echo "=== Finished iteration $i ==="
    echo
done
