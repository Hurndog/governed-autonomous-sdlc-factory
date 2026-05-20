# Example Workflows

This directory contains runnable example workflows demonstrating key platform capabilities.

## Available Examples

### 1. Finance Workflow (`finance_workflow.py`)

Demonstrates automated financial report generation with governance.

**Features:**
- Sovereign-required routing (no data leaves premises)
- Multi-model validation of numerical accuracy
- Evidence bundle generation for regulatory compliance
- Explainability for every figure

**Run:**
```bash
cd examples
python finance_workflow.py
```

### 2. Invoice Processing (`invoice_processing.py`)

Demonstrates automated invoice processing with multi-model arbitration.

**Features:**
- OCR-based invoice ingestion
- Multi-model extraction and validation
- Disagreement detection between models
- Operator escalation for edge cases

**Run:**
```bash
cd examples
python invoice_processing.py
```

### 3. Governance Escalation (`governance_escalation.py`)

Demonstrates automatic governance escalation when trust degrades.

**Features:**
- Trust score monitoring
- Automatic escalation on threshold breach
- Operator intervention recording
- Audit trail generation

**Run:**
```bash
cd examples
python governance_escalation.py
```

### 4. Multi-Model Arbitration (`multi_model_arbitration.py`)

Demonstrates multi-model execution and disagreement analysis.

**Features:**
- Parallel model execution
- Consensus scoring
- Contradiction detection
- Trust-weighted decision making

**Run:**
```bash
cd examples
python multi_model_arbitration.py
```

### 5. Memory Archival (`memory_archival.py`)

Demonstrates memory lifecycle management.

**Features:**
- Memory aging
- Archival with evidence preservation
- Quarantine and restore
- Lifecycle state transitions

**Run:**
```bash
cd examples
python memory_archival.py
```

### 6. Intervention Scenario (`intervention_scenario.py`)

Demonstrates operator intervention capabilities.

**Features:**
- Pause and resume
- Quarantine and rollback
- Trust impact assessment
- Audit trail recording

**Run:**
```bash
cd examples
python intervention_scenario.py
```

### 7. Trust Degradation (`trust_degradation.py`)

Demonstrates trust score changes based on model behavior.

**Features:**
- Trust score computation
- Autonomy level adjustment
- Governance response to low trust
- Recovery through successful execution

**Run:**
```bash
cd examples
python trust_degradation.py
```

## Running All Examples

```bash
cd examples
python run_all.py
```

## Prerequisites

```bash
# Install example dependencies
pip install -r requirements-examples.txt

# Ensure backend is running
curl http://localhost:8000/api/v1/health
```
