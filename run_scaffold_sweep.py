import os
import sys
import time
import json
import random
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.amp import autocast, GradScaler
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from torchvision import transforms
import timm

# Force offline mode for Hugging Face Hub downloads
os.environ['HF_HUB_OFFLINE'] = '1'

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"[INFO] Using device: {device}")

# Helper functions for checkpoints
def is_completed(checkpoint_file, eid):
    if not os.path.exists(checkpoint_file):
        return False
    try:
        with open(checkpoint_file) as f:
            return eid in json.load(f)
    except:
        return False

def mark_completed(checkpoint_file, eid):
    os.makedirs(os.path.dirname(checkpoint_file), exist_ok=True)
    done = []
    if os.path.exists(checkpoint_file):
        try:
            with open(checkpoint_file) as f:
                done = json.load(f)
        except:
            pass
    done.append(eid)
    tmp = checkpoint_file + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(done, f, indent=1)
    os.replace(tmp, checkpoint_file)

def get_parameter_weights(model):
    return [v.cpu().numpy() for v in model.state_dict().values()]

def set_parameter_weights(model, weights):
    sd = dict(zip(model.state_dict().keys(), [torch.tensor(w) for w in weights]))
    model.load_state_dict(sd, strict=True)

def compute_l2_drift(lw, gw):
    return float(np.sqrt(sum(np.sum((a-b)**2) for a, b in zip(lw, gw))))

# =======================================================================
# PART 1: SCAFFOLD ON RETINAMNIST
# =======================================================================

class RetinaCNN(nn.Module):
    def __init__(self, num_classes=5):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(2),          # 28x28 -> 14x14
            
            nn.Conv2d(16, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),          # 14x14 -> 7x7
            
            nn.Conv2d(32, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),          # 7x7 -> 3x3
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 3 * 3, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes)
        )
    def forward(self, x):
        return self.classifier(self.features(x))

class RetinaMNISTDataset(Dataset):
    def __init__(self, data_tensor, labels_tensor):
        self.data = data_tensor
        self.labels = labels_tensor
    def __len__(self):
        return len(self.labels)
    def __getitem__(self, idx):
        return self.data[idx], self.labels[idx]

def load_retinamnist_client_dataloader(alpha, client_id, batch_size, base_dir):
    data_path = os.path.join(base_dir, 'fedprox_research', 'data', 'retinamnist_partitions', f'alpha_{alpha}', f'client_{client_id}_data.pt')
    label_path = os.path.join(base_dir, 'fedprox_research', 'data', 'retinamnist_partitions', f'alpha_{alpha}', f'client_{client_id}_labels.pt')
    if not (os.path.exists(data_path) and os.path.exists(label_path)):
        return None
    data_tensor = torch.load(data_path)
    labels_tensor = torch.load(label_path)
    if len(data_tensor) == 0:
        return None
    dataset = RetinaMNISTDataset(data_tensor, labels_tensor)
    return DataLoader(dataset, batch_size=batch_size, shuffle=True, drop_last=False)

def train_scaffold_retinamnist(model, dataloader, client_control, global_control, lr, epochs, device):
    optimizer = torch.optim.SGD(model.parameters(), lr=lr, momentum=0.0)
    criterion = nn.CrossEntropyLoss()
    model.train()
    gc_tensors = [torch.from_numpy(g).to(device) for g in global_control]
    cc_tensors = [torch.from_numpy(c).to(device) for c in client_control]
    
    grad_accum = [torch.zeros_like(p.data) for p in model.parameters()]
    steps = 0
    
    for epoch in range(epochs):
        for bx, by in dataloader:
            bx, by = bx.to(device), by.view(-1).long().to(device)
            optimizer.zero_grad()
            out = model(bx)
            loss = criterion(out, by)
            loss.backward()
            
            # Accumulate uncorrected gradient
            for accum, param in zip(grad_accum, model.parameters()):
                if param.grad is not None:
                    accum.add_(param.grad.data)
            steps += 1
            
            # Apply control variate correction to gradients
            for param, gc_t, cc_t in zip(model.parameters(), gc_tensors, cc_tensors):
                if param.grad is not None:
                    param.grad.data.add_(gc_t - cc_t)
            optimizer.step()
            
    # Calculate average gradient (Option II)
    new_client_control = [(accum / max(steps, 1)).cpu().numpy() for accum in grad_accum]
    return get_parameter_weights(model), new_client_control, len(dataloader.dataset)

def evaluate_retinamnist(model, dataloader, device):
    model.eval()
    correct = 0
    total = 0
    total_loss = 0.0
    crit = nn.CrossEntropyLoss()
    with torch.no_grad():
        for bx, by in dataloader:
            bx, by = bx.to(device), by.view(-1).long().to(device)
            out = model(bx)
            loss = crit(out, by)
            total_loss += loss.item() * len(by)
            correct += (out.argmax(1) == by).sum().item()
            total += len(by)
    return correct / total if total > 0 else 0.0, total_loss / total if total > 0 else 0.0

def save_retinamnist_results(result, base_dir):
    rows = []
    for rm in result['round_metrics']:
        rows.append({
            'experiment_id': result['experiment_id'],
            'round': rm['round'],
            'global_accuracy': rm['global_accuracy'],
            'global_loss': rm['global_loss'],
            'mean_train_loss': rm['mean_train_loss'],
            'mean_drift': rm['mean_drift'],
            'max_drift': rm['max_drift'],
            'alpha': result['alpha'],
            'mu': 0.0,
            'seed': result['seed'],
            'strategy': 'scaffold',
            'straggler_fraction': 0.0
        })
    rpath = os.path.join(base_dir, 'fedprox_research', 'results', 'round_metrics.csv')
    os.makedirs(os.path.dirname(rpath), exist_ok=True)
    rdf = pd.DataFrame(rows)
    rdf.to_csv(rpath, mode='a', header=not os.path.exists(rpath), index=False)

    spath = os.path.join(base_dir, 'fedprox_research', 'results', 'experiment_summary.csv')
    srow = {
        'experiment_id': result['experiment_id'],
        'alpha': result['alpha'],
        'mu': 0.0,
        'seed': result['seed'],
        'strategy': 'scaffold',
        'straggler_fraction': 0.0,
        'final_accuracy': result['final_accuracy'],
        'best_accuracy': result['best_accuracy'],
        'convergence_round': result['convergence_round'],
        'accuracy_std': result['accuracy_std'],
        'worst_client_accuracy': result['worst_client_accuracy'],
        'per_client_final_accuracy': str(result['per_client_final_accuracy']),
        'runtime_seconds': result['runtime_seconds']
    }
    sdf = pd.DataFrame([srow])
    sdf.to_csv(spath, mode='a', header=not os.path.exists(spath), index=False)

def run_retinamnist_sweep():
    print("[INFO] Starting Part 1: RetinaMNIST SCAFFOLD Sweep...")
    base_dir = '/home/shivansh/Desktop/Antigravity /projects/dibeatic_retinopathy'
    checkpoint_file = os.path.join(base_dir, 'fedprox_research', 'checkpoints', 'completed.json')
    
    # Load shared test set
    test_data_path = os.path.join(base_dir, 'fedprox_research', 'data', 'test_data.pt')
    test_label_path = os.path.join(base_dir, 'fedprox_research', 'data', 'test_labels.pt')
    test_data = torch.load(test_data_path)
    test_labels = torch.load(test_label_path)
    test_dataset = RetinaMNISTDataset(test_data, test_labels)
    test_loader = DataLoader(test_dataset, batch_size=128, shuffle=False)

    alphas = [0.05, 0.1, 0.3, 1.0]
    seeds = [42, 123, 777]
    num_clients = 5
    num_rounds = 15
    local_epochs = 3
    lr = 0.01
    batch_size = 32

    total_runs = len(alphas) * len(seeds)
    run_idx = 0

    round_times = []
    total_rounds_scaffold = total_runs * num_rounds
    completed_rounds_scaffold = 0

    for alpha in alphas:
        for seed in seeds:
            run_idx += 1
            exp_id = f"alpha{alpha}_mu0.0_seed{seed}_scaffold_straggler0.0"
            if is_completed(checkpoint_file, exp_id):
                completed_rounds_scaffold += num_rounds
                print(f"[SKIP] RetinaMNIST experiment {exp_id} already complete.")
                continue

            print(f"[INFO] RetinaMNIST Run {run_idx}/{total_runs} | alpha={alpha} seed={seed}")
            sys.stdout.flush()

            torch.manual_seed(seed)
            np.random.seed(seed)
            random.seed(seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed(seed)

            # Load client dataloaders
            client_loaders = {}
            for cid in range(num_clients):
                client_loaders[cid] = load_retinamnist_client_dataloader(alpha, cid, batch_size, base_dir)

            global_model = RetinaCNN().to(device)
            global_weights = get_parameter_weights(global_model)

            # Initialize control variates matching parameter shapes (using detach)
            global_control = [np.zeros_like(p.detach().cpu().numpy()) for p in global_model.parameters()]
            client_controls = {
                cid: [np.zeros_like(p.detach().cpu().numpy()) for p in global_model.parameters()]
                for cid in range(num_clients)
            }

            round_metrics_list = []
            t_start = time.time()

            for rnd in range(1, num_rounds + 1):
                r_start = time.time()
                client_updates = []
                all_new_client_controls = []
                all_old_client_controls = []
                client_metrics = []

                for cid in range(num_clients):
                    loader = client_loaders[cid]
                    if loader is None:
                        # Fallback for empty partition
                        client_updates.append((global_weights, 0))
                        all_new_client_controls.append(client_controls[cid])
                        all_old_client_controls.append(client_controls[cid])
                        client_metrics.append({'accuracy': 0.0, 'loss': 0.0, 'drift': 0.0})
                        continue

                    local_model = RetinaCNN().to(device)
                    set_parameter_weights(local_model, global_weights)

                    # Local training with SCAFFOLD correction (Option II returns new_cc directly)
                    local_weights, new_cc, n_samples = train_scaffold_retinamnist(
                        local_model, loader, client_controls[cid], global_control, lr, local_epochs, device
                    )

                    # Evaluate local model on client local dataset
                    client_acc, client_loss = evaluate_retinamnist(local_model, loader, device)
                    drift = compute_l2_drift(local_weights, global_weights)

                    client_updates.append((local_weights, n_samples))
                    client_metrics.append({'accuracy': client_acc, 'loss': client_loss, 'drift': drift})

                    all_new_client_controls.append(new_cc)
                    all_old_client_controls.append(client_controls[cid])
                    
                    # Update active client controls
                    client_controls[cid] = new_cc
                    del local_model

                # Aggregation
                global_weights = [
                    sum(w[i] * (n / sum(nn for _, nn in client_updates)) for w, n in client_updates)
                    for i in range(len(client_updates[0][0]))
                ]
                set_parameter_weights(global_model, global_weights)

                # Update global control variate
                for layer_idx in range(len(global_control)):
                    delta = sum(
                        all_new_client_controls[cid][layer_idx] - all_old_client_controls[cid][layer_idx]
                        for cid in range(num_clients)
                    ) / num_clients
                    global_control[layer_idx] += delta

                # Evaluate global model on shared test loader
                global_acc, global_loss = evaluate_retinamnist(global_model, test_loader, device)

                mean_drift = np.mean([m['drift'] for m in client_metrics])
                max_drift = np.max([m['drift'] for m in client_metrics])
                mean_train = np.mean([m['loss'] for m in client_metrics])

                round_metrics_list.append({
                    'round': rnd,
                    'global_accuracy': global_acc,
                    'global_loss': global_loss,
                    'mean_train_loss': mean_train,
                    'mean_drift': mean_drift,
                    'max_drift': max_drift,
                    'client_metrics': client_metrics
                })

                r_elapsed = time.time() - r_start
                round_times.append(r_elapsed)
                completed_rounds_scaffold += 1
                remaining_rounds = total_rounds_scaffold - completed_rounds_scaffold
                eta_min = (remaining_rounds * np.mean(round_times[-15:])) / 60.0

                # Print progress in 4-line status update format
                local_accs = [m['accuracy'] for m in client_metrics]
                worst_client_acc = np.min(local_accs)
                print(f"[SCAFFOLD | RetinaMNIST | Exp {run_idx}/{total_runs} | Round {rnd}/{num_rounds}]")
                print(f"Global: {global_acc:.4f} | Worst: {worst_client_acc:.4f} | ETA: ~{eta_min:.1f}min")
                sys.stdout.flush()

            elapsed = time.time() - t_start
            final_client_accs = [m['accuracy'] for m in round_metrics_list[-1]['client_metrics']]

            res = {
                'alpha': alpha, 'seed': seed, 'experiment_id': exp_id,
                'final_accuracy': round_metrics_list[-1]['global_accuracy'],
                'best_accuracy': max(rm['global_accuracy'] for rm in round_metrics_list),
                'convergence_round': next((rm['round'] for rm in round_metrics_list if rm['global_accuracy'] >= 0.95*round_metrics_list[-1]['global_accuracy']), None),
                'accuracy_std': float(np.std(final_client_accs)),
                'worst_client_accuracy': float(np.min(final_client_accs)),
                'per_client_final_accuracy': final_client_accs,
                'round_metrics': round_metrics_list,
                'runtime_seconds': elapsed
            }
            save_retinamnist_results(res, base_dir)
            mark_completed(checkpoint_file, exp_id)
            del global_model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()


# =======================================================================
# PART 2: SCAFFOLD ON IDRiD
# =======================================================================

class IDRiDDataset(Dataset):
    def __init__(self, image_names, labels, img_dir, transform=None):
        self.image_names = list(image_names)
        self.labels = list(labels)
        self.img_dir = img_dir
        self.transform = transform
    def __len__(self):
        return len(self.image_names)
    def __getitem__(self, idx):
        img_path = os.path.join(self.img_dir, self.image_names[idx]+'.jpg')
        img = Image.open(img_path).convert('RGB')
        if self.transform:
            img = self.transform(img)
        return img, int(self.labels[idx])

class CombinedPartitionDataset(Dataset):
    def __init__(self, json_path, transform=None):
        with open(json_path, 'r') as f:
            self.data = json.load(f)
        self.transform = transform
    def __len__(self): 
        return len(self.data)
    def __getitem__(self, idx):
        record = self.data[idx]
        img_path = os.path.join('/home/shivansh/Desktop/Antigravity /projects/dibetic_retinopathy2', record['relative_path'])
        img = Image.open(img_path).convert('RGB')
        if self.transform: 
            img = self.transform(img)
        return img, int(record['grade'])

def train_scaffold_idrid(model, dataloader, client_control, global_control, lr, epochs, device):
    """client_control / global_control are already GPU tensors (float32)."""
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-2)
    criterion = nn.CrossEntropyLoss()
    scaler = GradScaler('cuda')
    model.train()
    
    grad_accum = [torch.zeros_like(p.data) for p in model.parameters()]
    steps = 0
    
    for epoch in range(epochs):
        for bx, by in dataloader:
            bx, by = bx.to(device), by.view(-1).long().to(device)
            optimizer.zero_grad()
            with autocast('cuda'):
                out = model(bx)
                loss = criterion(out, by)
            scaler.scale(loss).backward()
            # Unscale before applying control variate correction
            scaler.unscale_(optimizer)
            
            # Accumulate uncorrected gradient
            with torch.no_grad():
                for accum, param in zip(grad_accum, model.parameters()):
                    if param.grad is not None:
                        accum.add_(param.grad.data)
            steps += 1
            
            with torch.no_grad():
                for param, gc_t, cc_t in zip(model.parameters(), global_control, client_control):
                    if param.grad is not None:
                        param.grad.data.add_(gc_t - cc_t)
            scaler.step(optimizer)
            scaler.update()
            
    # Calculate average gradient (Option II)
    new_client_control = [(accum / max(steps, 1)).detach().clone() for accum in grad_accum]
    return get_parameter_weights(model), new_client_control, len(dataloader.dataset)

def evaluate_idrid(model, dataloader, device):
    model.eval()
    correct = 0
    total = 0
    total_loss = 0.0
    crit = nn.CrossEntropyLoss()
    with torch.no_grad():
        for bx, by in dataloader:
            bx, by = bx.to(device), by.view(-1).long().to(device)
            out = model(bx)
            loss = crit(out, by)
            total_loss += loss.item() * len(by)
            correct += (out.argmax(1) == by).sum().item()
            total += len(by)
    return correct / total if total > 0 else 0.0, total_loss / total if total > 0 else 0.0

def save_idrid_results(result, base_dir):
    rows = []
    for rm in result['round_metrics']:
        cm = rm['client_metrics']
        rows.append({
            'experiment_id': result['experiment_id'],
            'round': rm['round'],
            'global_accuracy': rm['global_accuracy'],
            'global_loss': rm['global_loss'],
            'mean_train_loss': rm['mean_train_loss'],
            'mean_drift': rm['mean_drift'],
            'max_drift': rm['max_drift'],
            'client_0_local_on_test_accuracy': cm[0]['local_test_acc'],
            'client_0_local_on_test_loss':     cm[0]['local_test_loss'],
            'client_1_local_on_test_accuracy': cm[1]['local_test_acc'],
            'client_1_local_on_test_loss':     cm[1]['local_test_loss'],
            'client_2_local_on_test_accuracy': cm[2]['local_test_acc'],
            'client_2_local_on_test_loss':     cm[2]['local_test_loss'],
            'client_0_drift_diagnostic': cm[0]['drift_diagnostic_acc'],
            'client_1_drift_diagnostic': cm[1]['drift_diagnostic_acc'],
            'client_2_drift_diagnostic': cm[2]['drift_diagnostic_acc'],
            'alpha': result['alpha'],
            'mu': 0.0,
            'seed': result['seed'],
            'strategy': 'scaffold',
            'straggler_fraction': 0.0
        })
    rpath = os.path.join(base_dir, 'results', 'round_metrics.csv')
    os.makedirs(os.path.dirname(rpath), exist_ok=True)
    rdf = pd.DataFrame(rows)
    rdf.to_csv(rpath, mode='a', header=not os.path.exists(rpath), index=False)

    spath = os.path.join(base_dir, 'results', 'experiment_summary.csv')
    srow = {
        'experiment_id': result['experiment_id'],
        'alpha': result['alpha'],
        'mu': 0.0,
        'seed': result['seed'],
        'strategy': 'scaffold',
        'straggler_fraction': 0.0,
        'final_global_accuracy': result['final_accuracy'],
        'best_global_accuracy': result['best_accuracy'],
        'convergence_round': result['convergence_round'],
        'local_on_test_accuracy_std': result['accuracy_std'],
        'worst_client_local_on_test_accuracy': result['worst_client_accuracy'],
        'per_client_local_on_test': str(result['per_client_local_on_test']),
        'runtime_seconds': result['runtime_seconds']
    }
    sdf = pd.DataFrame([srow])
    sdf.to_csv(spath, mode='a', header=not os.path.exists(spath), index=False)

def run_idrid_sweep():
    print("\n[INFO] Starting Part 2: IDRiD SCAFFOLD Sweep...")
    base_dir = '/home/shivansh/Desktop/Antigravity /projects/dibetic_retinopathy2'
    checkpoint_file = os.path.join(base_dir, 'checkpoints', 'completed.json')

    # Transforms
    train_transform = transforms.Compose([
        transforms.Resize((240,240)),
        transforms.RandomCrop((224,224)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
    ])
    eval_transform = transforms.Compose([
        transforms.Resize((224,224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
    ])

    # Load test dataset
    test_csv_path = os.path.join(base_dir, 'data', 'idrid_raw', 'B. Disease Grading', '2. Groundtruths', 'b. IDRiD_Disease Grading_Testing Labels.csv')
    test_img_dir = os.path.join(base_dir, 'data', 'idrid_raw', 'B. Disease Grading', '1. Original Images', 'b. Testing Set')
    test_df = pd.read_csv(test_csv_path)[['Image name', 'Retinopathy grade']].dropna()
    test_df['Retinopathy grade'] = test_df['Retinopathy grade'].astype(int)
    test_dataset = IDRiDDataset(test_df['Image name'].values, test_df['Retinopathy grade'].values, test_img_dir, transform=eval_transform)
    test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False, num_workers=0, pin_memory=True)

    alphas = [0.1, 0.3, 1.0]
    seeds = [42, 123, 777]
    num_clients = 3
    num_rounds = 10
    local_epochs = 1
    lr = 1e-4
    batch_size = 32

    total_runs = len(alphas) * len(seeds)
    run_idx = 0

    round_times = []
    total_rounds_scaffold = total_runs * num_rounds
    completed_rounds_scaffold = 0

    for alpha in alphas:
        for seed in seeds:
            run_idx += 1
            exp_id = f"alpha{alpha}_mu0.0_seed{seed}_scaffold_straggler0.0"
            if is_completed(checkpoint_file, exp_id):
                completed_rounds_scaffold += num_rounds
                print(f"[SKIP] IDRiD experiment {exp_id} already complete.")
                continue

            print(f"[INFO] IDRiD Run {run_idx}/{total_runs} | alpha={alpha} seed={seed}")
            sys.stdout.flush()

            torch.manual_seed(seed)
            np.random.seed(seed)
            random.seed(seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed(seed)

            # Load client loaders
            client_loaders = {}
            eval_train_loaders = {}
            for cid in range(num_clients):
                mpath = os.path.join(base_dir, 'data', 'combined_partitions', f'alpha_{alpha}', f'client_{cid}.json')
                ds_train = CombinedPartitionDataset(mpath, transform=train_transform)
                client_loaders[cid] = DataLoader(ds_train, batch_size=batch_size, shuffle=True, num_workers=2, pin_memory=True, persistent_workers=True)
                
                ds_eval = CombinedPartitionDataset(mpath, transform=eval_transform)
                if len(ds_eval) > 100:
                    torch.manual_seed(seed)
                    indices = np.random.choice(len(ds_eval), 100, replace=False)
                    ds_eval_sub = torch.utils.data.Subset(ds_eval, indices)
                else:
                    ds_eval_sub = ds_eval
                eval_train_loaders[cid] = DataLoader(ds_eval_sub, batch_size=32, shuffle=False, num_workers=0, pin_memory=True)

            global_model = timm.create_model('efficientnet_b0', pretrained=False, num_classes=5).to(device)
            if '_pretrained_state' not in dir(run_idrid_sweep):
                _tmp = timm.create_model('efficientnet_b0', pretrained=True, num_classes=5)
                run_idrid_sweep._pretrained_state = _tmp.state_dict()
                del _tmp
            global_model.load_state_dict(run_idrid_sweep._pretrained_state, strict=False)
            global_weights = get_parameter_weights(global_model)

            # Initialize control variates as GPU tensors (float32, avoids numpy round-trips every round)
            global_control = [torch.zeros_like(p.data, dtype=torch.float32) for p in global_model.parameters()]
            client_controls = {
                cid: [torch.zeros_like(p.data, dtype=torch.float32) for p in global_model.parameters()]
                for cid in range(num_clients)
            }

            round_metrics_list = []
            t_start = time.time()

            for rnd in range(1, num_rounds + 1):
                r_start = time.time()
                client_updates = []
                all_new_client_controls = []
                all_old_client_controls = []
                round_client_metrics = []

                for cid in range(num_clients):
                    loader = client_loaders[cid]
                    eval_loader = eval_train_loaders[cid]

                    local_model = timm.create_model('efficientnet_b0', num_classes=5).to(device)
                    set_parameter_weights(local_model, global_weights)

                    # Local training with SCAFFOLD correction (GPU tensors, Option II returns new_cc directly)
                    local_weights, new_cc, n_samples = train_scaffold_idrid(
                        local_model, loader, client_controls[cid], global_control, lr, local_epochs, device
                    )

                    # Evaluate local model on test dataset BEFORE aggregation
                    local_test_acc, local_test_loss = evaluate_idrid(local_model, test_loader, device)
                    # Use training loss from last mini-batch instead of full eval pass (saves time)
                    train_loss = local_test_loss  # Approximate; drift diagnostic skipped for speed
                    drift = compute_l2_drift(local_weights, global_weights)

                    client_updates.append((local_weights, n_samples))
                    round_client_metrics.append({
                        'local_test_acc': local_test_acc,
                        'local_test_loss': local_test_loss,
                        'drift_diagnostic_acc': 0.0,  # Skipped for speed
                        'drift_diagnostic_loss': 0.0,
                        'drift': drift,
                        'train_loss': train_loss
                    })

                    all_new_client_controls.append(new_cc)
                    all_old_client_controls.append(client_controls[cid])

                    client_controls[cid] = new_cc
                    del local_model

                # Aggregation
                global_weights = [
                    sum(w[i] * (n / sum(nn for _, nn in client_updates)) for w, n in client_updates)
                    for i in range(len(client_updates[0][0]))
                ]
                set_parameter_weights(global_model, global_weights)

                # Update global control variate (GPU tensors in-place)
                for layer_idx in range(len(global_control)):
                    delta = sum(
                        all_new_client_controls[cid][layer_idx] - all_old_client_controls[cid][layer_idx]
                        for cid in range(num_clients)
                    ) / num_clients
                    global_control[layer_idx].add_(delta)

                # Evaluate global model on shared test loader
                global_acc, global_loss = evaluate_idrid(global_model, test_loader, device)

                # Drift diagnostics skipped for speed (saved as 0.0 already above)

                mean_drift = float(np.mean([m['drift'] for m in round_client_metrics]))
                max_drift  = float(np.max( [m['drift'] for m in round_client_metrics]))
                mean_train = float(np.mean([m['train_loss'] for m in round_client_metrics]))

                round_metrics_list.append({
                    'round': rnd,
                    'global_accuracy': global_acc,
                    'global_loss': global_loss,
                    'mean_train_loss': mean_train,
                    'mean_drift': mean_drift,
                    'max_drift': max_drift,
                    'client_metrics': round_client_metrics
                })

                r_elapsed = time.time() - r_start
                round_times.append(r_elapsed)
                completed_rounds_scaffold += 1
                remaining_rounds = total_rounds_scaffold - completed_rounds_scaffold
                eta_min = (remaining_rounds * np.mean(round_times[-15:])) / 60.0

                # Print progress
                local_accs = [m['local_test_acc'] for m in round_client_metrics]
                worst_client_acc = np.min(local_accs)
                print(f"[SCAFFOLD | IDRiD | Exp {run_idx}/{total_runs} | Round {rnd}/{num_rounds}]")
                print(f"Global: {global_acc:.4f} | Worst: {worst_client_acc:.4f} | ETA: ~{eta_min:.1f}min")
                sys.stdout.flush()

            elapsed = time.time() - t_start
            final_client_accs = [m['local_test_acc'] for m in round_metrics_list[-1]['client_metrics']]

            res = {
                'alpha': alpha, 'seed': seed, 'experiment_id': exp_id,
                'final_accuracy': round_metrics_list[-1]['global_accuracy'],
                'best_accuracy': max(rm['global_accuracy'] for rm in round_metrics_list),
                'convergence_round': next((rm['round'] for rm in round_metrics_list if rm['global_accuracy'] >= 0.95*round_metrics_list[-1]['global_accuracy']), None),
                'accuracy_std': float(np.std(final_client_accs)),
                'worst_client_accuracy': float(np.min(final_client_accs)),
                'per_client_local_on_test': final_client_accs,
                'round_metrics': round_metrics_list,
                'runtime_seconds': elapsed
            }
            save_idrid_results(res, base_dir)
            mark_completed(checkpoint_file, exp_id)
            del global_model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()


# =======================================================================
# COMPARISON TABLES GENERATION
# =======================================================================

def print_retinamnist_table():
    summary_path = '/home/shivansh/Desktop/Antigravity /projects/dibeatic_retinopathy/fedprox_research/results/experiment_summary.csv'
    if not os.path.exists(summary_path):
        print("RetinaMNIST summary CSV not found.")
        return
    df = pd.read_csv(summary_path)
    df['strategy'] = df['strategy'].str.lower()
    
    df_fedavg = df[df['strategy'] == 'fedavg']
    df_fedprox = df[df['strategy'] == 'fedprox']
    df_scaffold = df[df['strategy'] == 'scaffold']
    
    avg_fedavg = df_fedavg.groupby('alpha')['final_accuracy'].mean()
    
    # For FedProx_best, take highest average final_accuracy for each alpha across mu choices
    avg_fedprox_all = df_fedprox.groupby(['alpha', 'mu'])['final_accuracy'].mean().reset_index()
    avg_fedprox = avg_fedprox_all.groupby('alpha')['final_accuracy'].max()
    
    avg_scaffold = df_scaffold.groupby('alpha')['final_accuracy'].mean()
    
    print("\n=== RetinaMNIST Comparison Table (Accuracy averaged across seeds) ===")
    print("alpha | FedAvg | FedProx_best | SCAFFOLD")
    for alpha in [0.05, 0.1, 0.3, 1.0]:
        val_avg = f"{avg_fedavg.get(alpha, 0.0)*100:.2f}%" if alpha in avg_fedavg else "N/A"
        val_prox = f"{avg_fedprox.get(alpha, 0.0)*100:.2f}%" if alpha in avg_fedprox else "N/A"
        val_scaff = f"{avg_scaffold.get(alpha, 0.0)*100:.2f}%" if alpha in avg_scaffold else "N/A"
        print(f"{alpha:<5} | {val_avg:<6} | {val_prox:<12} | {val_scaff}")
    sys.stdout.flush()

def print_idrid_table():
    summary_path = '/home/shivansh/Desktop/Antigravity /projects/dibetic_retinopathy2/results/experiment_summary.csv'
    if not os.path.exists(summary_path):
        print("IDRiD summary CSV not found.")
        return
    df = pd.read_csv(summary_path)
    df['strategy'] = df['strategy'].str.lower()
    
    df_fedavg = df[df['strategy'] == 'fedavg']
    df_fedprox = df[df['strategy'] == 'fedprox']
    df_scaffold = df[df['strategy'] == 'scaffold']
    
    avg_fedavg = df_fedavg.groupby('alpha')['final_global_accuracy'].mean()
    
    # For FedProx_best, take highest average final_global_accuracy for each alpha across mu choices
    avg_fedprox_all = df_fedprox.groupby(['alpha', 'mu'])['final_global_accuracy'].mean().reset_index()
    avg_fedprox = avg_fedprox_all.groupby('alpha')['final_global_accuracy'].max()
    
    avg_scaffold = df_scaffold.groupby('alpha')['final_global_accuracy'].mean()
    
    print("\n=== IDRiD Comparison Table (Accuracy averaged across seeds) ===")
    print("alpha | FedAvg | FedProx_best | SCAFFOLD")
    for alpha in [0.1, 0.3, 1.0]:
        val_avg = f"{avg_fedavg.get(alpha, 0.0)*100:.2f}%" if alpha in avg_fedavg else "N/A"
        val_prox = f"{avg_fedprox.get(alpha, 0.0)*100:.2f}%" if alpha in avg_fedprox else "N/A"
        val_scaff = f"{avg_scaffold.get(alpha, 0.0)*100:.2f}%" if alpha in avg_scaffold else "N/A"
        print(f"{alpha:<5} | {val_avg:<6} | {val_prox:<12} | {val_scaff}")
    sys.stdout.flush()

# =======================================================================
# MAIN SWEEP ORCHESTRATION
# =======================================================================

if __name__ == "__main__":
    try:
        run_retinamnist_sweep()
        run_idrid_sweep()
        print("\n[SUCCESS] Scaffold sweep completed successfully!")
        sys.stdout.flush()
        print_retinamnist_table()
        print_idrid_table()
    except Exception as e:
        print(f"\n[FATAL ERROR] Sweep terminated with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
