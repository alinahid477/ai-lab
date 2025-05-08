

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

Generate synthetic data
```
ilab data generate --model /home/dev/.cache/instructlab/models/granite-7b-lab-Q4_K_M.gguf   --taxonomy-path /workspaces/ai-lab/instructlab/taxonomy --output-dir /workspaces/ai-lab/instructlab/outputs/datasets --pipeline simple
```

