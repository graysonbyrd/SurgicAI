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



