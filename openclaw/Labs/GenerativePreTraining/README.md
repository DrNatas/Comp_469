# Generative Pre-Training for NLP - Class Project Assignment

**Course:** COMP 469 - Artificial Intelligence / Neural Networks  
**Instructor:** Juan Rios (CSU Channel Islands)  
**Term:** Fall 2026  
**Reference:** Radford et al. "Generative Pre-Training for Language Understanding", ACL 2018  
**Paper URL:** https://gluebenchmark.com/leaderboard

---

## Overview

This project implements the two-stage training framework from the Generative Pre-Training paper:
1. **Unsupervised pre-training**: Train a Transformer on BooksCorpus to learn language representations
2. **Task-specific fine-tuning**: Adapt the pre-trained model to 12 NLP tasks using task-aware input transformations

**Expected Outcome:** Achieve State-of-the-Art (SOTA) results on 9/12 benchmark tasks, surpassing existing models by 5-9%.

---

## Assignment Objectives

- Implement the two-stage training procedure from Radford's paper
- Build task-specific input transformations (traversal-style approach)
- Train and benchmark the model on 12 NLP tasks
- Achieve SOTA performance on 9/12 tasks
- Document methodology, ablations, and results

---

## Project Structure

```
GenerativePreTraining/
├── notebooks/
│   ├── 01_setup.ipynb           # Setup and environment
│   ├── 02_unsupervised_pretrain.ipynb
│   ├── 03_task_transformations.ipynb
│   ├── 04_finetuning.ipynb       # Fine-tuning on tasks
│   ├── 05_benchmark_results.ipynb
│   └── 06_ablations.ipynb
├── src/
│   ├── books_corpus/             # BooksCorpus data
│   ├── transformer/              # Model implementation
│   ├── tasks/                    # Task-specific implementations
│   └── utils/                    # Utilities
├── requirements.txt
└── README.md
```

---

## Week 8 Timeline

### Tuesday
- **Setup**: Install dependencies (Python 3.10+, PyTorch, Transformers, FTFY, spaCy)
- **Task 1**: Project Setup and Dependencies (15 mins)
- **Task 2**: Implementation - Unsupervised Pre-Training (25 mins)

### Wednesday
- **Task 3**: Implementation - Task-Specific Input Transformations (25 mins)
- **Task 4**: Implementation - Task Fine-Tuning (15 mins)
- **Task 5**: Implementation - Results and Ablations (20 mins)

### Thursday
- Final submission review and presentation

---

## Key Concepts

### 1. Unsupervised Pre-Training

The pre-training stage uses a language modeling objective to learn representations from unstructured text:

```python
L1(U) = Σ log P(ui | ui−k, ..., ui−1; Θ)
```

**Model Architecture** (from Eq. 2 in paper):
- Transformer with 12 layers
- 768d hidden states with 12 attention heads
- 3072d FFN (inner states)
- Position embeddings (learned, not sinusoidal)
- BPE vocabulary: 40k merges

### 2. Task-Specific Input Transformations

Transformations are designed to map diverse task structures into sequence format for the Transformer:

#### Textual Entailment (Eq. 1)
```
Input: [premise; $; hypothesis]
Output: Transformer([premise, $, hypothesis])
```

#### Similarity (Eq. 3)
```
Input: [sentence1; $; sentence2]  AND  [sentence2; $; sentence1]
Output: [h1; h2; h1; h2] averaged element-wise
```

#### Question Answering (Eq. 4)
```
Input: [context; question; $; answer1, answer2, ...]
Output: [z; q; $; ak] for each answer
```

### 3. Fine-Tuning Objectives

**Supervised Loss** (Eq. 4):
```
L2(C) = Σ log P(y|x1,...,xm)
```

**Auxiliary Language Modeling Loss** (Eq. 5):
```
L3(C) = L2(C) + λ * L1(C)
λ = 0.5
```

**Fine-tuning Hyperparameters** (Section 4.2):
- LR: 6.25e-5
- Batch size: 32
- Epochs: 3
- Auxiliary weight λ: 0.5
- Dropout: 0.1

---

## Tasks and Deliverables

### Task 1: Project Setup (15 mins)
**Deliverable**: Working environment with all dependencies

**Commands**:
```bash
conda create -n npy python=3.10
conda activate npy
pip install torch transformers ftfy spaCy
```

### Task 2: Unsupervised Pre-Training (30 mins)
**Deliverable**: Full pre-training implementation

**Files to create**:
- `src/books_corpus/train_bookcorpus.py`
- `src/books_corpus/clean_bookcorpus.py`
- `src/books_corpus/transformer.py`

**Key functions**:
- `load_books_corpus()`: Load and clean BooksCorpus
- `train_language_model()`: Implement Eq. 1 with Transformer
- `evaluate_model()`: Calculate perplexity on BooksCorpus

### Task 3: Task-Specific Transformations (30 mins)
**Deliverable**: Implement Eq. 2, 3, 5 for all tasks

**Tasks to implement**:
- Textual Entailment transformation
- Similarity transformation (both orders)
- QA transformation

**Key functions**:
- `create_textual_entailment_input(premise, hypothesis)`
- `create_similarity_input(sentence1, sentence2)`
- `create_qa_input(context, question, answers)`

### Task 4: Fine-Tuning (25 mins)
**Deliverable**: Fine-tuning implementation with task transformations

**Key changes from baseline**:
- Add task-specific input transformers before the pre-trained model
- Use Eq. 5 (L2 + λ*L1) instead of Eq. 4

**Key functions**:
- `prepare_input_for_task(task, data)`
- `fine_tune_model(task, data, optimizer, scheduler)`
- Save checkpoints for each task

### Task 5: Benchmark and Ablations (20 mins)
**Deliverable**: Results notebook with 9/12 SOTA

**Metrics to report** (Table 1, 2, 3, 4, 5 in paper):

**Benchmarks to achieve** (SOTA scores in table 4):
- CoLA: 45.4 (93.2 vs 91.3)
- SST-2: 91.3 (90.2 vs 91.3)
- MRPC: 82.3 (80.2 vs 82.3)
- STSB: 82.0 (55.5 vs 82.0)
- QQP: 70.3 (66.1 vs 70.3)
- MNLI: 82.1 (72.2 vs 82.1)
- QNLI: 81.4 (75.7 vs 81.4)
- RTE: 56.0 (61.7 vs 56.0 - *below SOTA*)
- SNLI: 89.9 (88.5 vs 89.9)
- RACE: 57.4 (55.6 vs 57.4)
- Story Cloze: 86.5 (77.6 vs 86.5)

---

## Expected Results

**Table 5 Ablation Analysis**:
| Method | Avg Score | CoLA | SST-2 | MRPC | STSB | QQP |
|--------|-----------|------|-------|------|------|-----|
| Transformer w/ aux LM (full) | 74.7 | 45.4 | 91.3 | 82.3 | 82.0 | 70.3 |
| Transformer w/o pre-training | 59.9 | 18.9 | 84.0 | 79.4 | 30.9 | 65.5 |
| Transformer w/o aux LM | 75.0 | 47.9 | 92.0 | 84.9 | 83.2 | 69.8 |
| LSTM w/ aux LM | 69.1 | 30.3 | 90.5 | 83.2 | 71.8 | 68.1 |

**Expected performance**:
- On MRPC: +1.9% (80.2 → 82.3)
- On SST-2: +0.8% (90.2 → 91.3)
- On CoLA: +0.4% (86.0 → 91.3)
- On QQP: +4.0% (66.1 → 70.3)
- On MRPC + SST-2: Combined +2.6% improvement

---

## Submission Guidelines

**Required files**:
1. `/home/jrios/Documents/Github/Comp_469/openclaw/Labs/GenerativePreTraining/`
   - `requirements.txt`
   - `README.md`
   - `Notebook/` folder with all 6 notebooks
   - `src/` folder with all source files

2. **Presentation** (5 minutes):
   - Brief overview of methodology
   - Key results on each benchmark task
   - Ablation analysis interpretation
   - Comparison with existing SOTA

**Grading Rubric**:
| Criteria | Score |
|----------|-------|
| Correct implementation of Eq. 1-5 | 25% |
| Code working and tested | 20% |
| 9/12 tasks achieve SOTA | 25% |
| Ablation analysis (Table 5) | 15% |
| Presentation (5 mins) | 15% |

---

## References

1. Radford, Alec, et al. "Generative Pre-Training for Language Understanding." arXiv preprint arXiv:1803.05457, 2018.

2. Vaswani, A., et al. "Attention is All You Need." arXiv preprint arXiv:1706.03762, 2017.

3. Brown, T., et al. "Language Models are Few-Shot Learners." ICML 2020.

---

## Instructor Support

Questions or issues:
- Check `requirements.txt` for dependencies
- If encountering errors, share error messages with instructor
- For implementation questions, see the notebook cells for guidance

---

**Last updated**: 2026-07-03

**For more information about this course and project, visit:**
- [COMP 469 Course Syllabus](https://csuci.edu/comp-469)
- [AIMA Python Course Resources](https://github.com/aimacode/aima-python)
