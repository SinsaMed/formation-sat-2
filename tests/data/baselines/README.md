# Baseline Data Repository

## Purpose

This directory stores canonical outputs from the nominal simulation campaign once the end-to-end pipeline is commissioned. Each file shall reflect a validated Systems Tool Kit (STK 11.2) compatible product to ensure regression checks remain meaningful across software updates.

## Maintenance Guidance

1. Export the latest trusted simulation artefacts into this folder using deterministic filenames.
2. Record any preprocessing steps inside the accompanying mission log so reviewers can reproduce the baseline.
3. Replace existing baselines only after verifying the new results against mission requirements and documenting the justification in the change log.
4. Retain the `.gitkeep` placeholder until the directory contains approved artefacts to preserve repository structure.
