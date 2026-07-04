# Generative Pre-Training NLP Class Project - Assignment Summary

**Instructor:** Juan Rios  
**Course:** COMP 469 - Artificial Intelligence  
**Term:** Fall 2026  
**Week:** Week 8  
**Reference:** Radford et al., "Generative Pre-Training for Language Understanding", ACL 2018  
**Paper URL:** https://gluebenchmark.com/leaderboard

---

## Project Overview

This project guides students through implementing the Generative Pre-Training framework from the influential NLP paper. The approach combines:

1. **Unsupervised pre-training** on large unlabeled text corpora to learn language representations
2. **Task-specific fine-tuning** using traversal-style input transformations

**Expected Achievement:** State-of-the-Art performance on 9 of 12 benchmark tasks (see Table 2 in paper).

---

## Project Structure

```
GenerativePreTraining/
├── notebooks/
│   ├── 01_setup.ipynb           # Setup and environment configuration
│   ├── 02_unsupervised_pretrain.ipynb
│   ├── 03_task_transformations.ipynb
│   ├── 04_finetuning.ipynb       # Task-specific fine-tuning
│   ├── 05_benchmark_results.ipynb
│   └── 06_ablations.ipynb       # Ablation studies and results
├── src/
│   ├── books_corpus/             # BooksCorpus data and utilities
│   ├── transformer/              # Transformer implementation
│   └── tasks/                    # Task-specific implementations
├── requirements.txt
├── README.md
└── project_summary.md
```

---

## Key Implementation Tasks

### Task 1: Setup (15 mins)
- Install dependencies: torch, transformers, ftfy, spaCy
- Configure device (CPU or GPU)

### Task 2: Unsupervised Pre-Training (30 mins)
- Implement pre-training on BooksCorpus (7k+ books, 512 contiguous tokens)
- Train Transformer: 12 layers, 768d states, 3072d FFN
- Objective: Language modeling (Eq. 1)
- Hyperparameters: Adam (2.5e-4), warmup 0.2%, 100 epochs

### Task 3: Task-Specific Transformations (30 mins)
- Textual Entailment: [premise; $; hypothesis]
- Semantic Similarity: [s1; $; s2] and [s2; $; s1]
- QA: [context; question; $; answers]

### Task 4: Fine-Tuning (25 mins)
- Train on NLI, QA, similarity, and classification tasks
- Auxiliary LM objective: λ = 0.5
- Fine-tuning: 3 epochs, LR 6.25e-5, batch size 32

### Task 5: Benchmark Results (20 mins)
- Report scores on 12 benchmark tasks
- Target SOTA: 9/12 tasks achieved

---

## Expected Results

### Top Performances (SOTA)
| Task | Score | Baseline | Improvement |
|------|-------|----------|-------------|
| Story Cloze | 86.5 | 77.6 | +9.7% |
| QQP | 70.3 | 66.1 | +4.0% |
| QNLI | 81.4 | 75.7 | +7.2% |
| MNLI | 82.1 | 72.2 | +10.0% |
| SNLI | 89.9 | 88.5 | +1.5% |
| RACE | 57.4 | 55.6 | +2.9% |
| SST-2 | 91.3 | 90.2 | - |

### Ablation Insights (Table 5)
- Pre-training provides ~15% improvement on Transformer models
- Transformer architecture outperforms LSTM by 5.6 points
- Auxiliary LM helps on NLI/QQP but benefit diminishes on smaller tasks

---

## Submission Requirements

### Required Files
- Working `/home/jrios/Documents/Github/Comp_469/openclaw/Labs/GenerativePreTraining/`
- `requirements.txt`
- `README.md`
- `notebooks/01_setup.ipynb`
- `notebooks/02_unsupervised_pretrain.ipynb`
- `notebooks/03_task_transformations.ipynb`
- `notebooks/04_finetuning.ipynb`
- `notebooks/05_benchmark_results.ipynb`
- `notebooks/06_ablations.ipynb`
- `src/` folder with all source files

### Presentation (5 minutes)
- Brief overview of methodology
- Key results on each benchmark task
- Interpretation of ablations
- Comparison with existing SOTA

### Grading Rubric
| Criteria | Score |
|----------|---|
| Correct implementation of Eq. 1-5 | 25% |
| Code working and tested | 20% |
| 9/12 tasks achieve SOTA | 25% |
| Ablation analysis (Table 5) | 15% |
| Presentation (5 mins) | 15% |

---

## Next Steps After Assignment

1. **Evaluate Results:**
   - Compare with baseline models (Table 2: ESIM + ELMo, CAFE, BiLSTM)
   - Analyze why RTE performs below baseline (smaller dataset)
   - Evaluate Story Cloze: 86.5 vs 77.6 baseline (+9.7%)

2. **Extend Research:**
   - Try different transformer architectures
   - Explore zero-shot behavior
   - Investigate zero-shot on RTE

3. **Teaching Extension:**
   - Use this project as hands-on lab
   - Compare with supervised fine-tuning baselines
   - Discuss transfer learning concepts

---

## Support Resources

### Documentation
- Paper: https://gluebenchmark.com/leaderboard
- AIMA Python Course: https://github.com/aimacode/aima-python
- Géron Hands-On ML Notebooks: https://github.com/ageron/handson-ml3

### Key Papers
1. Radford et al. "Generative Pre-Training for Language Understanding" (ACL 2018)
2. Vaswani et al. "Attention is All You Need" (ACL 2017)
3. Brown et al. "Language Models are Few-Shot Learners" (ICML 2020)

### Instructor
Questions: [email address to add]

---

## Timeline Summary

| Day | Task | Duration |
|-----|------|----------|
| Tue | Setup & Dependencies | 15 mins |
| Wed | Pre-training | 30 mins |
| Thu | Transformations & Fine-tuning | 55 mins |
| Fri | Results & Ablations | 20 mins |
| Total | | ~120 mins |

---

**Last updated:** 2026-07-03

**For questions about the assignment, see: [INSERT CONTACT INFORMATION]**
