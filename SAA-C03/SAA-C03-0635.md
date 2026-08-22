# Question #635 - Topic 1

A company uses Amazon FSx for NetApp ONTAP in its primary AWS Region for CIFS and NFS file shares. Applications that run on Amazon EC2 instances access the file shares. The company needs a storage disaster recovery (DR) solution in a secondary Region. The data that is replicated in the secondary Region needs to be accessed by using the same protocols as the primary Region. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Create an AWS Lambda function to copy the data to an Amazon S3 bucket. Replicate the S3 bucket to the secondary Region.

**B.** Create a backup of the FSx for ONTAP volumes by using AWS Backup. Copy the volumes to the secondary Region. Create a new FSx for ONTAP instance from the backup.

**C.** Create an FSx for ONTAP instance in the secondary Region. Use NetApp SnapMirror to replicate data from the primary Region to the secondary Region.

**D.** Create an Amazon Elastic File System (Amazon EFS) volume. Migrate the current data to the volume. Replicate the volume to the secondary Region.

## 1. CONTEXT & DE BAI
- **Scenario:** FSx for ONTAP (CIFS + NFS) trong primary Region. Can DR solution o secondary Region voi cung protocols.
- **Existing Resources:** FSx for ONTAP, EC2 instances.
- **Current Issue/Goal:** Cross-region DR cho FSx for ONTAP, cung protocol (CIFS/NFS), least operational overhead.

## 2. KEYWORDS QUAN TRONG
| Keyword | Y nghia / Goi y |
|---------|-----------------|
| `FSx for NetApp ONTAP` | NetApp file system tren AWS. |
| `CIFS and NFS` | Can support ca hai protocols. |
| `same protocols` | Secondary Region cung phai ho tro CIFS + NFS. |
| `NetApp SnapMirror` | Built-in NetApp replication technology, tu dong, async. |
| `least operational overhead` | SnapMirror la native solution, toi uu nhat cho FSx for ONTAP DR. |

## 3. YEU CAU CUA DE
- **Question type:** Least operational overhead
- **Constraints:** Cross-region DR, same protocols (CIFS/NFS), FSx for ONTAP

## 4. DAP AN DUNG
**Dap an: C**

**Giai thich:**
- NetApp SnapMirror: native replication technology cho NetApp ONTAP, duoc ho tro tren FSx for ONTAP.
- Replicate truc tiep tu primary region sang secondary region FSx for ONTAP instance, tu dong, async.
- Secondary instance cung ho tro CIFS + NFS (cung protocols).
- Operational overhead thap nhat vi SnapMirror la built-in feature.

## 5. CAC DAP AN SAI
**Dap an A:**
- Lambda copy + S3 replication: can code, operational overhead cao. S3 khong ho tro CIFS/NFS.

**Dap an B:**
- AWS Backup: point-in-time backup, khong phai continuous replication. Can restore de su dung => operational overhead cao hon SnapMirror.

**Dap an D:**
- EFS: chi ho tro NFS, khong ho tro CIFS. Phai migrate du lieu => operational overhead cao.

## 6. MEO GHI NHO (Memory Hook)
*"FSx for ONTAP DR => NetApp SnapMirror (native replication, cung protocols). AWS Backup = restore needed."*
