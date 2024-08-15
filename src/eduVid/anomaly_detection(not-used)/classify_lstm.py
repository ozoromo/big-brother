import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from torchvision.models import VGG16_Weights, ResNet18_Weights, ResNet50_Weights
from PIL import Image


def find_max_frames(root_dir, labels):
    max_frames = 0
    for label in labels:
        label_dir = os.path.join(root_dir, label)
        if os.path.exists(label_dir):
            for video in os.listdir(label_dir):
                video_dir = os.path.join(label_dir, video)
                num_frames = len(os.listdir(video_dir))
                if num_frames > max_frames:
                    max_frames = num_frames
    return max_frames


class VideoDataset(Dataset):
    def __init__(self, root_dir, transform=None, max_frames=10):
        self.root_dir = root_dir
        self.transform = transform
        self.max_frames = max_frames
        self.data = []
        self.labels = {'BinaryTree': 0, 'NonBinaryTree': 1, 'Directed': 2}
        self.load_data()

    def load_data(self):
        for label in self.labels:
            label_dir = os.path.join(self.root_dir, label)
            if os.path.exists(label_dir):
                for video in os.listdir(label_dir):
                    video_dir = os.path.join(label_dir, video)
                    frames = [os.path.join(video_dir, frame) for frame in os.listdir(video_dir)]
                    self.data.append((frames, self.labels[label]))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        frames, label = self.data[idx]
        images = [Image.open(frame).convert('RGB') for frame in frames]
        if self.transform:
            images = [self.transform(image) for image in images]

        # Padding to handle unequal number of frames
        
        padded_images = torch.zeros((self.max_frames, *images[0].shape))
        padded_images[:len(images)] = torch.stack(images[:self.max_frames])

        return padded_images, label

transform = transforms.Compose([
    transforms.Resize((64, 64)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

labels = ['BinaryTree', 'NonBinaryTree', 'Directed']
max_frames_train = find_max_frames('train/data_frames', labels)
max_frames_val = find_max_frames('val/data_frames', labels)
max_frames = max(max_frames_train, max_frames_val)
print("Max Frames Count: ", max_frames)

train_dataset = VideoDataset(root_dir='train/data_frames', transform=transform, max_frames=max_frames)
val_dataset = VideoDataset(root_dir='val/val_frames', transform=transform, max_frames=max_frames)

train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=4, shuffle=False)

class CNNFeatureExtractor(nn.Module):
    def __init__(self):
        super(CNNFeatureExtractor, self).__init__()
        self.cnn = models.resnet18(weights = ResNet18_Weights.IMAGENET1K_V1)
        self.cnn.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
        self.cnn = nn.Sequential(*list(self.cnn.children())[:-1])  # Remove the classification layer

    def forward(self, x):
        features = self.cnn(x)
        features = features.view(features.size(0), -1)  # Flatten the features
        return features


class VideoClassifier(nn.Module):
    def __init__(self, cnn, num_classes=3):
        super(VideoClassifier, self).__init__()
        self.cnn = cnn
        self.lstm = nn.LSTM(512, hidden_size=128, num_layers=2,  batch_first=True)
        self.fc = nn.Linear(128, num_classes)

    def forward(self, x):
        batch_size, seq_len, c, h, w = x.size()
        c_in = x.view(batch_size * seq_len, c, h, w)
        c_out = self.cnn(c_in)
        r_in = c_out.view(batch_size, seq_len, -1)
        r_out, _ = self.lstm(r_in)
        r_out = r_out[:, -1, :]  # Get the last output of the sequence
        out = self.fc(r_out)
        return out


cnn = CNNFeatureExtractor()
model = VideoClassifier(cnn=cnn, num_classes=3)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

num_epochs = 10

print("Training Started.")
for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    for i, (inputs, labels) in enumerate(train_loader):
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
        if i % 10 == 9:  # Print every 10 batches
            print(f"[{epoch + 1}, {i + 1}] loss: {running_loss / 10:.3f}")
            running_loss = 0.0

    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for inputs, labels in val_loader:
            outputs = model(inputs)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    print(f"Validation accuracy after epoch {epoch + 1}: {100 * correct / total:.2f}%")

print('Finished Training')

torch.save(model.state_dict(), 'model.pth')
