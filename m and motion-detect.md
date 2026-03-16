
use m.py rename it to motion-detect.py and delete the original motion-detect.py file.

The differences are small but the choice is clear for the Docker setup.

**What changed between the two files:**

`motion-detect.py` has all configuration hardcoded as constants at the top:
```python
THRESHOLD = 25
MIN_AREA = 800
BLUR_SIZE = 21
...
```

`m.py` reads every value from environment variables with fallbacks:
```python
THRESHOLD = int(os.getenv("THRESHOLD", 25))
MIN_AREA  = int(os.getenv("MIN_AREA", 800))
BLUR_SIZE = int(os.getenv("BLUR_SIZE", 21))
...
```

That is the only meaningful difference. The detection logic, the dual-stream setup, the encoder handling — identical. Both have `format: "RGB888"` on the lores stream (the uploaded file's `# FIX` comment suggests that was a bug fix that was then carried into `m.py`).

**Which one to use for the Docker setup: `m.py` — without question.**

The entire point of the Docker setup is configuration through the `.env` file. The `docker-compose.yml` has `env_file: .env` which injects those variables into the container. With `motion-detect.py`, that mechanism does nothing — you would have to rebuild the image every time you want to change sensitivity or resolution. With `m.py`, you edit `.env`, run `docker compose up`, done.

The only practical issue is the filename mismatch. The Dockerfile has:
```dockerfile
COPY motion-detect.py .
CMD ["python3", "motion-detect.py"]
```

But the file in the repo is `m.py`. You need to either rename `m.py` to `motion-detect.py` before building, or update the Dockerfile to match the actual filename. The README also references `motion-detect.py`, so renaming `m.py` is probably the cleaner fix.