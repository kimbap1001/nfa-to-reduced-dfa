# nfa-to-reduced-dfa

A Python implementation of automata conversion pipeline:
**(ε-)NFA → DFA → Reduced DFA**

Developed as a Formal Languages course assignment.

---

## Overview

Given an NFA (including ε-transitions) defined in a structured text file,
this program automatically converts it through three stages and outputs
each result to a file.

**Stage 1:** Parse (ε-)NFA from text file  
**Stage 2:** Convert to DFA via subset construction  
**Stage 3:** Minimize DFA via partition refinement  

---

## Key Design Decisions

### Delta Function as Dictionary
Delta functions are stored as a Python `dict` with `(state, symbol)` tuples
as keys and result state sets as values. This allows O(1) lookup by
`(state, symbol)` pair and cleanly handles multiple transitions per state.

### Tuple-based Compound States
During NFA→DFA conversion, compound states (sets of NFA states) are
represented as tuples rather than lists, enabling their use as dictionary
keys. After conversion, all states are substituted back into
single-state names (`q000`, `q001`, ...) via `faStateSubst()`.

---

## Key Algorithms

### ε-Closure (`closure()`)
Computes all states reachable from a given state via ε-transitions only.
Uses iterative expansion to handle chained ε-transitions.

### Subset Construction (`NFAtoDFA()`)
Builds the DFA transition table starting from the ε-closure of the NFA
start state. Only accessible states are added, and ε-transitions are
handled by applying closure after each transition.

### Partition Refinement (`reduceDFA()`)
Minimizes the DFA by iteratively splitting state groups:
1. Initialize with `{final states}` and `{non-final states}`
2. For each group, check if all states have identical transition targets
   (by group index)
3. Split groups where transitions diverge
4. Repeat until no further splits occur

---

## Input Format
```
StateSet = { q000, q001, q002 }
TerminalSet = { a, b }
DeltaFunctions = {
(q000, a) = {q000, q001}
(q001, ε) = {q002}
}
StartState = q000
FinalStateSet = { q002 }
```

---

## Usage

Place `nfa1.txt` through `nfa10.txt` in the same directory as `nfa-dfa.py`,
then run:

```bash
python nfa-dfa.py
```

Generates `nfa1Result.txt` through `nfa10Result.txt`,
each containing the step-by-step conversion results.

---

## Test Cases

Verified against 10 NFA examples:
- Textbook examples (예제 3.18, 3.22, 3.23, 3.26)
- NFA with ε-transitions
- NFA where reduced DFA has fewer states than original DFA
- NFA where minimization produces a single-state DFA
- Edge cases where DFA and reduced DFA are identical

All results manually verified against hand-computed transition tables.

---

## Environment

- Python 3.x
- No external dependencies
