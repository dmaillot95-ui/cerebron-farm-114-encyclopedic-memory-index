import hashlib,json,pathlib,sys
records=[
 {"rdx_id":"RDX-CANARY-INDEX","object_id":"CLAIM-001","object_type":"CLAIM","content":"RAG can use external knowledge without changing model weights.","provenance":["SRC-001"]},
 {"rdx_id":"RDX-CANARY-INDEX","object_id":"CLAIM-002","object_type":"CLAIM","content":"Cold benchmarks must remain excluded from training data.","provenance":["SRC-002"]},
 {"rdx_id":"RDX-CANARY-INDEX","object_id":"CLAIM-001","object_type":"CLAIM","content":"RAG can use external knowledge without changing model weights.","provenance":["SRC-001"]}
]
def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":")).encode()
index={}; duplicates=0; conflicts=[]
for r in records:
    key=f"{r['rdx_id']}::{r['object_id']}"
    sha=hashlib.sha256(canon(r)).hexdigest()
    if key not in index:
        index[key]={"sha256":sha,"record":r}
    else:
        if index[key]["sha256"]==sha: duplicates+=1
        else: conflicts.append(key)
conflict_probe={"rdx_id":"RDX-CANARY-INDEX","object_id":"CLAIM-002","object_type":"CLAIM","content":"Conflicting content under same canonical ID.","provenance":["SRC-X"]}
probe_key=f"{conflict_probe['rdx_id']}::{conflict_probe['object_id']}"
probe_sha=hashlib.sha256(canon(conflict_probe)).hexdigest()
conflict_detected=(probe_key in index and index[probe_key]["sha256"]!=probe_sha)
status="PASS" if len(index)==2 and duplicates==1 and conflict_detected and not conflicts else "FAIL"
out={
 "schema":"F114_RDX_CANONICAL_INDEX_CANARY_V1","status":status,"farm_id":114,
 "canonical_count":len(index),"exact_duplicate_count":duplicates,
 "conflict_probe_detected":conflict_detected,"unexpected_conflicts":conflicts,
 "canonical_keys":sorted(index),"training_executed":False,
 "claim_ceiling":"CANONICAL_ID_INDEX_AND_CONFLICT_DETECTION_CANARY_ONLY"
}
out["receipt_sha256"]=hashlib.sha256(canon(out)).hexdigest()
pathlib.Path("artifacts").mkdir(exist_ok=True)
pathlib.Path("artifacts/rdx_canonical_index_canary.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,sort_keys=True)); sys.exit(0 if status=="PASS" else 2)
