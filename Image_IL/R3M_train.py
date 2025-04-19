import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torch.utils.data import DataLoader, Dataset
from PIL import Image
import numpy as np
import pickle
import os
import re
import wandb
import argparse
from r3m.r3m import load_r3m
import gc
import glob
from tqdm import tqdm

parser = argparse.ArgumentParser(description='Behavior Cloning Training')
parser.add_argument('--task_name', type=str, required=True, help='Name of the task')
parser.add_argument('--view_name', type=str, required=True, help='Name of the view')
parser.add_argument('--data_dir', type=str, required=True, help='The path to the directory containing your dataset\'s .pkl files')
args = parser.parse_args()

task_name = args.task_name
view_name = args.view_name

gc.collect()
torch.cuda.empty_cache()
# data_dir = f'/home/jwu220/Trajectory_cloud/Five_task_v2/{task_name}'
# model_save_dir_old = f'/home/jwu220/Trajectory_cloud/IL_model_v2/{task_name}/R3M_{view_name}_view/Model'

# data_dir = "/home/cis2-automated-suturing/Desktop/grayson/grayson_SurgicAI_fork/SurgicAI/RL/hardcoded_expert_traj_data/approach"
# data_dir = f'/home/cis2-automated-suturing/Desktop/grayson/grayson_SurgicAI_fork/SurgicAI/IL_trainsets/Regrasp_debugging'
# data_dir = f'/home/jwu220/Trajectory_cloud/Five_task_v2/{task_name}'
model_save_dir = os.path.join(args.data_dir, "trained_model")

os.makedirs(model_save_dir, exist_ok=True)

r3m_model = load_r3m("resnet50")
r3m_model.eval()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
r3m_model.to(device)

class BehaviorCloningModel(nn.Module):
    def __init__(self, r3m):
        super(BehaviorCloningModel, self).__init__()
        self.r3m = r3m
        self.regressor = nn.Sequential(
            nn.BatchNorm1d(2048 + 7),
            nn.Linear(2048 + 7, 256),
            nn.ReLU(),
            nn.Linear(256, 7),
            nn.Tanh()
        ).to(device)

    def forward(self, x, proprioceptive_data):
        with torch.no_grad():
            visual_features = self.r3m(x)
        combined_input = torch.cat((visual_features, proprioceptive_data), dim=1)
        return self.regressor(combined_input)

bc_model = BehaviorCloningModel(r3m_model)

class PickleDataset(Dataset):
    def __init__(self, data_dir, view_name):
        self.data = []
        self.view_name = view_name
        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        
        # for f in os.listdir(data_dir):
            # if re.match(r'episode_\d+\.pkl$', f):
        print(f"Loading data from dataset {data_dir}...")
        for f in tqdm(glob.glob(os.path.join(data_dir, "*.pkl"))):
            # file_path = os.path.join(data_dir, f)
            file_path = f
            with open(file_path, 'rb') as file:
                trajectory = pickle.load(file)
                self.data.extend(trajectory)
        
        print(f"Total number of data points: {len(self.data)}")

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        step = self.data[idx]
        
        image_data = step['images'][self.view_name]
        img = Image.fromarray(image_data.astype('uint8'), 'RGB') if isinstance(image_data, np.ndarray) else Image.open(image_data).convert('RGB')
        img = self.transform(img)
        
        proprioceptive = torch.tensor(step['obs']['observation'][0:7], dtype=torch.float32)
        action = torch.tensor(step['action'], dtype=torch.float32)
        
        return img, action, proprioceptive

# dataset_old = PickleDataset(data_dir_old, "front")
dataset = PickleDataset(args.data_dir, "cameraL")
train_size = int(0.8 * len(dataset))
test_size = len(dataset) - train_size
train_dataset, test_dataset = torch.utils.data.random_split(dataset, [train_size, test_size])

train_loader = DataLoader(train_dataset, batch_size=256, shuffle=True, num_workers=4)
test_loader = DataLoader(test_dataset, batch_size=256, shuffle=False, num_workers=4)

criterion = nn.MSELoss()
optimizer = torch.optim.Adam(bc_model.parameters(), lr=0.0001)

wandb.init(project="behavior_cloning_v2", name=f"{task_name}_{view_name}_view")
wandb.config.update(args)

def train_and_evaluate(model, train_loader, test_loader, criterion, optimizer, num_epochs, checkpoint_interval):
    print(f"Training for {num_epochs} epochs...")
    for epoch in range(num_epochs):
        model.train()
        total_train_loss = 0
        i = 0
        for images, actions, proprio_data in tqdm(train_loader):
            images, actions, proprio_data = images.to(device), actions.to(device), proprio_data.to(device)
            optimizer.zero_grad()
            outputs = model(images, proprio_data)
            loss = criterion(outputs, actions)
            loss.backward()
            optimizer.step()
            total_train_loss += loss.item()
            i += 1
        
        avg_train_loss = total_train_loss / len(train_loader)
        wandb.log({"Train Loss": avg_train_loss}, step=epoch)
        
        model.eval()
        total_test_loss = 0
        with torch.no_grad():
            for images, actions, proprio_data in test_loader:
                images, actions, proprio_data = images.to(device), actions.to(device), proprio_data.to(device)
                outputs = model(images, proprio_data)
                loss = criterion(outputs, actions)
                total_test_loss += loss.item()
            avg_test_loss = total_test_loss / len(test_loader)
            wandb.log({"Test Loss": avg_test_loss}, step=epoch)
            print(f'Epoch {epoch+1}, Train Loss: {avg_train_loss:.4f}, Test Loss: {avg_test_loss:.4f}')

        if (epoch + 1) % checkpoint_interval == 0 or (epoch + 1) == num_epochs:
            torch.save(model.state_dict(), os.path.join(model_save_dir, f'model_epoch_{epoch+1}.pth'))
            print(f'Model saved at epoch {epoch+1}')

    torch.save(model.state_dict(), os.path.join(model_save_dir, 'model_final.pth'))
    print('Final model saved')

num_epochs = 50
checkpoint_interval = 20
train_and_evaluate(bc_model, train_loader, test_loader, criterion, optimizer, num_epochs, checkpoint_interval)

wandb.finish()