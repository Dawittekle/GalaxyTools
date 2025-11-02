#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
import glob
import shutil
import gzip

# ---------------------------
# Argument parser
# ---------------------------
parser = argparse.ArgumentParser(description="Run GWAS summary statistics harmoniser and get harmonised table output")
parser.add_argument("--input", required=True, help="Path to input TSV file")
parser.add_argument("--genome_build", required=True, help="Genome build to harmonise to (e.g., 38)")
parser.add_argument("--threshold", required=True, help="Threshold for palindromic variants (e.g., 0.99)")
parser.add_argument("--ref_dir", required=True, help="Directory containing reference data (VCF/Parquet files)")
parser.add_argument("--repo_url", required=True, help="URL of the GWAS harmoniser repo")
parser.add_argument("--local_repo", required=True, help="Local path to clone the harmoniser repo")
parser.add_argument("--output", required=True, help="Path to save harmonised TSV output")
parser.add_argument("--chrom", default="22", help="Chromosome to harmonise (default 22)")
args = parser.parse_args()

# ---------------------------
# Clone or update repo
# ---------------------------
if not os.path.exists(args.local_repo):
    print(f"[INFO] Cloning repository from {args.repo_url} to {args.local_repo}...")
    subprocess.run(["git", "clone", args.repo_url, args.local_repo], check=True)
else:
    print(f"[INFO] Repository already exists at {args.local_repo}, pulling latest changes...")
    subprocess.run(["git", "-C", args.local_repo, "pull"], check=True)

# ---------------------------
# Check that .tsv-meta.yaml exists
# ---------------------------
meta_file = os.path.splitext(args.input)[0] + "-meta.yaml"
if not os.path.exists(meta_file):
    print(f"[ERROR] Missing metadata file for input: {meta_file}")
    print("You must create a .tsv-meta.yaml file in the same folder as your input TSV.")
    sys.exit(1)

# ---------------------------
# Build harmonisation command
# ---------------------------
cmd = [
    "nextflow", "run", args.local_repo,
    "-r", "master",
    "-profile", "conda",
    "--file", args.input,
    "--to_build", args.genome_build,
    "--threshold", args.threshold,
    "--ref_dir", args.ref_dir,
    "--chrom", args.chrom,
    "--harm"
]

print("[INFO] Running harmonisation pipeline...")
print("Command:", " ".join(cmd))

# ---------------------------
# Execute pipeline
# ---------------------------
process = subprocess.run(cmd, capture_output=True, text=True)
print(process.stdout)
print(process.stderr, file=sys.stderr)

# ---------------------------
# Search for harmonised file
# ---------------------------
# Nextflow creates *_h.tsv or *_h.tsv.gz
pattern = os.path.join(args.local_repo, "**", "*_h.tsv*")
result_files = glob.glob(pattern, recursive=True)

if not result_files:
    print("[ERROR] No harmonised file found. Check that the pipeline ran successfully and reference files exist.")
    sys.exit(1)

harmonised_file = result_files[0]
print(f"[INFO] Found harmonised file: {harmonised_file}")

# ---------------------------
# Save harmonised TSV to output
# ---------------------------
# If gzipped, unzip it
if harmonised_file.endswith(".gz"):
    with gzip.open(harmonised_file, "rb") as f_in:
        with open(args.output, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
else:
    shutil.copyfile(harmonised_file, args.output)

print(f"[SUCCESS] Harmonised TSV saved to: {args.output}")
