# Squirrel Test Framework

A Git-managed automated test framework for side-channel analysis workflows, with a current focus on TVLA-based validation, reproducible scripting, and skill-oriented orchestration.

## Overview

Squirrel Test Framework is a lightweight project for organizing, executing, and maintaining side-channel evaluation workflows in a structured and reproducible way. It is designed to support:

- automated side-channel test execution
- TVLA-oriented validation pipelines
- reusable scripts and source modules
- example-driven usage
- skill-based orchestration and extension
- regression-style testing for analysis code

This repository is intended to serve as both a development workspace and a reusable testbench for validating side-channel analysis functionality.

## Repository Structure

```text
squirrel-test-framework/
├── cracknuts_squirrel_reference/   # Reference materials and related resources
├── examples/                       # Minimal examples and usage demonstrations
├── scripts/                        # Utility scripts and runnable helpers
├── squirrel-skills/                # Skill definitions / skill-related assets
├── src/                            # Core source code
├── tests/                          # Test cases and validation logic
├── tvla-test/                      # TVLA-specific workflows and experiments
└── SKILL.md                        # Skill entry / usage document
```

## Case1: TVLA test
### Skill Entry

The skill `squirrel-dataset-prepare` is used as an entry point for generating TVLA-related test scripts.
Its purpose is to:
- prepare dataset-driven test cases
- generate runnable shell scripts
- standardize the structure of TVLA experiments
- simplify repeated testing across multiple leakage conditions

Generated scripts will be placed under the `tvla-test/` directory, while test results will be stored in `examples/`.

The framework can automatically generate multiple types of test scripts, including scripts for evaluating:
- leakage strength
- leakage position
- leakage quantity
After the scripts are generated, they can be executed directly through shell commands. For example:

```bash
./tvla-test/run_tvla_dual.sh
./tvla-test/run_tvla_medium.sh
./tvla-test/run_tvla_strong.sh
./tvla-test/run_tvla_weak.sh
```

## Future Updates
This framework is still evolving, and additional testing functions will be integrated incrementally in future updates.
