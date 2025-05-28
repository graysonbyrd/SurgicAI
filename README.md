# Automating Robotic Surgical Suturing using Image-based Imitation Learning

This is the github repo for a Spring 2025 CIS 2 project. Project wiki [here](https://ciis.lcsr.jhu.edu/doku.php?id=courses%3A456%3A2025%3Aprojects%3A456-2025-09%3Aproject-09)

## Installation

To run the code provided in this repo, you must first install the AMBF simulator and a specific commit of the Surgical Robotics Challenge. This also requires an Ubuntu 20.04 machine with ros1 noetic installed on it.

### Install AMBF

Follow the installation procedure outlined [here](https://github.com/WPI-AIM/ambf)

### Install Surgical Robotics Challenge

Click on the submodule in this repository at `surgical_robotics_challenge_old`. That is the commit needed to run the code.

## Running the code

In one terminal, run `~/ambf/bin/lin-x86_64/ambf_simulator --launch_file ~/ambf/surgical_robotics_challenge/launch.yaml -l 0,1,3,4,13,14 -p 200 -t 1 --override_max_comm_freq 120` to initialize the simulation environment with the Surgical Robotics Challenge.


## Stage 1: Data collection

To collect data for a specific suturing subtask, you must first define a domain randomization configuration file. An example configuration file is shown below: 


### Randomizing Lighting

```yaml
task_name: Approach
trans_error: 1
angle_error: 1
seed: 42
max_episode_steps: 2000
num_episodes: 225
use_domain_randomization: True


domain_randomization:
  lighting:
    randomize: True
    bounds: [0.1, 0.9]
    holdout:
      constant: 0.3
      linear: 0.6
      quadratic: 0.2
```

Here you can define domain randomization parameters for the lighting parameter in the environment configuration.

### Randomize Simulation Parameters

To randomize the simulation color parameters, you need to find the location of your shader file for the AMBF simulator. An example python file that randomizes the simulation colors is shown below:

```python
import os
import random

# Path to your file
file_path = os.path.expanduser("/home/cis2-automated-suturing/ambf/surgical_robotics_challenge/ambf_shaders/shader.fs")

# we will not change the colors to this during training, but will use this 
# at inference time
hold_out_colors = {
    "shaded.rrr"
}

# Variants you want to try
values = ["r", "g", "b"]

valid = False
while not valid:
    variant = f"shaded." + random.choice(values) + random.choice(values) + random.choice(values)
    if variant not in hold_out_colors:
        valid = True

# Read all lines
with open(file_path, "r") as f:
    lines = f.readlines()

# Modify line 93 (index 92)
lines[92] = f"    gl_FragColor = vec4({variant}, shadow.a);\n"

# Write back the modified file
with open(file_path, "w") as f:
    f.writelines(lines)

print(f"Updated line 93 to: gl_FragColor = vec4({variant}, shadow.a);")
```

You must restart the simulator each time you wish to ranodmize the colors in this way. You can use a batch script to do this. An example bash script that will automatically randomize the simulator colors and run a training is shown below:

```bash
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
```

More domain randomization parameters can and should be added here using this framework.

To run data collection, run the following:

```bash
python RL/data_collection_hardcoded_expert.py --config <path_to_config.yaml>
```

This will save the data in the following directory: `hardcoded_expert_traj_data/<task_name>/domain_randomization/<name_of_yaml_config_file>`. For example, the the above yaml configuration file name `Approach.yaml`, the dataset save directory would be: `hardcoded_expert_traj_data/approach/domain_randomization/Approach`.

## Stage 2: Model Training

To train a model on your collected data, find the path to the model checkpoint from Stage 1.

```bash
python ImageIL/R3M_train.py --task_name <task_name> \
    --view_name front \
    --data_dir <path_to_data_dir>
```

For example, for the above domain randomization .yaml file, the data_dir would be `hardcoded_expert_traj_data/approach/domain_randomization/Approach`.

## Stage 3: Model Evaluation

To run the model evaluation to see how your model performs, you must run: 

```bash
python Image_IL/Task_evaluation_R3M.py --task_name <task_name> \
    --view_name front \
    --trans_error <trans_error_threshold_for_success_criteria> \
    --angle_error <angle_error_threshold_for_success_criteria> \
    --model_path <path_to_model_checkpoint_file>
```

This will save an evaluation `.txt` file in the same directory as your model path.



