# Instructions for Jin to recreate results
Hey Jin, this is a repo for you to recreate my results. Feel free to text me if you have any questions if you want to reach me quickly.

## Collect Hardcoded Trajectory Dataset
I tried to copy your hardcoded trajectory code in order to collect a dataset for training an image based imitation learning model.

My script uses a yaml file to provide configuration for the data collection process. Collect data for the `Regrasp` task using the following:

```bash
python RL/data_collection_hardcoded_expert.py --config RL/configs/Regrasp.yaml
```

This will save your dataset in `./hardcoded_expert_traj_data/regrasp`. For each episode, you can use the images saved in the `images` folder for each episode to sanity check the collected data.

## Train your Image-based Imitation Learning Model

I made some very slight modifications to your `R3M_train.py` script to allow for inputting the dataset directory path as an argument. 

Use your collected dataset from the hardcoded expert to train an R3M_train.py model with the following command:

```bash
python Image_IL/R3M_train.py --data_dir hardcoded_expert_traj_data/regrasp --task_name Regrasp --view_name front
```

This will save your model checkpoints IN YOUR DATASET DIRECTORY to keep the models with the data that they were trained on for organization purposes.

## Evaluate your trained Image-based Imitation Learning Model

I also made slight modifications to your `Task_evaluation_R3M.py` script to allow for passing the model checkpoint as a parameter. To evaluate your trained Image_IL model for the regrasp task, run the following:

```bash
python Image_IL/Task_evaluation_R3M.py --task_name Regrasp --view_name front --trans_error 1 --angle_error 1 --model_path hardcoded_expert_traj_data/regrasp/trained_model/model_final.pth
```