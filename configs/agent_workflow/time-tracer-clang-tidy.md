---
description: Safe Clang-Tidy Refactoring Workflow
---

# Safe Refactoring Protocol (Agent Guidelines)

In order to safely improve code quality without breaking the build, the Agent must strictly follow this **Iterative Loop**.

### Core Rules: "3-1-Revert"
1. **3 Successful Cycles**: Stop and checkpoint after 3 successful fix iterations.
2. **1 Build Failure**: Stop IMMEDIATELY if `build_fast.sh` fails.
3. **Revert on Fail**: If the build fails, **REVERT** the last change. Do not try to "fix forward".

---

### 1. Analysis (Scan)
Run the check-only script to generate a diagnostic report.
```bash
./scripts/build_tidy.sh
# Expected: Exit code 1 (due to warnings). This is normal.
```

### 2. Selection (Scope)
Parse the log to choose a **small, atomic** task.
```bash
python scripts/tidy_analyzer.py build_tidy/build.log
```
**Constraint**: Pick **ONE** file or **ONE** specific rule type (e.g., `readability-identifier-naming`).

### 3. Execution (Apply Fix)
- Modify the code manually.
- **Do not** use `--fix` blindly.
- Apply no more than **5 changes** in a single batch.

### 4. Verification (Verify)
Run the fast build script (skips optimization/static analysis) to verify syntax.
```bash
./scripts/build_fast.sh
```
- **If SUCCESS (Exit 0)**: 
  - Increment cycle counter.
  - If counter < 3, GOTO Step 2.
  - If counter == 3, STOP and notify user.
- **If FAILURE**: 
  - **STOP**.
  - **REVERT** changes.
  - Notify user of the specific failure.