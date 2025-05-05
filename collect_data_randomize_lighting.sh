# Collect Hardcoded Data

# No Domain Randomization
# python RL/data_collection_hardcoded_expert.py --config ./RL/configs/no_randomization_configs/Regrasp.yaml
python RL/data_collection_hardcoded_expert.py --config ./RL/configs/no_randomization_configs/Approach.yaml
# python RL/data_collection_hardcoded_expert.py --config ./RL/configs/no_randomization_configs/Pullout.yaml
# python RL/data_collection_hardcoded_expert.py --config ./RL/configs/no_randomization_configs/Insert.yaml

# Domain Randomization
# python RL/data_collection_hardcoded_expert.py --config ./RL/configs/domain_randomization_configs/Regrasp.yaml
python RL/data_collection_hardcoded_expert.py --config ./RL/configs/domain_randomization_configs/Approach.yaml
# python RL/data_collection_hardcoded_expert.py --config ./RL/configs/domain_randomization_configs/Pullout.yaml
# python RL/data_collection_hardcoded_expert.py --config ./RL/configs/domain_randomization_configs/Insert.yaml

# Train Image IL Models

# Domain Randomization
# python Image_IL/R3M_train.py --task_name Regrasp --view_name front --data_dir ./hardcoded_expert_traj_data/regrasp/domain_randomization/Regrasp
python Image_IL/R3M_train.py --task_name Approach --view_name front --data_dir ./hardcoded_expert_traj_data/approach/domain_randomization/Approach
# python Image_IL/R3M_train.py --task_name Pullout --view_name front --data_dir ./hardcoded_expert_traj_data/pullout/domain_randomization/Pullout
# python Image_IL/R3M_train.py --task_name Insert --view_name front --data_dir ./hardcoded_expert_traj_data/insert/domain_randomization/Insert

# No Domain Randomization
python Image_IL/R3M_train.py --task_name Regrasp --view_name front --data_dir ./hardcoded_expert_traj_data/regrasp/no_randomization/Regrasp
python Image_IL/R3M_train.py --task_name Approach --view_name front --data_dir ./hardcoded_expert_traj_data/approach/no_randomization/Approach
# python Image_IL/R3M_train.py --task_name Pullout --view_name front --data_dir ./hardcoded_expert_traj_data/pullout/no_randomization/Pullout
# python Image_IL/R3M_train.py --task_name Insert --view_name front --data_dir ./hardcoded_expert_traj_data/insert/no_randomization/Insert


