# myscript.py
import os
import sys
import shlex

BAD = os.environ.get("BAD_HASH", "").strip()
GOOD = os.environ.get("GOOD_HASH", "").strip()

if not BAD or not GOOD:
    print("ERROR: Please provide BAD_HASH and GOOD_HASH as environment variables.")
    print("Example: BAD_HASH=c1a4be04... GOOD_HASH=e4cfc6f7... python myscript.py")
    sys.exit(2)

def run(cmd):
    print(f"+ {cmd}")
    rc = os.system(cmd)
    if rc != 0:
        print(f"Command failed with exit code {rc >> 8}")
    return rc

# Ensure full history (important on CI; harmless locally)
run("git fetch --all --tags --prune")

# Reset any previous bisect session
run("git bisect reset || true")

# Start automatic bisect
run(f"git bisect start {shlex.quote(BAD)} {shlex.quote(GOOD)}")

# Test command for each checked-out commit:
# - try to (re)install deps if requirements.txt exists
# - try to run migrations (Django), but don't fail the whole step if not needed
# - run the test suite; exit code decides good/bad for this commit
test_cmd = (
    "bash -lc '"
    "([ -f requirements.txt ] && pip install -r requirements.txt || true) && "
    "(python manage.py migrate --noinput || true) && "
    "python manage.py test'"
)

rc = run(f"git bisect run {test_cmd}")

# Save a log of the bisect reasoning
run("git bisect log > bisect.log || true")
run("git bisect visualize || true")  # prints handy summary if available

# Always return to the original state
run("git bisect reset")

# Propagate the bisect run's exit code (0 when it successfully found the first bad commit)
sys.exit(rc >> 8)
