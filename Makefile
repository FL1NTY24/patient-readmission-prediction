# Makefile
install:
    pip install -r requirements.txt
test:
    pytest tests/
format:
    black pipeline.py monitor.py app.py mlops_project.py
run-pipeline:
    python pipeline.py
run-monitor:
    python monitor.py
