# inference 대상이 latest인지, 날짜 dir인지 확인하기
# pre-trained 모델로 학습했을 경우 best.ts 지정

python inference.py \
    --model_dir /opt/ml/model-optimization/exp/latest \
    --weight_name best.ts
