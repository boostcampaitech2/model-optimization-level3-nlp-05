# boostcamp AI Tech 2기 - 모델 최적화

# Environment

## 1. Docker
```bash
docker run -it --gpus all --ipc=host -v ${path_to_code}:/opt/ml/code -v ${path_to_dataset}:/opt/ml/data placidus36/pstage4_lightweight:v0.4 /bin/bash
```

## 2. Install dependencies
```
pip install -r requirements.txt
```

# Run

## 1. train

```bash
python train.py \
--model configs/model/mobilenetv3.yaml \
--data configs/data/taco.yaml
```

## 2. inference (submission.csv)

```bash
python inference.py \
--model_dir /opt/ml/model-optimization/exp/latest \
--weight_name best.pt \
--img_root /opt/ml/data/test 
```

- `timm`을 통해 pre-trained 모델을 사용하고 model_config를 사용하지 않았다면 `weight_name` argument에 `best.ts`를 입력해야 한다.

# aistage 제출

서버 저장 후 제출 시 `Hyperparameter Inference` 부분에 다음 argument를 추가한다.

```
--model_dir /opt/ml/model-optimization/exp/latest
```

`timm`을 통해 pre-trained 모델을 사용하고 model_config를 사용하지 않았다면 `Hyperparameter Inference` 부분에 다음 argument를 추가한다.

```
--weight_name best.ts
```

# Reference

Our basic structure is based on [Kindle](https://github.com/JeiKeiLim/kindle)(by [JeiKeiLim](https://github.com/JeiKeiLim))
