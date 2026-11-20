PY ?= python3
export PYTHONPATH := src

.PHONY: test selftest lint labels cvat-project

test:
	$(PY) -m pytest -q

selftest:
	$(PY) -m road_lab.road_check selftest

labels:
	$(PY) -m road_lab.taxonomy

cvat-project:
	$(PY) -m road_lab.cvat_project $(ARGS)

# make lint FILES="an-front.zip an-fisheye.zip"
lint:
	$(PY) -m road_lab.road_check lint $(FILES)
