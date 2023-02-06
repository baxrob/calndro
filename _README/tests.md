
### Tests

See [schedul/tests.py](schedul/test.py)

There are feature tests with branch coverage.
- I don't like the number of utility functions
- Some auth tests are excessive or redundant
- I need to stipulate assumptions built into the fixture structure

```
overly parameterized

core axials ?
log authn/z pii disposabil

helper funcs .. pytest
integration / functional / feature: views, auth, dispatch, queries
..unit: token, mail

action : result : match condition
stitching together axiomatic view
thinking toward
formal verification
nice of self-doc typed api tools

list_tests.sh

tooling : py dj drf
```

```
todos:
-----
%[testdo]

add:
mail tests
env tests
docker tests

refactor:
fixture axiomatics
pytest
```

#### CI

Basic github workflow running Python 3.8 - 3.10. See [.github/workflows/ci.yml](.github/workflows/ci.yml)

Using ```Act``` frequently, an offline github workflow runner: https://github.com/nektos/act

#### Coverage
```
%[coverage]

https://github.com/nedbat/coveragepy
```
<!--
https://coverage.readthedocs.io/en/6.3.2/
-->

