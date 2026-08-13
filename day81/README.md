The xFusionCorp Industries machine learning platform team requires that every fraud-detector release tag is reproducible from a single Gitea page. This includes the Docker image used in production, the metrics.json file that details the model's performance, and a permanent link to the commit that generated these artifacts. A tag-triggered release workflow has been established in the main branch at .gitea/workflows/release.yml. However, the two container-registry steps, labeled Build image and Push image to Gitea registry, remain incomplete and currently only contain TODO stubs that result in an exit 1, preventing any image from being shipped with a release. Your task is to implement the necessary functionality for these two steps, ensuring that the workflow successfully builds the Docker image and publishes it to Gitea's integrated container (package) registry. Following the completion of these steps, proceed to create the v0.1.0 release, allowing the tag to trigger the finalized workflow.


The Gitea UI is running on port 3000 (the Gitea button opens the login page). Admin credentials: gitea-admin / gitea2026. The repo is at http://localhost:3000/gitea-admin/fraud-detector and a working clone is at /root/code/fraud-detector (on main).

The release workflow (.gitea/workflows/release.yml) triggers on any v* tag push. Its build-and-publish job already logs in to localhost:3000 (Gitea's built-in container registry) using the pre-provisioned repository secret REGISTRY_TOKEN, resolves the image version from the git tag (steps.version.outputs.VERSION), and runs python3 -m src.train to emit artifacts/metrics.json and attach it to the release via akkuman/gitea-release-action@v1. The two steps in between — Build image and Push image to Gitea registry — are TODO stubs that currently exit 1. The surrounding steps set $REGISTRY, $IMAGE, and the resolved version (steps.version.outputs.VERSION) for the two steps to use.

Once the workflow is completed on main, publishing a v0.1.0 release (target main, any non-empty title) from the repo's Releases tab cuts the tag that triggers the run, which publishes the image and attaches the metrics file.

The end state must include:

GET /api/v1/repos/gitea-admin/fraud-detector/releases/tags/v0.1.0 returns a release whose tag_name is v0.1.0.
release.yml at the v0.1.0 tag runs docker build and docker push in the build-and-publish job (the image is published by CI, not by hand).
The tag's commit SHA reports combined status success on its checks.
The release's assets array contains an entry whose name resolves to metrics.json.
Gitea's packages API (GET /api/v1/packages/gitea-admin?type=container) lists a container package named fraud-detector with a version equal to v0.1.0 (or 0.1.0).
Tagging a release is the moment a commit becomes addressable by humans, not just by SHA. The workflow's job is to make sure the release carries everything downstream systems need—an image reference for the deployer, a metrics file for compliance, a signed tag for provenance—so the Releases page becomes the single source of truth for what's running in production.




