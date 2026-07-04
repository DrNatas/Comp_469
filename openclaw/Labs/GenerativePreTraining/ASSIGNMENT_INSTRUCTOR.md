# Generative Pre-Training NLP - Class Assignment
## COMP 469 - Fall 2026

---

## Assignment Overview

This assignment guides students through implementing the **Generative Pre-Training** framework from the influential NLP paper:

> **Paper:** Radford, Alec, et al. "Generative Pre-Training for Language Understanding."  
> **Publication:** ACL 2018  
> **URL:** https://gluebenchmark.com/leaderboard

### Project Goal
Implement a two-stage training pipeline that achieves **State-of-the-Art** performance on 9 of 12 benchmark NLP tasks.

---

## Expected Results (SOTA from Paper)

| Task | Score | Improvement over Baseline |
|------|-------|---------------------------|
| Story Cloze | 86.5 | +9.7% |
| QQP | 70.3 | +4.0% |
| QNLI | 81.4 | +7.2% |
| MNLI | 82.1 | +10.0% |
| SNLI | 89.9 | +1.5% |
| RACE | 57.4 | +2.9% |
| SST-2 | 91.3 | 0% |
| MRPC | 82.3 | +1.1% |

---

## Project Structure

```
GenerativePreTraining/
├── notebooks/             # 6 Jupyter notebooks for students
│   ├── 01_setup.ipynb     # Setup and environment
│   ├── 02_unsupervised_pretrain.ipynb
│   ├── 03_task_transformations.ipynb
│   ├── 04_finetuning.ipynb
│   ├── 05_benchmark_results.ipynb
│   └── 06_ablations.ipynb
├── src/                   # Source code
│   ├── books_corpus/
│   ├── transformer/
│   └── tasks/
├── notebooks/
├── README.md              # Full assignment details
├── QUICK_REFERENCE.md     # Key formulas
├── project_summary.md     # Quick reference
├── ASSIGNMENT_CHECKLIST.md
├── .gitignore
└── requirements.txt
```

---

## Assignment Objectives

### 1. Implement Unsupervised Pre-Training
- Train a Transformer on BooksCorpus (7k+ books, 512 contiguous tokens)
- Use language modeling objective (Eq. 1)
- Achieve low perplexity (~18.4)

### 2. Implement Task-Specific Transformations
- Textual Entailment: `[premise; $; hypothesis]`
- Semantic Similarity: `[s1; $; s2]` and `[s2; $; s1]`
- Question Answering: `[context; question; $; answers]`

### 3. Perform Fine-Tuning
- Train on NLI, QA, similarity, and classification tasks
- Use auxiliary LM objective (Eq. 5) with λ = 0.5

### 4. Achieve SOTA Results
- Target 9/12 tasks in Table 4 of paper
- Compare with baseline models (ESIM + ELMo, CAFE, etc.)

---

## Key Concepts

### Pre-Training Objective (Eq. 1)
```
L1(U) = Σ log P(ui | ui−k, ..., ui−1; Θ)
```

### Fine-Tuning Objective (Eq. 5)
```
L3(C) = L2(C) + λ * L1(C)
λ = 0.5
```

### Input Transformations
All task inputs are converted to sequence format compatible with the Transformer:
- **Textual Entailment**: concatenate [premise, $, hypothesis]
- **Similarity**: concatenate [s1, $, s2] and [s2, $, s1] then average
- **QA**: concatenate [context, question, $, answers]

---

## Hyperparameters (from Paper)

| Parameter | Value |
|-----------|-------|
| Learning Rate | 6.25e-5 |
| Epochs | 3 |
| Batch Size | 32 |
| Auxiliary Weight (λ) | 0.5 |
| Dropout Rate | 0.1 |
| Warmup % | 0.2% of training steps |
| Gradient Clipping | 5.0 |

---

## Notebook Contents

### 01_setup.ipynb
- Install dependencies: torch, transformers, ftfy, spaCy
- Define vocabulary and embeddings
- Create attention mechanism

### 02_unsupervised_pretrain.ipynb
- Load BooksCorpus dataset
- Implement pre-training training loop
- Evaluate perplexity

### 03_task_transformations.ipynb
- Create traversal-style input transformations
- Test on NLI, QA, and similarity tasks

### 04_finetuning.ipynb
- Implement fine-tuning for NLI
- Implement fine-tuning for QA
- Implement fine-tuning for classification

### 05_benchmark_results.ipynb
- Report results on all 12 tasks
- Compare with baseline models
- Discuss ablations (Table 5)

### 06_ablations.ipynb
- Ablation studies (Table 5)
- Explain why Transformer works better than LSTM
- Discuss auxiliary LM benefits

---

## Submission Requirements

### Files Required
- `requirements.txt`
- `README.md`
- `QUICK_REFERENCE.md`
- `project_summary.md`
- `notebooks/01_setup.ipynb`
- `notebooks/02_unsupervised_pretrain.ipynb`
- `notebooks/03_task_transformations.ipynb`
- `notebooks/04_finetuning.ipynb`
- `notebooks/05_benchmark_results.ipynb`
- `notebooks/06_ablations.ipynb`
- `src/books_corpus/`
- `src/transformer/`
- `src/tasks/`
- `src/__init__.py`

### Presentation (5 minutes)
- Brief overview of methodology
- Key results on each benchmark task
- Interpretation of ablation analysis
- Comparison with existing SOTA

---

## Grading Rubric

| Criteria | Score |
|----------|-----|
| Correct implementation of Eq. 1-5 | 25% |
| Code working and tested | 20% |
| 9/12 tasks achieve SOTA | 25% |
| Ablation analysis (Table 5) | 15% |
| Presentation (5 mins) | 15% |

---

## Instructor Support

**Instructor:** Juan Rios  
**Course:** COMP 469 - Artificial Intelligence  
**Contact:** [insert email]

**Documentation:**
- Paper: https://gluebenchmark.com/leaderboard
- AIMA Course: https://github.com/aimacode/aima-python
- Géron ML Notebooks: https://github.com/ageron/handson-ml3

---

## Next Steps

1. **Run Pre-training** on BooksCorpus to achieve low perplexity
2. **Implement** task-specific transformations
3. **Train** on all 12 tasks and report results
4. **Achieve** SOTA on 9/12 tasks
5. **Create** presentation for classroom
6. **Address** RTE underperformance (why? - small dataset)

---

## Timeline

| Day | Task | Duration |
|-----|-----|-----|
| Tue | Setup & Dependencies | 15 mins |
| Wed | Pre-training | 30 mins |
| Thu | Transformations & Fine-tuning | 55 mins |
| Fri | Results & Ablations | 20 mins |
| Total | | ~120 mins |

---

**For questions about the assignment, contact the instructor.**

---

*This assignment is designed to teach transfer learning concepts through a concrete, hands-on implementation.*
