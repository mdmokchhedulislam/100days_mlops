The xFusionCorp Industries ML platform team practices canary rollouts using a pure-Python simulator before integrating the same traffic-split strategy into Argo Rollouts. The canary_deploy.py scaffold located at /root/code/serving/ is responsible for monitoring the v2 error rate and steering the rollout. However, the canary policy, including the phase-weight ramp and rollback threshold, has not yet been implemented. Your task is to develop the canary policy in canary_deploy.py to ensure that the simulator effectively ramps traffic from 95/5 to 70/30 and finally to 0/100, concluding with the outcome OUTCOME: PROMOTED under healthy v2 conditions.


The project layout under /root/code/serving/:

canary_deploy.py – Defines CanaryDeployer with promote(), rollback(), and send_requests(), plus a main() that runs three phases and rolls back if the v2 error rate exceeds ROLLBACK_THRESHOLD. send_requests(), rollback(), and main() are wired; promote()'s phase-weight ramp and the ROLLBACK_THRESHOLD value are left as TODOs. No network or model is used; the v2 error rate is simulated at 2 % per request via a seeded random.Random(seed=42).
The end state must include:

ROLLBACK_THRESHOLD is set to a value that keeps the healthy v2 rollout (simulated at a 2 % error rate) above the bar so it promotes rather than rolls back.
promote() ramps the weights across the three phases: phase 1 → 95/5; phase 2 → 70/30; phase 3 → 0/100.
Running the script prints three Phase N: lines, a Total requests: 300 line, and ends with OUTCOME: PROMOTED.
The phase-2 log line shows v1_requests > v2_requests.
Managed canary controllers such as Argo Rollouts, Flagger, and Linkerd ship with a small default rollback threshold—set high enough it lets a broken v2 do meaningful damage before the rollout halts, too low and a healthy rollout is aborted on noise.



