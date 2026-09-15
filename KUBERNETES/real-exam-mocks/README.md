# 🎯 CKA Real Exam Mocks — Authentic Performance-Based Scenarios (English)

> This directory contains **authentic CKA (Certified Kubernetes Administrator) exam scenario questions** crawled and aggregated from active DevOps communities, Reddit (`r/kubernetes`, `r/devops`), GitHub real-exam trackers, and Killer.sh simulator reports.
>
> **Why 100% English?**
> The actual CKA exam conducted by CNCF & The Linux Foundation is **100% in English** (or Japanese/Chinese/German, NO Vietnamese). Practicing with English task descriptions is **MANDATORY** to build immediate reflex, familiarize yourself with official Kubernetes phrasing, keywords, and command-line expectations.

---

## 📑 Structure of Real Exam Mocks

Each mock exam consists of **17 performance-based tasks** totaling **100% weightage**, strictly mirroring the format of the official 120-minute exam:

```text
KUBERNETES/real-exam-mocks/
├── README.md                 # Exam rules, scoring guide & strategy
├── REAL-MOCK-EXAM-01.md      # Set 1: Core Standard Exam (Etcd, Upgrade, Node NotReady, RBAC, NetPol)
├── REAL-MOCK-EXAM-02.md      # Set 2: Advanced & Killer.sh Level (Multi-AZ Storage, Static Pods, Custom Scheduler)
└── REAL-MOCK-EXAM-03.md      # Set 3: Speed & Accuracy Sprint (Ingress TLS, CSR Approval, PSA, JSONPath)
```

---

## ⏱️ Real Exam Simulation Rules (Strict Protocol)

To ensure this practice directly leads to passing on your first attempt:

1. **Time Limit:** Exactly **120 minutes (2 hours)** for all 17 questions.
2. **Context Switching Rule (CRITICAL):**
   - Every task starts with:
     ```bash
     kubectl config use-context <cluster-name>
     ```
   - You **MUST** run this command before attempting anything in that task. In the real exam, working in the wrong context yields **0 points** for that question.
3. **Allowed Resources:**
   - Only **1 single browser tab** open to:
     - `https://kubernetes.io/docs/`
     - `https://kubernetes.io/blog/`
     - `https://github.com/kubernetes/`
   - **NO Google search, NO ChatGPT, NO external notes!**
4. **Passing Score:**
   - Linux Foundation Passing Score: **66%**.
   - Personal Target for Guaranteed Success: **≥ 85%**.

---

## 📊 Domain Distribution per Mock Exam

| Domain | Weight | Typical Tasks in Mock |
|---|---|---|
| **Troubleshooting** | **30%** | Node `NotReady` (Kubelet crash), Static Pod crash (API Server flag error), Pod `CrashLoopBackOff`, CoreDNS failure |
| **Cluster Architecture & Installation** | **25%** | Kubeadm Upgrade (Control Plane & Worker), ETCD Snapshot Backup & Restore, RBAC Roles, User CSR |
| **Services & Networking** | **20%** | ClusterIP / NodePort expose, Ingress with TLS, NetworkPolicy microsegmentation, FQDN resolution |
| **Workloads & Scheduling** | **15%** | Deployments RollingUpdate, DaemonSet, StatefulSet, Taints & Tolerations, NodeAffinity, Native Sidecar |
| **Storage** | **10%** | PersistentVolume, PersistentVolumeClaim, StorageClass `WaitForFirstConsumer`, Volume Expansion |

---

## 🚀 Quick Navigation

- 📝 [Start REAL-MOCK-EXAM-01 (Set 1)](REAL-MOCK-EXAM-01.md)
- 📝 [Start REAL-MOCK-EXAM-02 (Set 2)](REAL-MOCK-EXAM-02.md)
- 📝 [Start REAL-MOCK-EXAM-03 (Set 3)](REAL-MOCK-EXAM-03.md)
