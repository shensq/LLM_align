autotrain llm \
--train \
--model 'meta-llama/Llama-2-7b-hf' \
--project-name 'llama2-7b' \
--data-path data/ \
--text-column text \
--lr 2e-4 \
--batch-size 8 \
--epochs 10 \
--warmup-ratio 0.1 \
--lora-r 16 \
--lora-alpha 32 \
--lora-dropout 0.05 \
--weight-decay 0.01 \
--fp16 \
--use-peft \
--use-int4 \
--logging_steps 10 \
--valid_split "valid"

# --block-size 128 \
# $( [[ "$USE_FP16" == "True" ]] && echo "--fp16" ) \
# $( [[ "$USE_PEFT" == "True" ]] && echo "--use-peft" ) \
# $( [[ "$USE_INT4" == "True" ]] && echo "--use-int4" ) \
# $( [[ "$PUSH_TO_HUB" == "True" ]] && echo "--push-to-hub --token ${HF_TOKEN} --repo-id ${REPO_ID}" )