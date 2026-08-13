The xFusionCorp Industries ML platform team is currently enhancing the fraud-detector continuous integration (CI) process. The existing main.yml file contains three similar inline jobs that have been duplicated, requiring the same changes to be implemented for each on every pull request (PR). A team member has already separated the lint, test, and report stages into distinct files located in the .gitea/workflows/ directory—each configured to declare on: workflow_call—and has opened a PR that modifies one job (lint) to call the reusable workflow. Your task is to complete this refactor by converting the two remaining inline jobs in main.yml into uses: calls, thereby enabling the main run to expand into three nested workflow_call executions.


The Gitea UI is on port 3000 (Gitea button). Admin credentials: gitea-admin / gitea2026. The repo is at http://localhost:3000/gitea-admin/fraud-detector and a working clone is at /root/code/fraud-detector, already checked out on branch add-reusable-workflows. The PR is pre-opened.

Four workflow files ship in .gitea/workflows/. lint.yml, test.yml, and report.yml are reusable callees, each triggered by on: workflow_call. main.yml is the caller: jobs.lint already calls ./.gitea/workflows/lint.yml via uses: (the example wiring), while jobs.test and jobs.report are still inline runs-on + steps jobs that duplicate logic already parked in the callee files. Those two inline job bodies need to become single uses: lines mirroring the lint job — a job cannot declare both uses: and steps:, so the inline blocks are removed entirely.

The end state must include:

lint.yml, test.yml, and report.yml each declare on: workflow_call on the PR head branch.
main.yml defines jobs lint, test, and report, each with a uses: key pointing at the matching ./.gitea/workflows/<name>.yml.
No job in main.yml mixes uses: with steps: (illegal in Actions YAML).
The PR head commit's combined status reaches success.
Reusable workflows turn a monolithic main.yml into a small graph of composable pieces. Each callee becomes the canonical definition for its concern (lint / test / report); any number of callers can consume it. When you later add a release.yml workflow for tagged pushes, it can reuse the same test.yml callee—no more copy-paste sync issues across files.