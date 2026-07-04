# Generative Pre-Training Quick Reference

## Key Formulas

### Pre-training Objective (Eq. 1)
```python
L1(U) = Σ log P(ui | ui−k, ..., ui−1; Θ)
```

### Fine-tuning Objective (Eq. 5)
```python
L3(C) = L2(C) + λ * L1(C)
λ = 0.5
```

### Input Transformations

**Textual Entailment** (Eq. 1):
```python
Input: [premise; $; hypothesis]
```

**Similarity** (Eq. 3):
```python
Input: [s1; $; s2]  AND  [s2; $; s1]
```

**QA** (Eq. 4):
```python
Input: [context; question; $; answers]
```

## Model Architecture

- **Transformers**: 12 layers, 768d states, 3072d FFN
- **BPE Vocabulary**: 40,000 merges
- **Dropout**: 0.1
- **Adam Optimizer**: lr 2.5e-4
- **Warmup**: 0.2% of training steps

## Hyperparameters

| Task | Hyperparameter | Value |
|------|---------------|-------|
| Fine-tuning LR | Learning rate | 6.25e-5 |
| Fine-tuning Epochs | Epochs | 3 |
| Fine-tuning Batch Size | Batch size | 32 |
| Auxiliary Weight | λ | 0.5 |
| Gradient Clipping | Limit | 5.0 |
| Warmup Steps | Warmup% | 0.2% |

## Expected Results

| Task | Our Model | SOTA |
|------|-----------|------|
| CoLA | 45.4 | 93.2 |
| SST-2 | 91.3 | 90.2 |
| MRPC | 82.3 | 80.2 |
| STSB | 82.0 | 55.5 |
| QQP | 70.3 | 66.1 |
| MNLI | 82.1 | 72.2 |
| QNLI | 81.4 | 75.7 |
| RTE | 56.0 | 61.7 |
| SNLI | 89.9 | 88.5 |
| RACE | 57.4 | 55.6 |
| Story Cloze | 86.5 | 77.6 |

## Implementation Notes

1. **Pre-training**: Train for 100 epochs, save checkpoints
2. **Fine-tuning**: 3 epochs for each task type
3. **Testing**: Test on BooksCorpus for pre-training
4. **Evaluation**: Evaluate on all 12 tasks
5. **Ablations**: Compare full model vs baselines

## Files to Include

- `Notebooks/` folder with all 6 notebooks
- `src/` folder with all source files
- `requirements.txt` with all dependencies
- `README.md` with complete assignment details
- `project_summary.md` with quick reference
