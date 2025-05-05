python Image_IL/Task_evaluation_R3M.py \
    --task_name Regrasp \
    --view_name front \
    --trans_error 5 \
    --angle_error 15 \
    --model_path /home/cis2-automated-suturing/Desktop/grayson/grayson_SurgicAI_fork/SurgicAI/hardcoded_expert_traj_data/regrasp/domain_randomization/Regrasp/trained_model/model_epoch_20.pth

python Image_IL/Task_evaluation_R3M.py \
    --task_name Regrasp \
    --view_name front \
    --trans_error 5 \
    --angle_error 15 \
    --model_path /home/cis2-automated-suturing/Desktop/grayson/grayson_SurgicAI_fork/SurgicAI/hardcoded_expert_traj_data/regrasp/no_randomization/Regrasp/trained_model/model_epoch_20.pth

python Image_IL/Task_evaluation_R3M.py \
    --task_name Pullout \
    --view_name front \
    --trans_error 1 \
    --angle_error 60 \
    --model_path /home/cis2-automated-suturing/Desktop/grayson/grayson_SurgicAI_fork/SurgicAI/hardcoded_expert_traj_data/pullout/domain_randomization/Pullout/trained_model_75_eps/model_final.pth

python Image_IL/Task_evaluation_R3M.py \
    --task_name Pullout \
    --view_name front \
    --trans_error 1 \
    --angle_error 60 \
    --model_path /home/cis2-automated-suturing/Desktop/grayson/grayson_SurgicAI_fork/SurgicAI/hardcoded_expert_traj_data/pullout/no_randomization/Pullout/trained_model_75_eps/model_final.pth