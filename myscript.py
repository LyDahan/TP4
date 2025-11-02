import os
import sys

bad = os.environ.get("BAD_COMMIT")
good = os.environ.get("GOOD_COMMIT")

if not bad or not good:
    print("ERROR: set BAD_COMMIT and GOOD_COMMIT environment variables in the workflow or shell.")
    sys.exit(1)

print("Fetching full history (required for bisect)...")
os.system("git fetch --unshallow || true")

print(f"Starting git bisect: bad={bad} good={good}")
os.system(f"git bisect start {bad} {good}")

print("Running git bisect using Django tests (python manage.py test)...")
ret = os.system("git bisect run python manage.py test")

if ret != 0:
    print("git bisect run exited with non-zero status. Inspect workflow logs for details.")
else:
    print("git bisect completed. Use 'git bisect log' locally to see the identified bad commit.")

print("Resetting bisect state...")
os.system("git bisect reset")

sys.exit(0 if ret == 0 else 1)