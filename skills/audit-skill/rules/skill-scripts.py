"""Semgrep fixtures: inspect with the engine, never execute."""
import ast
import os
import subprocess

# ruleid: skill-audit.python-eval-exec
eval(untrusted)
# ruleid: skill-audit.python-eval-exec
exec(untrusted)
# ok: skill-audit.python-eval-exec
ast.literal_eval(untrusted)

# ruleid: skill-audit.python-shell
subprocess.run(command, shell=True)
# ruleid: skill-audit.python-shell
os.system(command)
# ok: skill-audit.python-shell
subprocess.run(["echo", "example"], shell=False)

# ruleid: skill-audit.python-credential-literal
api_key = "synthetic-placeholder-only"
# ok: skill-audit.python-credential-literal
api_key = os.environ["TEST_KEY"]

# ruleid: skill-audit.python-runtime-install
subprocess.run(["pip", "install", "example"])
# ok: skill-audit.python-runtime-install
subprocess.run(["pip", "--version"])
