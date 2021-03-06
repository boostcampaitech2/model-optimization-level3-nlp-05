"""Baseline train
- Author: Junghoon Kim
- Contact: placidus36@gmail.com
"""

import argparse
import os
from datetime import datetime
from typing import Any, Dict, Tuple, Union

import torch
import torch.nn as nn
import torch.optim as optim
import yaml

import timm

from src.dataloader import create_dataloader
from src.loss import CustomCriterion
from src.model import Model
from src.trainer import TorchTrainer, count_model_params
from src.utils.common import get_label_counts, read_yaml
from src.utils.torch_utils import check_runtime, model_info

import wandb

def train(
    model_config: Dict[str, Any],
    data_config: Dict[str, Any],
    log_dir: str,
    fp16: bool,
    device: torch.device,
    pretrained_model: str
) -> Tuple[float, float, float]:
    """Train."""
    
    # save model_config, data_config
    with open(os.path.join(log_dir, "data.yml"), "w") as f:
        yaml.dump(data_config, f, default_flow_style=False)
    with open(os.path.join(log_dir, "model.yml"), "w") as f:
        yaml.dump(model_config, f, default_flow_style=False)

    if pretrained_model is not None:
        print(f"pre-trained model {pretrained_model} used...")
        model = timm.create_model(pretrained_model, pretrained=True, num_classes=6)
    else:
        model_instance = Model(model_config, verbose=True)
        model = model_instance.model

    model_path = os.path.join(log_dir, "best.pt")
    print(f"Model save path: {model_path}")
    
    if os.path.isfile(model_path):
        model.load_state_dict(
            torch.load(model_path, map_location=device)
        )
        
    model.to(device)
    
    img_size = data_config["IMG_SIZE"]
    mean_time = check_runtime(
        model,
        [model_config["input_channel"]] + [img_size, img_size],
        device
    )
    params_nums = count_model_params(model)

    # Create dataloader
    train_dl, val_dl, test_dl = create_dataloader(data_config)

    # Create optimizer, scheduler, criterion
    optimizer = torch.optim.SGD(
        model.parameters(), lr=data_config["INIT_LR"], momentum=0.9
    )
    scheduler = torch.optim.lr_scheduler.OneCycleLR(
        optimizer=optimizer,
        max_lr=data_config["INIT_LR"],
        steps_per_epoch=len(train_dl),
        epochs=data_config["EPOCHS"],
        pct_start=0.05,
    )
    criterion = CustomCriterion(
        samples_per_cls=get_label_counts(data_config["DATA_PATH"])
        if data_config["DATASET"] == "TACO"
        else None,
        device=device,
    )
    # Amp loss scaler
    scaler = (
        torch.cuda.amp.GradScaler() if fp16 and device != torch.device("cpu") else None
    )

    # Create trainer
    trainer = TorchTrainer(
        model=model,
        criterion=criterion,
        optimizer=optimizer,
        scheduler=scheduler,
        scaler=scaler,
        device=device,
        model_path=model_path,
        verbose=1,
    )
    best_acc, best_f1 = trainer.train(
        train_dataloader=train_dl,
        n_epoch=data_config["EPOCHS"],
        val_dataloader=val_dl if val_dl else test_dl,
        mean_time=mean_time,
        params_nums=params_nums
    )

    # evaluate model with test set
    model.load_state_dict(torch.load(model_path))
    test_loss, test_f1, test_acc = trainer.test(
        model=model, test_dataloader=val_dl if val_dl else test_dl
    )

    return test_loss, test_f1, test_acc

def get_args():
    parser = argparse.ArgumentParser(description="Train model.")
    parser.add_argument(
        "--model",
        default="configs/model/mobilenetv3.yaml",
        type=str,
        help="model config",
    )
    parser.add_argument(
        "--data",
        default="configs/data/taco.yaml",
        type=str,
        help="data config"
    )
    parser.add_argument(
        "--pretrained",
        default="",
        type=str,
        help="timm pre-trained model's name"
    )
    parser.add_argument(
        "--wandb_entity",
        default="this-is-real",
        type=str,
        help="wandb entity"
    )
    parser.add_argument(
        "--wandb_project",
        default="model-optimization",
        type=str,
        help="wandb project name"
    )
    parser.add_argument(
        "--run_name",
        default="run",
        type=str,
        help="wandb run name"
    )
    args = parser.parse_args()
    return args

def get_log_dir():
    log_dir = os.environ.get("SM_MODEL_DIR", os.path.join("exp", 'latest'))

    if os.path.exists(log_dir):
        modified = datetime.fromtimestamp(os.path.getmtime(log_dir + '/best.pt'))
        new_log_dir = os.path.dirname(log_dir) + '/' + modified.strftime("%Y-%m-%d_%H-%M-%S")
        os.rename(log_dir, new_log_dir)

    os.makedirs(log_dir, exist_ok=True)

    return log_dir

def main():
    args = get_args()

    model_config = read_yaml(cfg=args.model)
    data_config = read_yaml(cfg=args.data)

    data_config["DATA_PATH"] = os.environ.get("SM_CHANNEL_TRAIN", data_config["DATA_PATH"])

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    log_dir = get_log_dir()
    
    wandb.login()
    wandb.init(
        project=args.wandb_project,
        entity=args.wandb_entity,
        name=args.run_name
    )
    
    wandb.config.update(args)

    test_loss, test_f1, test_acc = train(
        model_config=model_config,
        data_config=data_config,
        log_dir=log_dir,
        fp16=data_config["FP16"],
        device=device,
        pretrained_model=args.pretrained if args.pretrained != "" else None
    )
    print(f"Test | loss: {test_loss:.6f}, f1: {test_f1:.6f}, acc: {test_acc:.6f}")

if __name__ == "__main__":
    main()



