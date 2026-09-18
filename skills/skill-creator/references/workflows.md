# Workflow Patterns

## Sequential Workflows

Use an ordered sequence when dependencies or fragile operations require it.
Complexity alone does not require fixed phases. For flexible work, describe the
outcome, relevant decision criteria, and evidence, and let the agent choose the
approach. Consult sibling guidance without inheriting its full workflow.

For a sequence with actual dependencies, give a compact overview:

```markdown
Filling a PDF form involves these steps:

1. Analyze the form (run analyze_form.py)
2. Create field mapping (edit fields.json)
3. Validate mapping (run validate_fields.py)
4. Fill the form (run fill_form.py)
5. Verify output (run verify_output.py)
```

## Conditional Workflows

For tasks with branching logic, guide the agent through decision points:

```markdown
1. Determine the modification type:
   **Creating new content?** → Follow "Creation workflow" below
   **Editing existing content?** → Follow "Editing workflow" below

2. Creation workflow: [steps]
3. Editing workflow: [steps]
```