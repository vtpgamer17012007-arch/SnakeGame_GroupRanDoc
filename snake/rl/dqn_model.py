import torch
import torch.nn as nn
import torch.nn.functional as F
import os

class Linear_QNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        # Lớp tuyến tính 1: Từ 11 đầu vào lên 256 node ẩn
        self.linear1 = nn.Linear(input_size, hidden_size)
        # Lớp tuyến tính 2: Từ 256 node ẩn xuống 4 đầu ra (hành động)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def load(self, file_name='best_model.pth'):
        full_path = os.path.join('./models', file_name)
        if os.path.exists(full_path):
            self.load_state_dict(torch.load(full_path))
            self.eval() 
            return True
        return False
    
    def forward(self, x):
        # Chạy dữ liệu qua lớp 1 và dùng hàm kích hoạt ReLU
        x = F.relu(self.linear1(x))
        # Chạy qua lớp 2 để lấy kết quả Q-values cuối cùng
        x = self.linear2(x)
        return x

    def save(self, episode=None, file_name='model.pth'):
        model_folder_path = './models' 
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
        if episode is not None:
            file_name = f'model_ep{episode}.pth'       
        final_path = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), final_path)
        print(f"Model saved to {final_path}")