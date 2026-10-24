"""Direct test runner (no pytest, no tempfile): imports every tests/test_*.py
module, runs unittest TestCases plus zero-arg test_* functions, and reports
counts. Fixture-dependent functions (params) are skipped and counted.
Written to verify Wave 22's suite when the VM temp-dir guard blocks pytest.
"""
import importlib.util
import inspect
import os
import sys
import traceback
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TESTS = os.path.join(ROOT, "tests")
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, TESTS)

passed = failed = skipped = 0
failures = []

for fname in sorted(os.listdir(TESTS)):
    if not fname.startswith("test_") or not fname.endswith(".py"):
        continue
    mod_name = fname[:-3]
    spec = importlib.util.spec_from_file_location(mod_name, os.path.join(TESTS, fname))
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception:
        failed += 1
        failures.append((fname, "<import>", traceback.format_exc(limit=3)))
        continue
    # unittest TestCases
    suite = unittest.TestLoader().loadTestsFromModule(mod)
    if suite.countTestCases():
        res = unittest.TextTestRunner(stream=open(os.devnull, "w"), verbosity=0).run(suite)
        passed += res.testsRun - len(res.failures) - len(res.errors)
        for t, tb in res.failures + res.errors:
            failed += 1
            failures.append((fname, str(t), tb[-500:]))
    # pytest-style plain classes (name starts with Test, not a TestCase):
    # instantiate and call their zero-arg test_* methods
    for cls_name, cls in vars(mod).items():
        if not (cls_name.startswith("Test") and inspect.isclass(cls)):
            continue
        if issubclass(cls, unittest.TestCase):
            continue
        try:
            obj = cls()
        except Exception:
            continue
        for name in dir(obj):
            if not name.startswith("test_"):
                continue
            fn = getattr(obj, name)
            if not callable(fn):
                continue
            try:
                sig = inspect.signature(fn)
            except (TypeError, ValueError):
                continue
            params = [p for p in sig.parameters.values()
                      if p.default is inspect.Parameter.empty
                      and p.kind in (inspect.Parameter.POSITIONAL_ONLY,
                                     inspect.Parameter.POSITIONAL_OR_KEYWORD)]
            if params:
                skipped += 1
                continue
            try:
                fn()
                passed += 1
            except Exception:
                failed += 1
                failures.append((fname, cls_name + "::" + name, traceback.format_exc(limit=3)))
    # plain zero-arg test_* functions (pytest-style, no fixtures)
    for name, fn in vars(mod).items():
        if name.startswith("test_") and callable(fn) and not inspect.isclass(fn):
            try:
                sig = inspect.signature(fn)
            except (TypeError, ValueError):
                continue
            params = [p for p in sig.parameters.values()
                      if p.default is inspect.Parameter.empty
                      and p.kind in (inspect.Parameter.POSITIONAL_ONLY,
                                     inspect.Parameter.POSITIONAL_OR_KEYWORD)]
            if params:
                skipped += 1
                continue
            try:
                fn()
                passed += 1
            except Exception:
                failed += 1
                failures.append((fname, name, traceback.format_exc(limit=3)))

print("DIRECT-RUN: passed=%d failed=%d skipped_fixture_dependent=%d" % (passed, failed, skipped))
for fname, name, tb in failures[:20]:
    print("FAIL %s::%s\n%s" % (fname, name, tb))
