The xFusionCorp Industries ML platform team operates a shell-based Docker CI pipeline for the fraud-detection Flask service. In this process, tests are executed, the image is built, a short git SHA is applied as the tag, and the tagged image is subsequently pushed to the local private registry. However, the pre-staged build.sh located at /root/code/ci/ does not currently execute cleanly from start to finish. Your objective is to rectify the configuration so that ./build.sh completes its execution without errors and that the registry catalog displays ml-ci-app tagged with the current git short SHA.


The Docker daemon is already running and a registry:2 container named local-registry is already up on host port 5555.

The repository layout under /root/code/ci/:

app/app.py – Flask service exposing /health + /predict on port 8086. Correct.
app/test_app.py – Three pytest cases covering /health, the fraud-flag flow, and the pass-through flow. Correct.
app/Dockerfile – python:3.11-slim, installs flask, COPYs app.py, exposes 8086, runs the Flask app. Correct.
app/.git/ – A local git repository initialised at startup with a single "Initial CI baseline" commit. Correct.
build.sh – Executable shell script with four stages (test → build → tag → push). Needs attention.
The end state must include:

./build.sh runs end-to-end without non-zero exit.
docker images ml-ci-app:latest lists the locally-built image.
curl http://localhost:5555/v2/_catalog lists ml-ci-app in the repositories array.
curl http://localhost:5555/v2/ml-ci-app/tags/list lists the current git -C app rev-parse --short HEAD value in the tags array.
Run ./build.sh against the scaffold as-is; each re-run surfaces the next blocker. All fixes live inside build.sh.




