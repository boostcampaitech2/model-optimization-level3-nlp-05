# boostcamp AI Tech 2기 - 모델 최적화

## Environment

### 1. Docker
```bash
docker run -it --gpus all --ipc=host -v ${path_to_code}:/opt/ml/code -v ${path_to_dataset}:/opt/ml/data placidus36/pstage4_lightweight:v0.4 /bin/bash
```

<br>

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

<br>

## Baseline
```bash
.
├── configs
│   ├── data                # data 관련 yaml 파일
│   └── model               # parsing 전 모델 yaml 파일
│   │   ├── example.yaml
│   │   └── mobilenetv3.yaml
│   │   └── effnetb0.yaml
├── inference.py
├── src
│   ├── init.py
│   ├── dataloader.py
│   ├── loss.py
│   ├── model.py
│   ├── trainer.py
│   ├── augmentation
│   ├── modules             # parsing 을 위한 모델 아키텍쳐 모듈들
│   └── utils
├── tests
│   └── test_model_parser.py
│   └── test_model_conversion.py
└── train.py
```


## Run

### 1. train

```bash
python train.py \
--model \
--data \
--pretrained \
--wandb_entity \
--wandb_project \
--run_name \
```

- `--model`
  - model config yaml 파일 경로
  - default: `configs/model/mobilenetv3.yaml`
- `--data`
  - data config yaml 파일 경로
  - default: `configs/data/taco.yaml`
- `--pretrained`
  - `timm`을 통해 불러올 pre-trained 모델명
  - 해당 argument 지정 시 `model_config`를 사용하지 않고 pre-trained 모델을 불러와서 학습 실시
  - ex) `mobilenetv3_large_100`
  - default: `""`
- `--wandb_entity`
  - wandb entity 이름
  - default: `this-is-real`
- `--wandb_project`
  - wandb project 이름
  - default: `model-optimization`
- `--run_name`
  - wandb run 이름
  - default: `run`

<br>

### 2. inference (submission.csv)

```bash
python inference.py \
--dst \
--model_dir \
--weight_name \
--img_root \
```

- `--dst`
  - submmision.csv 파일 저장 경로
  - default: `os.environ.get("SM_OUTPUT_DATA_DIR")` (서버 제출 시 사용됨)
- `--model_dir`
  - 모델 checkpoint가 저장된 경로
  - 해당 프로젝트에서 inference를 진행하기 위해선 `/opt/ml/model-optimization/exp/latest` 지정
  - default: `/opt/ml/code/exp/latest`
- `--weight_name`
  - 모델 가중치 파일명
  - ex) `best.pt`, `best.ts`
  - pre-trained 모델로 학습했을 경우 `best.ts` 지정
  - default: `best.pt`
- `--img_root`
  - 테스트 이미지 데이터셋 경로
  - default: `/opt/ml/data/test`

<br>

## aistage 제출

서버 저장 후 제출 시 `Hyperparameter Inference` 부분에 다음 argument를 추가한다.

```
--model_dir /opt/ml/model-optimization/exp/latest
```

`timm`을 통해 pre-trained 모델을 사용하고 model_config를 사용하지 않았다면 `Hyperparameter Inference` 부분에 다음 argument를 추가한다.

```
--weight_name best.ts
```

<br>

## Reference

Our basic structure is based on [Kindle](https://github.com/JeiKeiLim/kindle)(by [JeiKeiLim](https://github.com/JeiKeiLim))
