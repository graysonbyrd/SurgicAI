import gymnasium as gym
from stable_baselines3.common.evaluation import evaluate_policy
# from Model_free_Approach.Approach_env_model_free import SRC_approach
from Approach_env import SRC_approach
from Regrasp_env import SRC_regrasp
from Insert_env import SRC_insert
from Pullout_env import SRC_pullout
from subtask_env import SRC_subtask
import numpy as np
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.env_checker import check_env
from stable_baselines3 import HerReplayBuffer, DDPG, PPO, SAC
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.noise import NormalActionNoise
from stable_baselines3.common.utils import set_random_seed
import time
import pickle
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import rospy
from omegaconf import OmegaConf
import os
import cv2
import argparse
from PIL import Image as PIL_Image
import yaml

bridge = CvBridge()

global current_images, image_received
current_images = dict()

def parse_arguments():
    parser = argparse.ArgumentParser(description="Collect expert trajectory data.")
    parser.add_argument('--config', type=str, required=True, help='Name of the task/environment')
    return parser.parse_args()

def cameraL_image_callback(msg):
    """Callback function to store image data"""
    try:
        # Convert the ROS Image message to a CV2 image
        current_images["cameraL"] = bridge.imgmsg_to_cv2(msg, "bgr8")
        image_received = True  # Set flag that a new image is received
    except Exception as e:
        rospy.logerr("Failed to convert image: %s", e)

def policy(obs,action_dim,time_step,noise=None):
    obs_dict = obs
    current = obs_dict['achieved_goal']
    goal = obs_dict['desired_goal']
    dist_vec = np.array(goal-current,dtype = np.float32)
    action = np.where(dist_vec>0,0.7,-0.7).astype(np.float32)
    if time_step%8 == 0:
        noise = np.random.uniform(-1.0, 1.0, size=action.shape)

    # add noise to the action
    if noise is not None:
        action = np.clip(action + noise, -1, 1)
    
    # do not begin closing the gripper angle until the arm is close enough to
    # the needle
    if np.mean((current[:-1] - goal[:-1])**2) > 0.01:
        action[-1] = 0
    else:
        action[-1] *= 0.7

    return action,noise

def get_env_entry_point(task_name: str) -> SRC_subtask:
    if task_name.lower() == "approach":
        return SRC_approach
    elif task_name.lower() == "regrasp":
        return SRC_regrasp
    elif task_name.lower() == "insert":
        return SRC_insert
    elif task_name.lower() == "pullout":
        return SRC_pullout

args = parse_arguments()
config = OmegaConf.load(args.config)
seed = config.seed
set_random_seed(seed)
max_episode_steps=config.max_episode_steps
trans_step = 0.01e-2  # Trans unit in m
angle_step = np.deg2rad(0.5)
jaw_step = 0.05
threshold = [config.trans_error,np.deg2rad(config.angle_error)] # Trans unit in cm

step_size = np.array([trans_step,trans_step,trans_step,angle_step,angle_step,angle_step,jaw_step],dtype=np.float32) 
####################

threshold_expert = [0.1,np.deg2rad(5)]
env_entry_point = get_env_entry_point(config.task_name)
gym.envs.register(id="SAC_HER_sparse", entry_point=env_entry_point, max_episode_steps=max_episode_steps)
env = gym.make("SAC_HER_sparse", render_mode=None,reward_type = "dense",seed = seed, threshold = threshold_expert,max_episode_step=max_episode_steps,step_size=step_size)

# rospy.init_node('expert_data_collector')
image_data = []
task_name = config.task_name
image_subscriber = rospy.Subscriber('/ambf/env/cameras/cameraL/ImageData', Image, cameraL_image_callback)

num_episodes = config.num_episodes # Take 17 mins to collect 1000 trajectories
episode_transitions = []
action_dim = 7
success = 0
max_action = [float('-inf')] * action_dim
min_action = [float('inf')] * action_dim
average_time_step = 0
image_received = False

save_dir = os.path.join("hardcoded_expert_traj_data", task_name.lower())
os.makedirs(save_dir, exist_ok=True)

env.reset()

for episode in range(num_episodes):
    img_idx = 0
    obs,_ = env.reset()
    time.sleep(0.5)
    noise = None
    end_state_count = 0
    episode_transitions = list()
    for timestep in range(max_episode_steps):
        action, noise = policy(obs,action_dim,timestep,noise)
        next_obs, reward, done, _, info = env.step(action)
        time.sleep(0.01)
        transition = {
            "obs": obs,
            "next_obs": next_obs,
            "action": action,
            "reward": np.array([reward], dtype=np.float32),
            "done": np.array([done], dtype=np.float32),
            "info": info,
            "images": current_images.copy()
        }
        episode_transitions.append(transition)
        obs = next_obs
        if done:
            print(timestep)
            average_time_step += timestep
            success+=1
            break

    # save the dataset as a .pkl and each images into an images folder
    save_path = os.path.join(os.path.join(save_dir, f"episode_{episode}_seed_{config.seed}.pkl"))
    with open(save_path, "wb") as file:
        pickle.dump(episode_transitions, file)

average_time_step /= num_episodes
print(f"success rate is {success/num_episodes}")    # Make sure the success rate is 1 !    
print(f"max action range is {max_action}")
print(f"min action range is {min_action}")
print(f"average time step is {average_time_step}")