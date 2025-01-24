uv run mlx_lm.lora \
    --model "Qwen/Qwen2.5-3B" \
    --train \
    --data "./dataset/coldstart" \
    --learning-rate 1e-5 \
    --iters 100 \
    --fine-tune-type full


uv run -m mlx_lm.generate \
  --model "Qwen/Qwen2.5-3B" \
  --max-tokens 500 \
  --adapter-path adapters \
  --prompt '{"role":"user","content":"Hello, how are you?"}'


  <|endoftext|>


A conversation between User and Assistant. The user asks a question, and the Assistant solves it. The assistant first thinks about the reasoning process in the mind and then provides the user with the answer. The reasoning process and answer are enclosed within <think> </think> and <answer> </answer> tags, respectively, i.e., <think> reasoning process here </think>
<answer> answer here </answer>.<|im_start|>user\nwhat is larger a horse or a cow?<|im_end|>\n<|im_start|>assistant\n