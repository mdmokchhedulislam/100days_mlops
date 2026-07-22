# """Canary-deployment simulator for the fraud-detection model.

# Runs a three-phase traffic-split rollout from the stable v1 to the
# candidate v2:

#   Phase 1 — 95 % v1 / 5 % v2   (initial canary wedge)
#   Phase 2 — 70 % v1 / 30 % v2  (confidence ramp)
#   Phase 3 — 0  % v1 / 100 % v2 (full promotion)

# Each phase fires `REQUESTS_PER_PHASE` requests, routes them per the
# current weights, and measures the v2 error rate. If the error rate
# exceeds `ROLLBACK_THRESHOLD`, the deployer rolls back to 100 % v1
# and the simulation reports `ROLLED_BACK`; otherwise it advances to
# the next phase. A clean three-phase run reports `PROMOTED`.

# Released canary tooling (Argo Rollouts, Flagger, Linkerd) uses 5 %
# as the standard rollback threshold — anything higher lets a bad
# v2 do meaningful damage before the rollout halts.
# """
# import random

# # TODO: set the canary rollback bar. Released canary tooling (Argo
# #       Rollouts, Flagger, Linkerd) halts a rollout once the candidate's
# #       error rate exceeds ~5% — set ROLLBACK_THRESHOLD to 0.05.
# ROLLBACK_THRESHOLD = 1.0
# REQUESTS_PER_PHASE = 100

# # Simulated per-request error probability of the v2 candidate.
# # Stays well below a 5 % rollback threshold under healthy conditions.
# V2_ERROR_RATE = 0.02


# class CanaryDeployer:
#     def __init__(self, seed: int = 42) -> None:
#         self._rng = random.Random(seed)
#         self.v1_weight = 1.0
#         self.v2_weight = 0.0
#         self.phase = 0

#     def promote(self) -> tuple[float, float]:
#         """Advance to the next phase's traffic weights."""
#         self.phase += 1
#         # TODO: author the canary ramp — set self.v1_weight and
#         #   self.v2_weight for each phase (self.phase is 1, 2, or 3).
#         #   Keep v1 the majority until v2 has proven itself, then hand
#         #   v2 all traffic:
#         #     phase 1 -> v1=0.95, v2=0.05   (initial 5% canary wedge)
#         #     phase 2 -> v1=0.70, v2=0.30   (confidence ramp)
#         #     phase 3 -> v1=0.00, v2=1.00   (full promotion)
#         return self.v1_weight, self.v2_weight

#     def rollback(self) -> None:
#         self.v1_weight = 1.0
#         self.v2_weight = 0.0

#     def send_requests(self, n: int = REQUESTS_PER_PHASE) -> dict:
#         v1_hits = 0
#         v2_hits = 0
#         v2_errors = 0
#         for _ in range(n):
#             if self._rng.random() < self.v1_weight:
#                 v1_hits += 1
#             else:
#                 v2_hits += 1
#                 if self._rng.random() < V2_ERROR_RATE:
#                     v2_errors += 1
#         v2_error_rate = v2_errors / v2_hits if v2_hits else 0.0
#         return {
#             "v1_requests": v1_hits,
#             "v2_requests": v2_hits,
#             "v2_errors": v2_errors,
#             "v2_error_rate": v2_error_rate,
#         }


# def main() -> None:
#     deployer = CanaryDeployer(seed=42)
#     total_requests = 0

#     for phase_num in range(1, 4):
#         v1_w, v2_w = deployer.promote()
#         print(f"Phase {phase_num}: v1={v1_w:.0%} v2={v2_w:.0%}")
#         stats = deployer.send_requests()
#         total_requests += stats["v1_requests"] + stats["v2_requests"]
#         print(
#             f"  v1_requests={stats['v1_requests']} "
#             f"v2_requests={stats['v2_requests']} "
#             f"v2_error_rate={stats['v2_error_rate']:.2%}"
#         )

#         if stats["v2_error_rate"] > ROLLBACK_THRESHOLD:
#             print(
#                 f"  ROLLBACK — v2 error rate {stats['v2_error_rate']:.2%} "
#                 f"> threshold {ROLLBACK_THRESHOLD:.0%}"
#             )
#             deployer.rollback()
#             print(f"OUTCOME: ROLLED_BACK after {phase_num} phase(s)")
#             print(f"Total requests: {total_requests}")
#             return

#     print("OUTCOME: PROMOTED")
#     print(f"Total requests: {total_requests}")


# if __name__ == "__main__":
#     main()



"""Canary-deployment simulator for the fraud-detection model.

Runs a three-phase traffic-split rollout from the stable v1 to the
candidate v2:

  Phase 1 — 95 % v1 / 5 % v2   (initial canary wedge)
  Phase 2 — 70 % v1 / 30 % v2  (confidence ramp)
  Phase 3 — 0  % v1 / 100 % v2 (full promotion)

Each phase fires `REQUESTS_PER_PHASE` requests, routes them per the
current weights, and measures the v2 error rate. If the error rate
exceeds `ROLLBACK_THRESHOLD`, the deployer rolls back to 100 % v1
and the simulation reports `ROLLED_BACK`; otherwise it advances to
the next phase. A clean three-phase run reports `PROMOTED`.

Released canary tooling (Argo Rollouts, Flagger, Linkerd) uses 5 %
as the standard rollback threshold — anything higher lets a bad
v2 do meaningful damage before the rollout halts.
"""

import random

# Canary rollback threshold (5%)
ROLLBACK_THRESHOLD = 0.05
REQUESTS_PER_PHASE = 100

# Simulated per-request error probability of the v2 candidate.
V2_ERROR_RATE = 0.02


class CanaryDeployer:
    def __init__(self, seed: int = 42) -> None:
        self._rng = random.Random(seed)
        self.v1_weight = 1.0
        self.v2_weight = 0.0
        self.phase = 0

    def promote(self) -> tuple[float, float]:
        """Advance to the next phase's traffic weights."""
        self.phase += 1

        if self.phase == 1:
            # Phase 1: 95% v1 / 5% v2
            self.v1_weight = 0.95
            self.v2_weight = 0.05

        elif self.phase == 2:
            # Phase 2: 70% v1 / 30% v2
            self.v1_weight = 0.70
            self.v2_weight = 0.30

        elif self.phase == 3:
            # Phase 3: 0% v1 / 100% v2
            self.v1_weight = 0.00
            self.v2_weight = 1.00

        return self.v1_weight, self.v2_weight

    def rollback(self) -> None:
        self.v1_weight = 1.0
        self.v2_weight = 0.0

    def send_requests(self, n: int = REQUESTS_PER_PHASE) -> dict:
        v1_hits = 0
        v2_hits = 0
        v2_errors = 0

        for _ in range(n):
            if self._rng.random() < self.v1_weight:
                v1_hits += 1
            else:
                v2_hits += 1
                if self._rng.random() < V2_ERROR_RATE:
                    v2_errors += 1

        v2_error_rate = v2_errors / v2_hits if v2_hits else 0.0

        return {
            "v1_requests": v1_hits,
            "v2_requests": v2_hits,
            "v2_errors": v2_errors,
            "v2_error_rate": v2_error_rate,
        }


def main() -> None:
    deployer = CanaryDeployer(seed=42)
    total_requests = 0

    for phase_num in range(1, 4):
        v1_w, v2_w = deployer.promote()

        print(f"Phase {phase_num}: v1={v1_w:.0%} v2={v2_w:.0%}")

        stats = deployer.send_requests()

        total_requests += stats["v1_requests"] + stats["v2_requests"]

        print(
            f"  v1_requests={stats['v1_requests']} "
            f"v2_requests={stats['v2_requests']} "
            f"v2_error_rate={stats['v2_error_rate']:.2%}"
        )

        if stats["v2_error_rate"] > ROLLBACK_THRESHOLD:
            print(
                f"  ROLLBACK — v2 error rate {stats['v2_error_rate']:.2%} "
                f"> threshold {ROLLBACK_THRESHOLD:.0%}"
            )

            deployer.rollback()

            print(f"OUTCOME: ROLLED_BACK after {phase_num} phase(s)")
            print(f"Total requests: {total_requests}")
            return

    print("OUTCOME: PROMOTED")
    print(f"Total requests: {total_requests}")


if __name__ == "__main__":
    main()