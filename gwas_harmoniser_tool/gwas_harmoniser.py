#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
import glob
import shutil
import gzip
import yaml

# ---------------------------
# Argument parser
# ---------------------------
parser = argparse.ArgumentParser(
    description="Run GWAS summary statistics harmoniser and get harmonised table output (remote GitHub version)"
)
parser = argparse.ArgumentParser(description="Run GWAS summary statistics harmoniser and get harmonised table output")
parser.add_argument("--input", required=True, help="Path to input TSV file")
parser.add_argument("--genome_build", required=True, help="Genome build to harmonise to (e.g., 38)")
parser.add_argument("--threshold", required=True, help="Threshold for palindromic variants (e.g., 0.99)")
parser.add_argument("--ref_dir", required=True, help="Directory containing reference data")
parser.add_argument("--repo_url", required=True, help="URL of the GWAS harmoniser repo")
parser.add_argument("--output", required=True, help="Path to save harmonised TSV output")
parser.add_argument("--chrom", default="22", help="Chromosome to harmonise (default 22)")
args = parser.parse_args()


# ---------------------------
# Step 1: Check metadata
# ---------------------------
meta_file = os.path.splitext(args.input)[0] + "-meta.yaml"
if not os.path.exists(meta_file):
    print(f"[ERROR] Missing metadata file: {meta_file}")
    sys.exit(1)
else:
    print(f"[INFO] Found metadata file: {meta_file}")
    with open(meta_file, "r") as f:
        metadata = yaml.safe_load(f)
        print("[INFO] Metadata contents:")
        print(metadata)

# ---------------------------
# Step 2: Verify references
# ---------------------------
if not os.path.isdir(args.ref_dir):
    print(f"[ERROR] Reference directory does not exist: {args.ref_dir}")
    sys.exit(1)

vcf_files = glob.glob(os.path.join(args.ref_dir, "*.vcf.gz"))
if not vcf_files:
    print(f"[ERROR] No VCF reference files found in {args.ref_dir}")
    sys.exit(1)
else:
    print(f"[INFO] Found {len(vcf_files)} reference VCFs in {args.ref_dir}")

# ---------------------------
# Step 3: Run harmonisation directly from GitHub
# ---------------------------
cmd = [
    "nextflow", "run", args.repo_url,
    "-r", "v1.1.7",  # <- instead of "master"
    "-profile", "conda",
    "--file", args.input,
    "--to_build", args.genome_build,
    "--threshold", args.threshold,
    "--ref_dir", args.ref_dir,
    "--chrom", args.chrom,
    "--harm"
]


print("[INFO] Running harmonisation pipeline directly from GitHub...")
print("Command:", " ".join(cmd))

process = subprocess.run(cmd, capture_output=True, text=True)
print(process.stdout)
print(process.stderr, file=sys.stderr)

# ---------------------------
# Step 4: Find harmonised output
# ---------------------------
result_files = glob.glob("**/*_h.tsv*", recursive=True)
if not result_files:
    print("[ERROR] No harmonised file found.")
    sys.exit(1)

harmonised_file = result_files[0]
print(f"[INFO] Found harmonised file: {harmonised_file}")

# ---------------------------
# Step 5: Save output
# ---------------------------
if harmonised_file.endswith(".gz"):
    with gzip.open(harmonised_file, "rb") as f_in:
        with open(args.output, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
else:
    shutil.copyfile(harmonised_file, args.output)

print(f"[SUCCESS] Harmonised output saved to: {args.output}")
