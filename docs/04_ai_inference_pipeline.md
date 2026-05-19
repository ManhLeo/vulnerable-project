# AI Inference Pipeline
## Purpose
The AI inference pipeline is responsible for:
- preprocessing source code
- tokenizing input
- running AI inference
- generating vulnerability predictions
- returning structured results
---
# Current AI Model
## Model
CodeBERT
## Frameworks
- PyTorch
- HuggingFace Transformers
---
# AI Task
Binary classification:
- vulnerable
- non-vulnerable
---
# Supported Languages
- C
- C++
- Python
- Java
---
# Pipeline Flow
Source Code
↓
Preprocessing
↓
Tokenization
↓
CodeBERT Inference
↓
Probability Score
↓
Threshold Decision
↓
Prediction Result
---
# Input Format
Example:
```c
char buf[10];
strcpy(buf, input);
```
---
# Preprocessing
## Responsibilities
- remove comments
- normalize whitespace
- sanitize input
- remove empty lines
---
# Tokenization
## Tokenizer
```text
microsoft/codebert-base
```
## Responsibilities
- convert source code into tokens
- apply padding and truncation
- prepare tensors for inference
---
# Inference Stage
## Responsibilities
- load trained model
- run forward pass
- calculate probabilities
- generate predictions
---
# Prediction Logic
## Classes
| Class | Meaning |
|---|---|
| 0 | Non-vulnerable |
| 1 | Vulnerable |
## Threshold
```text
0.88
```
## Rule
```python
if probability >= threshold:
    vulnerable
else:
    non-vulnerable
```
---
# Example Output
```json
{
  "is_vulnerable": true,
  "confidence": 0.91
}
```
---
# Extended Backend Output
The backend may enrich AI results with:
- suspicious patterns
- risk levels
- heuristic analysis
Example:
```json
{
  "is_vulnerable": true,
  "confidence": 0.91,
  "risk_level": "HIGH",
  "suspicious_patterns": [
    {
      "pattern": "strcpy",
      "issue": "Potential buffer overflow"
    }
  ]
}
```
---
# Model Loading Rules
## Required
- load model once at startup
- use singleton model instance
- keep model in memory
## Forbidden
- loading model per request
- retraining during runtime
- modifying model weights
---
# GPU Support
If CUDA is available:
- use GPU inference
Otherwise:
- fallback to CPU
---
# Performance Requirements
| Metric | Target |
|---|---|
| Inference Time | < 1 second |
| API Response Time | < 2 seconds |
| Max Input Length | 512 tokens |
---
# Error Handling
The inference layer must handle:
- invalid input
- empty source code
- tokenizer failures
- inference failures
---
# Security Rules
The AI pipeline must NEVER:
- execute uploaded code
- compile source code
- run shell commands
- expose model internals
---
# Future Improvements
The pipeline must support future:
- multi-model inference
- CWE classification
- explainability
- localization
- AST integration
---
# Final Goal
Build a fast and scalable AI inference pipeline capable of:
- analyzing source code securely
- detecting vulnerabilities accurately
- supporting production deployment