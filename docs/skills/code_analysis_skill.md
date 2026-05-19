# Code Analysis Skill

## Goal
Detect suspicious code patterns.

## Supported Patterns
- strcpy
- gets
- eval
- system()
- SQL string concatenation

## Output
{
  "pattern": "strcpy",
  "issue": "Potential buffer overflow"
}