# 🧠 Ensemble-Based LLM Verification for Biomedical Citation Accuracy

## 📌 Research Question

**How effective is ensemble-based LLM verification in detecting citation errors (existence and relevance) in biomedical literature compared to individual LLM assessments and human expert validation?**

---

## 🤔 What Does "Ensemble-Based" Mean?

**Ensemble-based** methods combine multiple models or algorithms to make predictions, rather than relying on just one.  
Think of it like consulting a group of experts instead of a single one.

---

## ⚙️ How Ensemble Methods Work

### ✅ Basic Concept:
- Use multiple LLMs instead of one for verifying citations.
- Each model gives its own judgment.
- Predictions are combined to reach a consensus.
- Performance improves as more models are added.

### 🛠️ Common Techniques:

#### 1. Voting:
- Each model “votes” on citation correctness.
- Majority wins.
- _Example_: If 3 out of 5 LLMs say it’s accurate → **Marked Accurate**

#### 2. Weighted Combination:
- Assign weights based on model performance.
- Better models influence the final decision more.

#### 3. Stacking:
- A **meta-model** is trained to learn the best way to combine base model outputs.

---

## 🚀 Why Ensemble Methods Are Better

To address the variance in LLM-generated answers, we:
- Average over multiple **prompts**
- Combine **different models**

**Benefits**:
- 🔍 **Reduced Errors** – More consensus = higher reliability  
- 🧠 **Better Coverage** – Different models catch different error types  
- ✅ **Higher Confidence** – Agreement increases trust

---

## 🧪 Practical Example in Citation Verification

- Instead of using just GPT-4, use an ensemble: **GPT-4 + Claude + Gemini + Mixtral**
- Each model evaluates citation independently.
- Combine decisions:
  - e.g., If 2/3 say “inaccurate”, flag the citation.
- Use varied prompts per model for diverse perspectives.

---

## 📊 Key Findings

### 📈 1. Individual LLM Performance:
- **Best Performing Individual Model**:
  - Micro-F1: 0.59, Macro-F1: 0.52  
  - GPT-4: Better at detecting accurate citations, weaker for erroneous ones  
  - **Micro-F1**: 0.65, **Macro-F1**: 0.45  
  - > *50-90% of LLM responses are not fully supported by cited sources*  
  - > GPT-4o: ~30% of statements unsupported  
  - 🔗 [Oxford Academic Bioinformatics](https://academic.oup.com/bioinformatics)  
  - 🔗 [Nature PubMed Central](https://www.nature.com/)

### 🧠 2. Ensemble Improves Performance:
- Performance scales with the number of models in the ensemble  
- Ensembles outperform individual models in error detection

### 👨‍⚕️ 3. Agreement with Human Experts:
- Claude 3.5 Sonnet: **87.0%** agreement with expert consensus  
- GPT-4o: **88.7%** agreement (p = 0.52)  
- Source Verifier: **95.8%** agreement with doctors  
- 🔗 [PMC Reference](https://pubmed.ncbi.nlm.nih.gov/)  
- 🔗 [arXiv:2502.21014](https://arxiv.org/abs/2502.21014)

---

## 📉 Citation Error Rates in Biomedical Literature

- 3063 citation instances analyzed  
- **39.18%** contained accuracy errors  
- 🔗 [Oxford Academic](https://academic.oup.com/)  

---

## ✅ Advantages of Ensemble Approaches

| Benefit             | Description                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| 🎯 Reduced Variance | Lowers inconsistency in predictions across models                           |
| 🧪 Better Detection | Matches or outperforms traditional annotation techniques                    |
| 📈 Improved Reliability | Catches edge cases missed by single models                              |

---

## ⚠️ Challenges & Limitations

- **Citation Accuracy Issues**:
  - LLMs often fail to provide *all* valid references.
  - Sometimes cite unrelated or contradictory sources.

- **Weakness in Error Detection**:
  - GPT-4 struggles with **NOT_ACCURATE** classification.
  - Despite good accuracy detection, poor at flagging wrong citations.
  - 🔗 [arXiv:2305.14627](https://arxiv.org/abs/2305.14627)  
  - 🔗 [PromptLayer Benchmark](https://www.promptlayer.com/)

---

## 🩺 Practical Applications

In real-world biomedical citation screening:
- **Sensitivity**: 0.75 → improved to 0.91 with prompt tuning  
- **Specificity**: 0.99 (very high)  
- 🔗 [arXiv:2410.18889](https://arxiv.org/abs/2410.18889)

---

## 🧾 Conclusion

Ensemble-based LLM verification demonstrates:
- 🧠 **Improved citation error detection** in biomedical papers
- ✅ **Higher expert agreement** (87–95%)
- 📉 **Lower variance** than single-model approaches

**However**, more work is needed to:
- Address weaknesses in detecting **inaccurate citations**
- Lower the baseline biomedical error rate (~39%)

---

## 📚 References

- [Guide to Ensemble Learning (Analytics Vidhya)](https://www.analyticsvidhya.com/blog/2021/06/ensemble-learning/)
- [Bioinformatics | Oxford Academic](https://academic.oup.com/bioinformatics)
- [Nature | PubMed Central](https://www.nature.com/)
- [arXiv:2502.21014](https://arxiv.org/abs/2502.21014)
- [arXiv:2305.14627](https://arxiv.org/abs/2305.14627)
- [arXiv:2410.18889](https://arxiv.org/abs/2410.18889)

---

## 🔬 Future Work

- Incorporate prompt engineering and meta-learning techniques
- Build open-source tools for citation verification
- Extend beyond biomedical literature to legal, scientific, and educational domains

---

> 🧪 _This README serves as a documentation draft for evaluating ensemble-based LLMs for citation verification research._
