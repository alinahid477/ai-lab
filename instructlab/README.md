

https://developers.redhat.com/blog/2024/06/12/getting-started-instructlab-generative-ai-model-tuning

https://raw.githubusercontent.com/cedricclyburn/vegas-taxonomy/main/knowledge/trivia/vegas/qna.yaml

https://github.com/cedricclyburn/las-vegas-gambling-knowledge/blob/main/biggest_vegas_jackpots.md

https://github.com/instructlab/instructlab?tab=readme-ov-file#-creating-new-knowledge-or-skills-and-training-the-model




```
cd /workspace/ai-lab/instructlab
```

CPU based install
```
pip cache remove llama_cpp_python
pip install instructlab

```

Clone the taxonomy. I dont know yet whether this is requirement for synthetic data generate or tune. 
```
git clone https://github.com/instructlab/taxonomy.git
```


```
ilab --version

```

initialize instructlab.
```
ilab config init
```

test serving a local model
```
ilab model chat --model /workspaces/ai-lab/training/models/ibm-granite/quantized/granite-3.3-2b-instruct-Q4_K_M.gguf
```

prepare taxonomy => training/instructlab/qna.yaml, additional documents:training/instructlab/intellilogs-commands-variations.md 
```
mkdir -p /workspace/ai-lab/instructlab/taxonomy/knowledge/extraction/intellilogs/
cp ../training/instructlab/qna.yaml /workspace/ai-lab/instructlab/taxonomy/knowledge/extraction/intellilogs/qna.yaml
```

Download granite-7b. ***must be 7b. 2b does not work. throws errors like tokenization model not found.***
```
ilab model download --repository instructlab/granite-7b-lab-GGUF --filename granite-7b-lab-Q4_K_M.gguf --hf-token <hf token>
```
Generate synthetic data ***on cpu using granite-7b this process took 12 hours***
```
ilab data generate --model /home/dev/.cache/instructlab/models/granite-7b-lab-Q4_K_M.gguf   --taxonomy-path /workspaces/ai-lab/instructlab/taxonomy --output-dir /workspaces/ai-lab/instructlab/outputs/datasets

OR

ilab data generate --model /home/dev/.cache/instructlab/models/granite-7b-lab-Q4_K_M.gguf --endpoint-url https://granite-3-1-8b-instruct-w4a16-maas-apicast-production.apps.prod.rhoai.rh-aiservices-bu.com:443/v1 --api-key ffaf3a383cf51ca345f7b5132b2c1f8f --taxonomy-path /workspaces/ai-lab/instructlab/taxonomy --output-dir /workspaces/ai-lab/instructlab/outputs/datasets --num-cpus 14
```

