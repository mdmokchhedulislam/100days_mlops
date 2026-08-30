# """Two-component Kubeflow Pipelines v2 source.

# Structure: ``prep_data`` → ``train``. Each component runs as its own
# pod on the kind cluster managed by Kubeflow Pipelines. The pipeline
# function below is unfinished -- it wires only the first component.
# Complete the DAG, then compile this file to ``pipeline.yaml``
# (``python3 pipeline.py``) and upload that artefact through the KFP UI.
# """
# from kfp import compiler, dsl

# PIPELINE_NAME = "fraud-training"


# @dsl.component(base_image="python:3.11-slim")
# def prep_data():
#     print("[prep_data] synthesising training data: synthetic-rows=100")


# @dsl.component(base_image="python:3.11-slim")
# def train():
#     print("[train] training on synthetic data -> model artefact ready")


# @dsl.pipeline(
#     name=PIPELINE_NAME,
#     description="Synthetic two-step training pipeline for the KFP lab.",
# )
# def fraud_training_pipeline():
#     prep = prep_data()
#     # TODO: Complete the DAG. Call the `train` component and make it run
#     # AFTER `prep_data` -- KFP runs components in parallel unless you
#     # declare a dependency. Chain the ordering with `.after(prep)`.


# if __name__ == "__main__":
#     compiler.Compiler().compile(
#         pipeline_func=fraud_training_pipeline,
#         package_path="pipeline.yaml",
#     )
#     print("Wrote pipeline.yaml -- upload this file via the KFP UI.")




"""Two-component Kubeflow Pipelines v2 source.

Structure: ``prep_data`` → ``train``. Each component runs as its own
pod on the kind cluster managed by Kubeflow Pipelines. The pipeline
function below is unfinished -- it wires only the first component.
Complete the DAG, then compile this file to ``pipeline.yaml``
(``python3 pipeline.py``) and upload that artefact through the KFP UI.
"""

from kfp import compiler, dsl

PIPELINE_NAME = "fraud-training"


@dsl.component(base_image="python:3.11-slim")
def prep_data():
    print("[prep_data] synthesising training data: synthetic-rows=100")


@dsl.component(base_image="python:3.11-slim")
def train():
    print("[train] training on synthetic data -> model artefact ready")


@dsl.pipeline(
    name=PIPELINE_NAME,
    description="Synthetic two-step training pipeline for the KFP lab.",
)
def fraud_training_pipeline():
    prep = prep_data()

    # train runs AFTER prep_data
    train_task = train().after(prep)


if __name__ == "__main__":
    compiler.Compiler().compile(
        pipeline_func=fraud_training_pipeline,
        package_path="pipeline.yaml",
    )

    print("Wrote pipeline.yaml -- upload this file via the KFP UI.")