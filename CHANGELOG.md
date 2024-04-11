# CHANGELOG



## v0.3.9 (2024-04-11)

### Fix

* fix: update tests and added raise ValueError for 401 responses ([`6956095`](https://github.com/MountainGod2/chaturbate_poller/commit/6956095c2997d2a9dc1ffafdd598b8c45967f4f0))


## v0.3.8 (2024-04-11)

### Fix

* fix: changed URL default and added argument to allow the use of the testbed URL for development ([`17b074d`](https://github.com/MountainGod2/chaturbate_poller/commit/17b074d1925b93d76170122f67135bb2b6590d58))


## v0.3.7 (2024-04-11)

### Fix

* fix: modified http error codes to use an enum ([`d67e3ce`](https://github.com/MountainGod2/chaturbate_poller/commit/d67e3ced6c80259901e4f9098099a4157d9cd7be))

### Test

* test: added formatting tests into test_chaturbate_poller.py ([`4dd6206`](https://github.com/MountainGod2/chaturbate_poller/commit/4dd6206773d229aee54fe8b9908f1948541fc1a5))


## v0.3.6 (2024-04-10)

### Fix

* fix: correct typing and format code ([`9cd7688`](https://github.com/MountainGod2/chaturbate_poller/commit/9cd768811402c9a428541b661708eb904071201f))

### Test

* test: refactored test_format_message.py ([`4bca906`](https://github.com/MountainGod2/chaturbate_poller/commit/4bca9064657fae333e7a81a881e978a594f7e281))


## v0.3.5 (2024-04-10)

### Fix

* fix: added format_messages.py and updated tests ([`e57fa63`](https://github.com/MountainGod2/chaturbate_poller/commit/e57fa63c7bd7929f3a4d54970cabb9dda915650b))


## v0.3.4 (2024-04-09)

### Fix

* fix: rename files and add logs to .gitignore ([`43ed001`](https://github.com/MountainGod2/chaturbate_poller/commit/43ed001ce0e73d14ce05a2476e5084b232347b1e))


## v0.3.3 (2024-04-09)

### Fix

* fix: refactored models and added test coverage ([`aa69183`](https://github.com/MountainGod2/chaturbate_poller/commit/aa691832303cadeef6cc1ea650c7e23ebecb2014))


## v0.3.2 (2024-04-08)

### Fix

* fix: update examples and refactor logging ([`47f9208`](https://github.com/MountainGod2/chaturbate_poller/commit/47f92086978ed0344c5d3c3cd70652755b90a8be))


## v0.3.1 (2024-04-07)

### Fix

* fix: refactor package and update README.md ([`bea835a`](https://github.com/MountainGod2/chaturbate_poller/commit/bea835a387df9775b5274cdacba7f00a14e48c2f))


## v0.3.0 (2024-04-07)

### Feature

* feat: refactored modules and updated docstrings ([`17a3a8b`](https://github.com/MountainGod2/chaturbate_poller/commit/17a3a8bb35082da36df87cc1f1031115e9b6f320))

### Test

* test: adjust timeout for test_main.py ([`0a3ac67`](https://github.com/MountainGod2/chaturbate_poller/commit/0a3ac673780d7157159121e0917d6970c115078c))


## v0.2.0 (2024-04-04)

### Feature

* feat: refactor chaturbate_poller.py and tests ([`99ebad1`](https://github.com/MountainGod2/chaturbate_poller/commit/99ebad18244d69ad6deb1ab436f06be6df369ce9))

### Test

* test: refactor test_chaturbate_poller.py ([`12001bd`](https://github.com/MountainGod2/chaturbate_poller/commit/12001bd1b41d2e3a7a9443e1660f5292d9531a49))

* test: added additional tests to test_main.py ([`11dafde`](https://github.com/MountainGod2/chaturbate_poller/commit/11dafde7c0b4ef2afe7a11b4b46e1c205f3dd70b))


## v0.1.4 (2024-04-03)

### Fix

* fix: fixed tests and updated workflows ([`0793ff6`](https://github.com/MountainGod2/chaturbate_poller/commit/0793ff686397032f99d7e3155db84003098c488f))

### Test

* test: added user env&#39;s to ci-cd.yml test ([`4fa745c`](https://github.com/MountainGod2/chaturbate_poller/commit/4fa745c2581e393e2b815962a72fc007f33827ef))

* test: updated ci-cd.yml ([`b0dad36`](https://github.com/MountainGod2/chaturbate_poller/commit/b0dad362fcd21d99bca607b4a90783be31497018))

* test: update test_main.py ([`6252a3a`](https://github.com/MountainGod2/chaturbate_poller/commit/6252a3a76310fa947cb9fbe4e1e3dd81b7e59b7a))

* test: update ci-cd.yml ([`bb2850b`](https://github.com/MountainGod2/chaturbate_poller/commit/bb2850b8e38d035c52f70a2037bf57fd1433d658))

* test: update ci-cd.yml ([`2882e5e`](https://github.com/MountainGod2/chaturbate_poller/commit/2882e5e8d6e09440833c19b734aa089fc657be9d))

* test: update ci-cd.yml ([`94c4f65`](https://github.com/MountainGod2/chaturbate_poller/commit/94c4f652da65855e837492fa13c1f1c66bd864f1))

* test: update test_main.py ([`c9b932a`](https://github.com/MountainGod2/chaturbate_poller/commit/c9b932a7c3fec214ff197dbf60a960627050cdbb))


## v0.1.3 (2024-04-02)

### Build

* build: update ci-cd.yml ([`77c3f93`](https://github.com/MountainGod2/chaturbate_poller/commit/77c3f93d83c7e2928b704ba65b2013cf15715bd8))

* build: added poetry to dev group dependencies and update poetry.lock ([`92cb07f`](https://github.com/MountainGod2/chaturbate_poller/commit/92cb07f179858d6437304aacc3a1f859ce0aa6f3))

* build: moved codeql.yml to it&#39;s own file ([`c967b3e`](https://github.com/MountainGod2/chaturbate_poller/commit/c967b3e5104c1adf2dbb162c6bd956def153301e))

* build: added dependabot.yml ([`d33aca9`](https://github.com/MountainGod2/chaturbate_poller/commit/d33aca9b40d097f3e12c4b70ec2880c5669222b3))

* build: added CodeQL to ci-cd.yml ([`a63da4c`](https://github.com/MountainGod2/chaturbate_poller/commit/a63da4ce25575c81978a02fd692ab93aa337d8cd))

### Documentation

* docs: added SECURITY.md ([`2a2785d`](https://github.com/MountainGod2/chaturbate_poller/commit/2a2785d60928caa4fbeed139c910a4d05e977f66))

### Fix

* fix: correct test_main.py python path ([`be8b38f`](https://github.com/MountainGod2/chaturbate_poller/commit/be8b38f8846b3fcdb8ee7a3b62a70a9f65757fb5))

### Test

* test: update ci-cd.yml and test_main.py ([`54254c2`](https://github.com/MountainGod2/chaturbate_poller/commit/54254c25b546d6a947a0ef915c2b6b6d9478af26))

* test: adjust test_main.py ([`2bd6647`](https://github.com/MountainGod2/chaturbate_poller/commit/2bd6647b9ebd5dd552e6493af123b79f0f73ce35))

* test: another attempt at fixing the pytest path in ci-cd.yml ([`ec55a22`](https://github.com/MountainGod2/chaturbate_poller/commit/ec55a229f6e90957844bc04977cd2a97ab343890))

* test: fix ruff exceptions after formatting causing ci to fail ([`8d86d5f`](https://github.com/MountainGod2/chaturbate_poller/commit/8d86d5f01590dce490947bdd166e33697e40180d))

* test: fix ruff exceptions ([`172e7db`](https://github.com/MountainGod2/chaturbate_poller/commit/172e7dbcd481f350cd54965ee9a9ae72d7dc28f1))

* test: try to fix test_main.py and ci-cd.yml testing ([`6cff5b4`](https://github.com/MountainGod2/chaturbate_poller/commit/6cff5b4ca07da3be2e46a30f1f07866dff193ed9))

* test: added additional coverage for test_main.py ([`9f0e075`](https://github.com/MountainGod2/chaturbate_poller/commit/9f0e075266d4cc581442a820a26ba8832c08f05f))

* test: fix python path in test_main.py causing ci to fail ([`155cce0`](https://github.com/MountainGod2/chaturbate_poller/commit/155cce072db2a99218923239ef32395cda9ae8bf))

* test: added additional coverage for test_main.py ([`9b2a0da`](https://github.com/MountainGod2/chaturbate_poller/commit/9b2a0da66152d4306fc9b44d0f7f21f08ac2473e))


## v0.1.2 (2024-04-01)

### Fix

* fix: update links to repository and docs in pyproject.toml ([`3003d16`](https://github.com/MountainGod2/chaturbate_poller/commit/3003d16c9be5d1c25f30e91c1b2a0912475a904e))


## v0.1.1 (2024-04-01)

### Build

* build: fix ruff actions ([`fbaf8e7`](https://github.com/MountainGod2/chaturbate_poller/commit/fbaf8e7bd3fa58dff2a5157b9005442d080bd7be))

* build: update ci-cd.yml to include ruff formatting and linting ([`c44acdf`](https://github.com/MountainGod2/chaturbate_poller/commit/c44acdf132220b3668abf81d4a5468720049ec31))

### Fix

* fix: update imports in chaturbate_poller.py ([`ade470f`](https://github.com/MountainGod2/chaturbate_poller/commit/ade470f0c2a89361b1fdd32d2ba5a7ee232c6757))

### Test

* test: update test_chaturbate_poller.py ([`1cc1855`](https://github.com/MountainGod2/chaturbate_poller/commit/1cc1855d263b6165d568ed6fe38364fe0db925c7))


## v0.1.0 (2024-03-31)

### Build

* build: updated documation build action in ci-cd.yml to ensure all files are updated ([`9d679ed`](https://github.com/MountainGod2/chaturbate_poller/commit/9d679ede55fce85d8b2254e88695c4a824cf9335))

### Documentation

* docs: update README.md ([`3f7241f`](https://github.com/MountainGod2/chaturbate_poller/commit/3f7241fb5dfcd0ed15cbc9e10fb67979bd484f80))

### Feature

* feat: add codecov to ci-cd.yml ([`9973692`](https://github.com/MountainGod2/chaturbate_poller/commit/9973692f6cea70ea1e64b18a9e3b7cbfa59a4f8a))


## v0.0.1 (2024-03-31)

### Fix

* fix: add python-semantic-release to requirements ([`1c67a65`](https://github.com/MountainGod2/chaturbate_poller/commit/1c67a658b414202372a01c18cda21c0262622a68))


## v0.0.0 (2024-03-31)

### Unknown

* first commit ([`49a9bf2`](https://github.com/MountainGod2/chaturbate_poller/commit/49a9bf2f34f22bbc842dfb000e97e8249490b4fa))
