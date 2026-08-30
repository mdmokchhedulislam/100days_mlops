The xFusionCorp Industries ML platform team is piloting Kubeflow Pipelines on their kind cluster, with the KFP web UI exposed on port 5000. A two-component pipeline source (prep_data → train) is staged at /root/code/kfp/pipeline.py, but its pipeline function wires only the first component. Your task is to complete the DAG so train runs after prep_data, compile it to an IR YAML with the KFP SDK, upload it through the KFP UI as fraud-training, then create and run it from the Default experiment and confirm the run reaches Succeeded.


Kubeflow Pipelines is running on the kind cluster and its UI is exposed via the KFP UI button at the top of the lab (port 5000). A two-component pipeline source is staged at /root/code/kfp/pipeline.py: the @dsl.component functions prep_data and train are written, but fraud_training_pipeline wires only prep_data — inspect the pipeline function to see what is missing.

Compile the source to an IR YAML (the KFP SDK is installed):

cd /root/code/kfp && python3 pipeline.py

The KFP UI's file picker reads from your local machine, not the lab container, so download the compiled pipeline.yaml from the VS Code Explorer before uploading it through the UI.

The end state must include:

The KFP UI is reachable on :5000.
/root/code/kfp/pipeline.py's pipeline function wires the train component after prep_data.
GET /apis/v2beta1/pipelines returns a pipeline named fraud-training.
At least one run from that pipeline reaches state SUCCEEDED (tests poll up to 420 s).
KFP compiles each @dsl.component into one container-per-step; the @dsl.pipeline function is the DAG that wires them, and python3 pipeline.py runs the compiler to produce the IR YAML the KFP UI executes. Components run in parallel unless an explicit ordering edge declares a dependency.