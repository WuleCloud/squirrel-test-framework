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
