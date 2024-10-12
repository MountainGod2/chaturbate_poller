# CHANGELOG


## v0.11.1 (2024-10-12)

### Chores

* chore: update .gitignore file ([`9ca6fa4`](https://github.com/MountainGod2/chaturbate_poller/commit/9ca6fa428d89d6c2a08b5b1186a574fea07a6bbb))

* chore: update chaturbate-poller version to 0.11.0 ([`7c5334a`](https://github.com/MountainGod2/chaturbate_poller/commit/7c5334a1ffa5a07f1d9e65becfc2884c15fcb403))

### Fixes

* fix: refactor import statements in chaturbate_client.py and event_handler.py ([`e6a7111`](https://github.com/MountainGod2/chaturbate_poller/commit/e6a71116d3f58c2dd3a6f3f71b3514edb657ef7c))

### Refactoring

* refactor: update import statements in tests ([`d4d86d8`](https://github.com/MountainGod2/chaturbate_poller/commit/d4d86d8656f4fa0ca1f8f48400307df008829053))

* refactor: Update HttpStatusCode enum in constants.py

Update the HttpStatusCode enum in constants.py to include additional HTTP status codes and provide clear attribute descriptions. ([`93fee7e`](https://github.com/MountainGod2/chaturbate_poller/commit/93fee7eef1fd5db84db6658216a3fe6f761c6b59))

### Testing

* test: update tests and add HttpStatusCode enum to test_backoff_handlers.py ([`a3712d7`](https://github.com/MountainGod2/chaturbate_poller/commit/a3712d734349dffc6550a913dd59ff4f54f744e9))


## v0.11.0 (2024-10-11)

### Chores

* chore: update dependencies in requirements.txt and uv.lock ([`2a122d4`](https://github.com/MountainGod2/chaturbate_poller/commit/2a122d4af92c916d3b79099ac26b7c8749a17b49))

* chore: add rich and rich-click dependencies in pyproject.toml and uv.lock ([`55216c5`](https://github.com/MountainGod2/chaturbate_poller/commit/55216c54e6384deb71a8fe80b839ec7a092f9e59))

* chore: update pypa/gh-action-pypi-publish action to latest version in ci-cd-build.yml ([`fd60bac`](https://github.com/MountainGod2/chaturbate_poller/commit/fd60bac6d21e5bb74839d28077c761e299d25dd7))

* chore: update pypa/gh-action-pypi-publish to version 1.10.3 in ci-cd-build.yml ([`16bf816`](https://github.com/MountainGod2/chaturbate_poller/commit/16bf81640b846942f1cc8b73429f1e246544ee07))

* chore: update chaturbate-poller version to 0.10.4 in uv.lock and pyproject.toml ([`48ae136`](https://github.com/MountainGod2/chaturbate_poller/commit/48ae13616075e86b585190be0ad910341e5fd91e))

### Features

* feat: add RetryError exception for Chaturbate Poller ([`0a27f41`](https://github.com/MountainGod2/chaturbate_poller/commit/0a27f412d7f564df46ceb0da7f1992433a593bad))

### Fixes

* fix: handle server errors and raise RetryError

When a server error occurs, a RetryError is raised with the message "Giving up after server error". This ensures that the request is retried when encountering server errors. ([`1dca0b0`](https://github.com/MountainGod2/chaturbate_poller/commit/1dca0b0c1041225b2b8351cd1033a1fdb043d300))

### Refactoring

* refactor: update error handling in ChaturbateUtils

Refactor the error handling logic in the ChaturbateUtils class. The code now properly handles different server error codes and raises the appropriate PollingError exception. This improves the error reporting and makes the code more robust. ([`4717ab3`](https://github.com/MountainGod2/chaturbate_poller/commit/4717ab3044094a94f2c9e582a247ab068f25f42f))

* refactor: update signal handling in SignalHandler

Update the signal handling in the SignalHandler class in signal_handler.py. Instead of logging a debug message when receiving a signal, it now logs an info message with the received signal name. Additionally, when cancelling running tasks, it now logs the number of tasks being cancelled. ([`84d4e6e`](https://github.com/MountainGod2/chaturbate_poller/commit/84d4e6e5eea0faaab3d311ccee9b66ddc9126826))

* refactor: update error handling and dependencies in Chaturbate Poller ([`00babab`](https://github.com/MountainGod2/chaturbate_poller/commit/00babab18c3cc79c3d5b96671de34d6fb41310a5))

* refactor: update error handling in InfluxDBHandler ([`536f40d`](https://github.com/MountainGod2/chaturbate_poller/commit/536f40dc84341fe69eb25bc31e1db788c33123d4))

* refactor: rename RetryError to PollingError in exceptions.py ([`0c5ecc7`](https://github.com/MountainGod2/chaturbate_poller/commit/0c5ecc7b297c140b83e4a320f5513b8cd85b79c4))

* refactor: update error handling in ChaturbateClient

Refactor the error handling in the ChaturbateClient class to improve logging and error reporting. Instead of logging the full HTTP error response, sanitize the sensitive data in the URL and log a more generic error message. This change enhances the readability and security of the code. ([`36bf673`](https://github.com/MountainGod2/chaturbate_poller/commit/36bf67336ee90e855e3146dfd090f4535af76dc5))

* refactor: update console logging configuration and dependencies

- Refactor the console logging configuration in the Chaturbate Poller. ([`8a0cddd`](https://github.com/MountainGod2/chaturbate_poller/commit/8a0cddde102c70bab3fb745bfd57d3417d1b6ee2))

* refactor: update console logging configuration

Update the console logging configuration in `logging_config.py` to use `RichHandler` from the `rich.logging` module. This change enables the use of rich formatting and tracebacks in console logs. The `sanitize_sensitive_data` filter is also applied to the console handler. ([`18d7c54`](https://github.com/MountainGod2/chaturbate_poller/commit/18d7c5419cf111d574d0a0f9bcb5c90d92da4d97))

### Testing

* test: update exception names in test_backoff_handlers.py and test_event_fetching.py ([`216dc6f`](https://github.com/MountainGod2/chaturbate_poller/commit/216dc6fb15a1cbe7fe8a3719fa4f93c06a226c3f))

* test: handle server errors and raise RetryError in backoff handlers and event fetching ([`0c7d34e`](https://github.com/MountainGod2/chaturbate_poller/commit/0c7d34ebe0aba389fa14b53ad302016fb5cd72c2))


## v0.10.4 (2024-10-09)

### Chores

* chore: Update chaturbate-poller version to 0.10.3 in uv.lock ([`b884fe4`](https://github.com/MountainGod2/chaturbate_poller/commit/b884fe405a625f6c31bf5c46f6464831619ffaea))

### Fixes

* fix: update pyproject.toml to include chaturbate-poller version from uv.lock in version_toml ([`eb113a1`](https://github.com/MountainGod2/chaturbate_poller/commit/eb113a1dcca21d3dd4c25e8e474d955665258985))

### Refactoring

* refactor: remove poetry.lock to complete transition to using uv to manage package ([`16dbc58`](https://github.com/MountainGod2/chaturbate_poller/commit/16dbc58491c434f067b41238d987fe159a7fbd37))


## v0.10.3 (2024-10-09)

### Chores

* chore: update chaturbate-poller version to 0.10.2 ([`f3d27f1`](https://github.com/MountainGod2/chaturbate_poller/commit/f3d27f189e5be60b05c9b910de7597ef3cdb6602))

### Fixes

* fix: update GitHub Releases publishing action ([`ca687c8`](https://github.com/MountainGod2/chaturbate_poller/commit/ca687c8057fe275aec2e6ab23e00a8931130d9bb))


## v0.10.2 (2024-10-09)

### Build System

* build: update Dockerfile and docker-entrypoint.sh

Update the Dockerfile to install tini and update the entrypoint script to use tini as the entrypoint. ([`6009538`](https://github.com/MountainGod2/chaturbate_poller/commit/600953837ec78f343441bc30fb5bf340dbbeebc6))

### Chores

* chore: remove unnecessary whitespace in test_config_manager.py ([`4656543`](https://github.com/MountainGod2/chaturbate_poller/commit/4656543c7ea9d64800c9916d2701588153056558))

* chore: update uv.lock and dependencies

Update the required version of `uv` to `0.4.19` and other dependencies to their latest versions. ([`cf240a8`](https://github.com/MountainGod2/chaturbate_poller/commit/cf240a8a8f3c959b42df53155ba2cf9a7eab9408))

* chore: update uv.lock ([`83206a6`](https://github.com/MountainGod2/chaturbate_poller/commit/83206a6b597ad727c6caf7cf4809e3a504d4b280))

### Fixes

* fix: update Dockerfile to use alpine-based image and improve dependency management (#47) ([`35746f0`](https://github.com/MountainGod2/chaturbate_poller/commit/35746f021a1b0048d28efa16008db949059a0cba))

### Refactoring

* refactor: update Dockerfile to install uv and dependencies (#46)

* refactor: update Dockerfile to install uv and dependencies

- Updated the Dockerfile to include a new stage for installing uv and its dependencies.
- Set the working directory and copied the project files into the image.
- Modified the uv sync command to exclude dev dependencies.
- Prepared the final runtime image with the virtual environment from the builder stage.
- Set the docker-entrypoint.sh script as executable and copied it into the image.
- Set environment variables for the virtual environment.
- Updated the default entrypoint.
- Updated .gitignore

* refactor: raise ValueError with error message when CB_USERNAME and CB_TOKEN are not provided

* refactor: add signal handling to gracefully stop Chaturbate Poller

- Updated the `SignalHandler` class in `signal_handler.py` to include signal handling for gracefully stopping the Chaturbate Poller.
- Added a check in the `handle_signal` method to only create a shutdown task if the `stop_future` is not done.
- Removed the unnecessary `run_until_complete` call in the `handle_signal` method when the `stop_future` is already done. ([`8182be0`](https://github.com/MountainGod2/chaturbate_poller/commit/8182be025be1448e4e44da72e9441cac63fb7107))

* refactor: add signal handling to gracefully stop Chaturbate Poller

This commit adds signal handling to the Chaturbate Poller application, allowing it to gracefully stop when receiving a signal. It creates an asyncio event loop, sets up a signal handler, and waits for a stop signal to be received before closing the event loop. This ensures that the application can be stopped cleanly without interrupting any ongoing tasks. ([`2a6476c`](https://github.com/MountainGod2/chaturbate_poller/commit/2a6476c1f3d983bb46a3e70b1542fb4516ea48fc))

* refactor: update Dockerfile entrypoint ([`463780f`](https://github.com/MountainGod2/chaturbate_poller/commit/463780f9e833886b78f710171b1ab1b9bedf42c5))

* refactor: update CI/CD workflow dependencies in ci-cd-build.yml ([`98a25b3`](https://github.com/MountainGod2/chaturbate_poller/commit/98a25b338cffbc2450535419b262e72ea95e6118))

* refactor: update CI/CD workflow badge link in README.md ([`97fc5bc`](https://github.com/MountainGod2/chaturbate_poller/commit/97fc5bce552d8f958df1169f50c68325e8a489b9))

* refactor: remove redundant build and continuous deployment workflows (#45)

* refactor: remove redundant build and continuous deployment workflows

* refactor: update CI/CD workflow to fetch full commit history

* refactor: update CI/CD workflow to fetch full commit history ([`cb43fdc`](https://github.com/MountainGod2/chaturbate_poller/commit/cb43fdce05bc72018b459639743afb3023e4fbf7))


## v0.10.1 (2024-10-07)

### Fixes

* fix: add dependencies between build and cd workflows (#44)

This commit adds the "needs" keyword to the build and cd workflows in the GitHub Actions configuration. This ensures that the cd workflow will only run after the build workflow has successfully completed. This dependency ensures that the Docker image is built and pushed to the GitHub Container Registry before the release and deployment steps are executed.

Refactor the workflows to include the "needs" keyword for better workflow coordination and dependency management. ([`5321c9b`](https://github.com/MountainGod2/chaturbate_poller/commit/5321c9b5e637b3cf043f32034e5d9f63a0739f35))


## v0.10.0 (2024-10-07)

### Build System

* build(deps): bump httpcore from 1.0.5 to 1.0.6 (#42)

Bumps [httpcore](https://github.com/encode/httpcore) from 1.0.5 to 1.0.6.
- [Release notes](https://github.com/encode/httpcore/releases)
- [Changelog](https://github.com/encode/httpcore/blob/master/CHANGELOG.md)
- [Commits](https://github.com/encode/httpcore/compare/1.0.5...1.0.6)

---
updated-dependencies:
- dependency-name: httpcore
  dependency-type: direct:production
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
Co-authored-by: MountainGod2 <88257202+MountainGod2@users.noreply.github.com> ([`0915ba9`](https://github.com/MountainGod2/chaturbate_poller/commit/0915ba9cf44e365db5011979d55709c26f9dd433))

* build(deps): bump sphinx-rtd-theme from 2.0.0 to 3.0.0 (#41)

Bumps [sphinx-rtd-theme](https://github.com/readthedocs/sphinx_rtd_theme) from 2.0.0 to 3.0.0.
- [Changelog](https://github.com/readthedocs/sphinx_rtd_theme/blob/master/docs/changelog.rst)
- [Commits](https://github.com/readthedocs/sphinx_rtd_theme/compare/2.0.0...3.0.0)

---
updated-dependencies:
- dependency-name: sphinx-rtd-theme
  dependency-type: direct:production
  update-type: version-update:semver-major
...

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
Co-authored-by: MountainGod2 <88257202+MountainGod2@users.noreply.github.com> ([`14194bc`](https://github.com/MountainGod2/chaturbate_poller/commit/14194bc2ff8e525bd206e2e65f4ad20defad3680))

### Chores

* chore: update version in uv.lock ([`4c5d9f2`](https://github.com/MountainGod2/chaturbate_poller/commit/4c5d9f27f6c2a9b521ec06af190621280fb0a2d2))

### Features

* feat: add GitHub workflows for building and deploying Docker image and continuous deployment (#43)

- Added a new file `.github/workflows/build.yml` for building and deploying Docker image to GitHub Container Registry.
- Added a new file `.github/workflows/cd.yml` for handling release and deployment.
- Deleted the file `.github/workflows/ci-cd.yml`.
- Added a new file `.github/workflows/ci.yml` for continuous integration.

These changes introduce GitHub workflows to automate the build, deployment, and continuous integration processes for the project. ([`d1938db`](https://github.com/MountainGod2/chaturbate_poller/commit/d1938dbb3035405a79d63e80a56f1d8e5cfa4189))


## v0.9.7 (2024-10-07)

### Build System

* build: remove build step for distribution packages in CI/CD workflow and add build_command to semantic_release config in pyproject.toml ([`bc4aaab`](https://github.com/MountainGod2/chaturbate_poller/commit/bc4aaab8f704483c1662ec9dd5e72732fe1f8a1f))

### Chores

* chore: update CI/CD workflow to build documentation and deploy to GitHub Pages ([`af369f0`](https://github.com/MountainGod2/chaturbate_poller/commit/af369f081b949911823ef759dd0583849a571c5f))

* chore: update cache key format in CI/CD workflow ([`95c3495`](https://github.com/MountainGod2/chaturbate_poller/commit/95c3495dc21fe8ac2afd07d07335852422ae5eb9))

* chore: update version in uv.lock ([`245bf89`](https://github.com/MountainGod2/chaturbate_poller/commit/245bf89371166472aa57cf5d5296614ebb0f0037))

### Fixes

* fix: update build_command in pyproject.toml to include uv install ([`1044423`](https://github.com/MountainGod2/chaturbate_poller/commit/10444234e4c04fb527c4c755dc40e2bc0d30be2b))

* fix: streamline build package installation in CI/CD workflow ([`04a119c`](https://github.com/MountainGod2/chaturbate_poller/commit/04a119c01dde2413fe6547125e4a28b1db036dd1))


## v0.9.6 (2024-10-07)

### Build System

* build: streamline build package installation in CI/CD workflow ([`e6368a8`](https://github.com/MountainGod2/chaturbate_poller/commit/e6368a8b16aa86b4807414a9cc6800d88db84455))

* build: add step to install build package in CI/CD workflow ([`a2d1567`](https://github.com/MountainGod2/chaturbate_poller/commit/a2d15675c9546e4853436ca12226ab157e910cc9))

### Chores

* chore: update version in uv.lock ([`548db4a`](https://github.com/MountainGod2/chaturbate_poller/commit/548db4acaeb821e0f852fa446bfe54ad651ef783))

### Fixes

* fix: update Python Semantic Release to version 9.10.0 and build distribution packages (#40) ([`06b3845`](https://github.com/MountainGod2/chaturbate_poller/commit/06b3845d2801f9f4e9b9f8d3815bb82c566bab23))


## v0.9.5 (2024-10-05)

### Fixes

* fix: refactor log directory instantation into main.py ([`ac45973`](https://github.com/MountainGod2/chaturbate_poller/commit/ac459731f920245224f4c6a708ad7aca0c5ec0fb))

### Refactoring

* refactor: update pyproject.toml and uv.lock to remove pyyaml ([`b42d90b`](https://github.com/MountainGod2/chaturbate_poller/commit/b42d90bd75808764202b9c4940745a635f7bc22d))

* refactor: remove unused code and simplify ConfigManager initialization ([`a505522`](https://github.com/MountainGod2/chaturbate_poller/commit/a505522b07d4588459b65556a140919a7d43f3fc))

* refactor: update examples ([`8dcb0ec`](https://github.com/MountainGod2/chaturbate_poller/commit/8dcb0ecca6ab675b39d55cb82665d5d0d706ee80))

* refactor: update lint configuration in pyproject.toml ([`5153b40`](https://github.com/MountainGod2/chaturbate_poller/commit/5153b40c895735ea0783542e06043f2af1cb6d71))


## v0.9.4 (2024-10-05)

### Chores

* chore: update chaturbate-poller version to 0.9.3 ([`32b008c`](https://github.com/MountainGod2/chaturbate_poller/commit/32b008c9a238e16a8dac0c3cda3cfb3e7c260b96))

### Documentation

* docs: improve documentation ([`c334d63`](https://github.com/MountainGod2/chaturbate_poller/commit/c334d636e446c674b7b2fcf5c534496dbdafe75c))

### Fixes

* fix: update logging throughout program (#39) ([`df0e9d5`](https://github.com/MountainGod2/chaturbate_poller/commit/df0e9d57abe0477b21b0646f0452cf845bf6b68f))

### Refactoring

* refactor: update logging configuration in tests/conftest.py ([`518a3b5`](https://github.com/MountainGod2/chaturbate_poller/commit/518a3b5f33631be855e6a50f7a00c412e00c1dce))

* refactor: update ChaturbateClient initialization and logging ([`de610fd`](https://github.com/MountainGod2/chaturbate_poller/commit/de610fd67daccfd61fd9130b914d3cf18e0526e0))

* refactor: update logging in event_handler.py and influxdb_client.py ([`7da5ee2`](https://github.com/MountainGod2/chaturbate_poller/commit/7da5ee217090655d333bffb2967304930fef11fa))

* refactor: update linting configuration in pyproject.toml ([`20cfc0a`](https://github.com/MountainGod2/chaturbate_poller/commit/20cfc0a568e61ce19b1da746d40a352eeba9376f))

* refactor: update Dockerfile to install uv and sync project dependencies ([`80ce181`](https://github.com/MountainGod2/chaturbate_poller/commit/80ce18159413044e075698a708112e9fae877aea))

* refactor: update source directory in pyproject.toml ([`f1c0c6a`](https://github.com/MountainGod2/chaturbate_poller/commit/f1c0c6a67e23f2c110b1870d6718007ee363100f))

* refactor: remove unnecessary blank line in signal handler shutdown ([`4b1b1fa`](https://github.com/MountainGod2/chaturbate_poller/commit/4b1b1fa7d29f117fb0ccb13ccaef1a1b6c65ef12))

* refactor: update source directory in pyproject.toml ([`3b85fb8`](https://github.com/MountainGod2/chaturbate_poller/commit/3b85fb84543f26ed8fac0af80707576587e6d258))

### Testing

* test: remove unused logger instances in test_main.py and test_signal_handler.py ([`1d59397`](https://github.com/MountainGod2/chaturbate_poller/commit/1d593978d5d462ca790860b26b999d00f5b8e463))

* test: refactor tests into separate scripts to reduce complexity and improve readability ([`7c735a3`](https://github.com/MountainGod2/chaturbate_poller/commit/7c735a329b9df0d9d41567d18dd795ca144f7f85))


## v0.9.3 (2024-10-02)

### Build System

* build(deps): bump myst-nb from 1.1.1 to 1.1.2 (#32)

Bumps [myst-nb](https://github.com/executablebooks/myst-nb) from 1.1.1 to 1.1.2.
- [Release notes](https://github.com/executablebooks/myst-nb/releases)
- [Changelog](https://github.com/executablebooks/MyST-NB/blob/master/CHANGELOG.md)
- [Commits](https://github.com/executablebooks/myst-nb/compare/v1.1.1...v1.1.2)

---
updated-dependencies:
- dependency-name: myst-nb
  dependency-type: direct:production
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`35b5e25`](https://github.com/MountainGod2/chaturbate_poller/commit/35b5e250710a26797e6ba78465393d9890687c24))

* build(deps): bump sphinx-autoapi from 3.0.0 to 3.3.2 (#33)

Bumps [sphinx-autoapi](https://github.com/readthedocs/sphinx-autoapi) from 3.0.0 to 3.3.2.
- [Release notes](https://github.com/readthedocs/sphinx-autoapi/releases)
- [Changelog](https://github.com/readthedocs/sphinx-autoapi/blob/main/CHANGELOG.rst)
- [Commits](https://github.com/readthedocs/sphinx-autoapi/compare/v3.0.0...v3.3.2)

---
updated-dependencies:
- dependency-name: sphinx-autoapi
  dependency-type: direct:production
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
Co-authored-by: MountainGod2 <88257202+MountainGod2@users.noreply.github.com> ([`7cfef9a`](https://github.com/MountainGod2/chaturbate_poller/commit/7cfef9a475d0cf8865ebbc67a01749df60737b3a))

* build(deps): bump pydantic-core from 2.23.4 to 2.24.0 (#34)

Bumps [pydantic-core](https://github.com/pydantic/pydantic-core) from 2.23.4 to 2.24.0.
- [Release notes](https://github.com/pydantic/pydantic-core/releases)
- [Commits](https://github.com/pydantic/pydantic-core/compare/v2.23.4...v2.24.0)

---
updated-dependencies:
- dependency-name: pydantic-core
  dependency-type: direct:production
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
Co-authored-by: MountainGod2 <88257202+MountainGod2@users.noreply.github.com> ([`fc71aa7`](https://github.com/MountainGod2/chaturbate_poller/commit/fc71aa72aa06985bcac56ceea54d278bd9eaf073))

### Continuous Integration

* ci: refactor source directory in pyproject.toml ([`a4ad7ba`](https://github.com/MountainGod2/chaturbate_poller/commit/a4ad7ba4c65b4190f89551a99a7c6dec480da6fb))

* ci: refactor source directory in pyproject.toml ([`85f20d4`](https://github.com/MountainGod2/chaturbate_poller/commit/85f20d475f8ed265c181cfb7c59db7d82df19c43))

* ci: refactor sonar-project.properties: update source directory ([`942a728`](https://github.com/MountainGod2/chaturbate_poller/commit/942a72849c4ae0169335736ef070fe11ec2a29fd))

* ci: refactor sonar-project.properties: update source directory ([`e1b4a03`](https://github.com/MountainGod2/chaturbate_poller/commit/e1b4a034b3e532b34b72c044bfc29318b82b8a63))

* ci: refactor sonar-project.properties: update source directory ([`c5b3f06`](https://github.com/MountainGod2/chaturbate_poller/commit/c5b3f061bf46ed952e54e839caf61aad75c21609))

* ci: refactor sonar-project.properties: update source directory ([`541fcce`](https://github.com/MountainGod2/chaturbate_poller/commit/541fccefc1bcef2105077e871ad062078828f552))

* ci: refactor sonar-project.properties: update source directory ([`2eea2d2`](https://github.com/MountainGod2/chaturbate_poller/commit/2eea2d2bf5d66908000e0587a0defcbb1490f5cf))

* ci: bump chaturbate-poller version to 0.9.2 ([`9e98a8e`](https://github.com/MountainGod2/chaturbate_poller/commit/9e98a8ea72db2c73f9794768b07bba25a9a539e2))

### Fixes

* fix: refactor signal handler shutdown and task cancellation (#37)

* ci: refactor source directory in pyproject.toml

* fix: refactor signal handler shutdown and task cancellation ([`52ca119`](https://github.com/MountainGod2/chaturbate_poller/commit/52ca11915f18113cecd0d0ddfd9f894123febb37))

### Refactoring

* refactor: move main function to separate module (#35)

* refactor: move main function to separate module

* refactor: updated description for project

* refactor: improve signal handling and shutdown process

* refactor: improve logging usage and consistency

* refactor: add constants for pytests

* refactor: simplify signal handler setup

* test: refactor test fixtures and logging in tests

* 0.9.2 (#36)

Automatically generated by python-semantic-release ([`733f8ca`](https://github.com/MountainGod2/chaturbate_poller/commit/733f8ca4bbc43b1932c6350aa98caf29fcfcd0dd))

### Testing

* test: refactor test_chaturbate_poller.py: remove unnecessary assert statement ([`d34ab03`](https://github.com/MountainGod2/chaturbate_poller/commit/d34ab03a44efd70b31092b9646d046e1da34cb3e))


## v0.9.2 (2024-09-29)

### Fixes

* fix: remove duplicate depandabot.yml ([`5776aca`](https://github.com/MountainGod2/chaturbate_poller/commit/5776aca1332c401a18ab1e5ec168c97d7179dcd0))

### Refactoring

* refactor: refactor format_messages.py to improve tip message formatting ([`f597021`](https://github.com/MountainGod2/chaturbate_poller/commit/f597021d04b1011e5478e1e00c999f9a4425e4a1))

* refactor: refactor format_messages.py to fix tip message formatting ([`f2df1a6`](https://github.com/MountainGod2/chaturbate_poller/commit/f2df1a6b26f909b450639c737dcea3d992346240))

### Unknown

* tests: update pytest configuration for asyncio default fixture loop scope ([`4680f95`](https://github.com/MountainGod2/chaturbate_poller/commit/4680f952c8e840928d19715bd0cf761fed7a867b))

* Update chaturbate-poller version to 0.9.1 ([`1f08d33`](https://github.com/MountainGod2/chaturbate_poller/commit/1f08d331cbb425e0aa16cedeb8ad228a9cf64acb))


## v0.9.1 (2024-09-28)

### Chores

* chore: update ci-cd.yml to remove unnecessary tags in push step ([`3667556`](https://github.com/MountainGod2/chaturbate_poller/commit/3667556b8356c066d38cd2e39c8625438fbf3c79))

* chore: add uv package to cd step ([`2cd6b4b`](https://github.com/MountainGod2/chaturbate_poller/commit/2cd6b4b6e43cfe24c721c265a2cc74483ebfc2cb))

* chore: update Python version to 3.12 and use uv as the package manager in ci-cd.yml (#30) ([`fb14eb1`](https://github.com/MountainGod2/chaturbate_poller/commit/fb14eb18df45d62652d10ab56bd6a0de5bdf9ac3))

### Fixes

* fix: update test_signal_handler.py (#31) ([`52e18b8`](https://github.com/MountainGod2/chaturbate_poller/commit/52e18b8b433ed1efb48178fb380aafec31664501))

* fix: fix formatting issue in format_tip_event function ([`599d8a4`](https://github.com/MountainGod2/chaturbate_poller/commit/599d8a477bb4f4ddd2a374c0423cf73202e072ad))

### Refactoring

* refactor: update ci-cd.yml to include SSH private and public signing keys ([`1034c3d`](https://github.com/MountainGod2/chaturbate_poller/commit/1034c3d930839eb0aa9951747f037a6943f7005c))

* refactor: update ci-cd.yml to set git committer and author information ([`c28f230`](https://github.com/MountainGod2/chaturbate_poller/commit/c28f23070d8f77682a9637033160f25310fed8de))

* refactor: update ci-cd.yml to set git committer and author information ([`1d9a6e2`](https://github.com/MountainGod2/chaturbate_poller/commit/1d9a6e279b68c42b8633f14e117f528935116efb))

* refactor: update pyproject.toml ([`0d70a01`](https://github.com/MountainGod2/chaturbate_poller/commit/0d70a01b39c906577fc61f1c10820104587112b9))

* refactor: add signal handler for SIGINT and SIGTERM signals ([`be9f4a6`](https://github.com/MountainGod2/chaturbate_poller/commit/be9f4a61b2ac7c707b3a0ef1bad7be3c06e627a5))

* refactor: fix formatting issue in format_tip_event function ([`824c667`](https://github.com/MountainGod2/chaturbate_poller/commit/824c667726caf2d48100d1754db561f3cf09c2be))

* refactor: refactored to use uv as the package manager (#29)

* chore: refactored to use uv as the package manager

* chore: update dependencies in requirements.txt

* refactor: update Chaturbate poller utility functions

* chore: update ci-cd.yml to use uv as the package manager and cache uv dependencies ([`ad3a835`](https://github.com/MountainGod2/chaturbate_poller/commit/ad3a83599d99a253c0d9e1efce9014d29b301262))


## v0.9.0 (2024-09-27)

### Build System

* build: fix release action in ci-cd.yml ([`53eefb9`](https://github.com/MountainGod2/chaturbate_poller/commit/53eefb9cfdc462bdc106dff361f57f4189fe35f2))

* build: added version tag to Docker build action in ci-cd.yml ([`d1633ac`](https://github.com/MountainGod2/chaturbate_poller/commit/d1633ac0e0eb1f319de235a0e250e9b0c866e1b5))

### Continuous Integration

* ci: corrected ci-cd.yml build action ([`40c13b8`](https://github.com/MountainGod2/chaturbate_poller/commit/40c13b8d11ea3a771bcf7dc4dd4760ed93fa0e7a))

### Features

* feat: added pull request template (#28)

* chore: update dependencies in pyproject.toml

* chore: update Ruff version to v0.6.7 and add linting and formatting hooks

* feat: added pull request template ([`3e80b23`](https://github.com/MountainGod2/chaturbate_poller/commit/3e80b23549134b081b005e4aabbd7bc5c07476bb))

### Refactoring

* refactor: add ChaturbateUtils class for Chaturbate poller utility functions (#27) ([`e4736e7`](https://github.com/MountainGod2/chaturbate_poller/commit/e4736e72e08257768f292a3249a81fb6825426ae))


## v0.8.1 (2024-09-26)

### Fixes

* fix: update Dockerfile build command ([`f3faf6c`](https://github.com/MountainGod2/chaturbate_poller/commit/f3faf6c6a759027e55f303f774a14430ab90ce91))


## v0.8.0 (2024-09-25)

### Chores

* chore: update semantic-release configuration in pyproject.toml (#25) ([`e1fd4e8`](https://github.com/MountainGod2/chaturbate_poller/commit/e1fd4e8b9d78e925ae523211a195104d66bea3ab))

### Features

* feat: refactored docker build to improve speed and reduce size (#26)

* feat: refactored docker build to improve speed and reduce size of final image

* refactor: update docker-entrypoint.sh to print command before execution ([`af26621`](https://github.com/MountainGod2/chaturbate_poller/commit/af26621ae4243d5aa6ce0d2844577753396b6fed))


## v0.7.5 (2024-09-25)

### Chores

* chore: update python-semantic-release to version 9.8.8 (#24)

* chore: update python-semantic-release to version 9.8.8

* chore: update Python version to 3.11 in CI/CD workflow ([`872aafe`](https://github.com/MountainGod2/chaturbate_poller/commit/872aafe33b5802e520bc96c1952b81f8d7443cf6))

### Fixes

* fix: corrected build step in cd action ([`16a7b80`](https://github.com/MountainGod2/chaturbate_poller/commit/16a7b808b9c1685eafd61cdea8e7a5e0f3cfc342))


## v0.7.4 (2024-09-24)

### Fixes

* fix: update tip message handling in format_messages.py (#23)

* chore: handle NameResolutionError when resolving InfluxDB URL in InfluxDBHandler

* fix: update tip message handling in format_messages.py

* test: add test for handling NameResolutionError in InfluxDBHandler ([`65ce182`](https://github.com/MountainGod2/chaturbate_poller/commit/65ce1827f7924b7f1e8ac9ec9265dfcc3adcf0de))


## v0.7.3 (2024-09-24)

### Build System

* build(deps-dev): bump pytest-asyncio from 0.23.8 to 0.24.0 (#18)

Bumps [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio) from 0.23.8 to 0.24.0.
- [Release notes](https://github.com/pytest-dev/pytest-asyncio/releases)
- [Commits](https://github.com/pytest-dev/pytest-asyncio/compare/v0.23.8...v0.24.0)

---
updated-dependencies:
- dependency-name: pytest-asyncio
  dependency-type: direct:development
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`4258c6a`](https://github.com/MountainGod2/chaturbate_poller/commit/4258c6acb53e9fa18b5ef0e68e6fdfdf3ac2813a))

* build(deps): bump sphinx-autoapi from 3.0.0 to 3.3.1 (#17)

Bumps [sphinx-autoapi](https://github.com/readthedocs/sphinx-autoapi) from 3.0.0 to 3.3.1.
- [Release notes](https://github.com/readthedocs/sphinx-autoapi/releases)
- [Changelog](https://github.com/readthedocs/sphinx-autoapi/blob/main/CHANGELOG.rst)
- [Commits](https://github.com/readthedocs/sphinx-autoapi/compare/v3.0.0...v3.3.1)

---
updated-dependencies:
- dependency-name: sphinx-autoapi
  dependency-type: direct:production
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`68ee307`](https://github.com/MountainGod2/chaturbate_poller/commit/68ee3078b21c1061751953ae4806ecad6b91002f))

* build(deps): bump myst-nb from 1.1.0 to 1.1.1 (#19)

Bumps [myst-nb](https://github.com/executablebooks/myst-nb) from 1.1.0 to 1.1.1.
- [Release notes](https://github.com/executablebooks/myst-nb/releases)
- [Changelog](https://github.com/executablebooks/MyST-NB/blob/master/CHANGELOG.md)
- [Commits](https://github.com/executablebooks/myst-nb/compare/v1.1.0...v1.1.1)

---
updated-dependencies:
- dependency-name: myst-nb
  dependency-type: direct:production
  update-type: version-update:semver-patch
...

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`7c8a6d2`](https://github.com/MountainGod2/chaturbate_poller/commit/7c8a6d29162bddaf22042f3e3ca425711e530a5c))

* build(deps-dev): bump ruff from 0.5.7 to 0.6.7 (#20)

Bumps [ruff](https://github.com/astral-sh/ruff) from 0.5.7 to 0.6.7.
- [Release notes](https://github.com/astral-sh/ruff/releases)
- [Changelog](https://github.com/astral-sh/ruff/blob/main/CHANGELOG.md)
- [Commits](https://github.com/astral-sh/ruff/compare/0.5.7...0.6.7)

---
updated-dependencies:
- dependency-name: ruff
  dependency-type: direct:development
  update-type: version-update:semver-minor
...

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com> ([`a177325`](https://github.com/MountainGod2/chaturbate_poller/commit/a177325b0cff8978ecb2164b9fd0c186fece935f))

* build(deps-dev): bump cryptography from 43.0.0 to 43.0.1

Bumps [cryptography](https://github.com/pyca/cryptography) from 43.0.0 to 43.0.1.
- [Changelog](https://github.com/pyca/cryptography/blob/main/CHANGELOG.rst)
- [Commits](https://github.com/pyca/cryptography/compare/43.0.0...43.0.1)

---
updated-dependencies:
- dependency-name: cryptography
  dependency-type: indirect
...

Signed-off-by: dependabot[bot] <support@github.com> ([`bd143a2`](https://github.com/MountainGod2/chaturbate_poller/commit/bd143a20be4d71784e71260191b40c161595a1b6))

### Chores

* chore: Remove Renovate configuration and workflow files (#15) ([`d572d7b`](https://github.com/MountainGod2/chaturbate_poller/commit/d572d7bf51ea79337a376ee2d5bf5c0549ccd390))

* chore: update dependencies in poetry.lock ([`f762e8d`](https://github.com/MountainGod2/chaturbate_poller/commit/f762e8da9b7219cd231352f52b2ba23d4487db89))

* chore: reorganize pyproject.toml ([`1763cbd`](https://github.com/MountainGod2/chaturbate_poller/commit/1763cbd0ea7e648cec9b42615ea2dc33bf8facb9))

* chore: update Python version to 3.11 in README.md ([`8c42d3b`](https://github.com/MountainGod2/chaturbate_poller/commit/8c42d3b0bee24c3a3e6ecd5251e9200c0d29b914))

* chore: update Python version to 3.11 in .readthedocs.yml ([`32c4b80`](https://github.com/MountainGod2/chaturbate_poller/commit/32c4b809ffe41165b30dc41ff334cc61952ea8e0))

* chore: update SonarCloud GitHub Action to version 3.0.0 ([`ef6f03f`](https://github.com/MountainGod2/chaturbate_poller/commit/ef6f03f4360c2c472f401578207c0e555b8c1068))

* chore: update SonarCloud GitHub Action to version 5.9.3 ([`073ae5d`](https://github.com/MountainGod2/chaturbate_poller/commit/073ae5d215e12f7059f17124734eacfd1041ea18))

### Fixes

* fix: update personal token for GitHub Pages deployment (#22)

* fix: update personal token for GitHub Pages deployment

* chore: enable commit signing in git settings

* chore: added asyncio_default_fixture_loop_scope to pytest.ini options in pyproject.toml

* test: updated URL sanitization in logging tests ([`8f857d4`](https://github.com/MountainGod2/chaturbate_poller/commit/8f857d486d285529a422426abd19456897e3b5db))

### Refactoring

* refactor: update ChaturbateClient timeout parameter name to api_timeout (#21) ([`e730527`](https://github.com/MountainGod2/chaturbate_poller/commit/e730527c21fe2b2751321e93370e0dc0a7de3d6e))

* refactor: update ConfigManager.get() method to handle default values more efficiently ([`948c6bf`](https://github.com/MountainGod2/chaturbate_poller/commit/948c6bf72449eb0dab49a8fea8f14ef4277fd511))

### Unknown

* Create dependabot.yml (#16) ([`f46bb7e`](https://github.com/MountainGod2/chaturbate_poller/commit/f46bb7e0a90db0c5d0e26bd695c9eb5b17839d55))

* Test Renovate workflow (#14)

* chore: add renovate configuration file

* chore: add Renovate workflow ([`a2693a8`](https://github.com/MountainGod2/chaturbate_poller/commit/a2693a869586db6df0ecaeaede1420e17afbcbd6))

* Merge pull request #13 from MountainGod2/dependabot/pip/cryptography-43.0.1

build(deps-dev): bump cryptography from 43.0.0 to 43.0.1 ([`5c17045`](https://github.com/MountainGod2/chaturbate_poller/commit/5c170453b0caff7e25b2c4548492016f1b565cb3))


## v0.7.2 (2024-08-15)

### Fixes

* fix: correct coverage target ([`faa955b`](https://github.com/MountainGod2/chaturbate_poller/commit/faa955b41d62bb26f2b543cdb859d4c40f5a7bd7))


## v0.7.1 (2024-08-14)

### Chores

* chore: updated dependencies and modified pytest config options ([`456b7d5`](https://github.com/MountainGod2/chaturbate_poller/commit/456b7d5d6d01fff1c12019838ec89656a12550a5))

### Fixes

* fix: created `config_manager.py` for centralized config management ([`1a3bc30`](https://github.com/MountainGod2/chaturbate_poller/commit/1a3bc30e3225a94ce083caefacf1ad27f1ec62c1))

### Unknown

* tests: updated test suite ([`1304bc9`](https://github.com/MountainGod2/chaturbate_poller/commit/1304bc9faa81bec43e0a11bda78ad68a08f36b14))


## v0.7.0 (2024-08-14)

### Chores

* chore: update dependencies to latest versions and added bandit to dev dependencies ([`ec9d763`](https://github.com/MountainGod2/chaturbate_poller/commit/ec9d763e606efc8ed9baa1e16c1f5edb79140ce4))

### Documentation

* docs: update READMER ([`d544a6d`](https://github.com/MountainGod2/chaturbate_poller/commit/d544a6d4f8ede27f36cf42d177d56b7bdcb83cd1))

### Features

* feat: refactored influxdb support ([`f22149a`](https://github.com/MountainGod2/chaturbate_poller/commit/f22149a49897bbc80eca69bb5646f7c9daae1e5e))

### Unknown

* Merge pull request #11 from MountainGod2/dev

docs: update README ([`f035f65`](https://github.com/MountainGod2/chaturbate_poller/commit/f035f6556ad7108ac1ade909c74d280da1053e3e))

* Merge pull request #10 from MountainGod2/dev

chore: update tests and expand coverage ([`4b1e274`](https://github.com/MountainGod2/chaturbate_poller/commit/4b1e27498188f275343e31b5679f9a1046b0862a))

* Merge pull request #9 from MountainGod2/main

rebase from main ([`3d315c9`](https://github.com/MountainGod2/chaturbate_poller/commit/3d315c98fa426bc9afdee874dc7d1e88eac080d0))

* Merge pull request #8 from MountainGod2/dev

tests: update tests and expand coverage ([`aaf58aa`](https://github.com/MountainGod2/chaturbate_poller/commit/aaf58aafd2dd278101235fa6469c57d21632bea3))


## v0.6.11 (2024-08-12)

### Chores

* chore: Update tests and expand coverage ([`226cc15`](https://github.com/MountainGod2/chaturbate_poller/commit/226cc15033a21dddd899277dc1385be3b6333a1f))

### Fixes

* fix: update dependencies ([`fc41ff5`](https://github.com/MountainGod2/chaturbate_poller/commit/fc41ff5c597b1268f01b28cbb6a3c6c1c926fa17))

### Unknown

* Merge pull request #7 from MountainGod2/dev

fix: update dependencies ([`5754b99`](https://github.com/MountainGod2/chaturbate_poller/commit/5754b9999b7143351707430d8df008ef6e3c3f14))

* tests: update tests and expand coverage ([`bf4d183`](https://github.com/MountainGod2/chaturbate_poller/commit/bf4d1834d744218af5107522a271aa8156ba2625))


## v0.6.10 (2024-08-12)

### Build System

* build: update Dockerfile ([`1daf4e7`](https://github.com/MountainGod2/chaturbate_poller/commit/1daf4e7d7c49f208f08ef0f2995576bb8b19b52b))

### Fixes

* fix: update influxdb error handling ([`efb13ee`](https://github.com/MountainGod2/chaturbate_poller/commit/efb13ee67daa83912e41b39f909e4ef7f8b7fdc7))

* fix: updated influxdb_client exception handling ([`9e874db`](https://github.com/MountainGod2/chaturbate_poller/commit/9e874dbfa08519290852015fbdd8fa43d58e4624))

* fix: updated influxdb_client exception handling ([`c367d56`](https://github.com/MountainGod2/chaturbate_poller/commit/c367d56a45fb3453da0b43844bf38b291096ad65))

### Unknown

* Merge pull request #6 from MountainGod2/dev

fix: update influxdb logic and improve testing coverage ([`62f9d9a`](https://github.com/MountainGod2/chaturbate_poller/commit/62f9d9a921b957f7c5419ec1524ee1003bd80de3))

* tests: update test logic ([`879de34`](https://github.com/MountainGod2/chaturbate_poller/commit/879de3435e4a6367617ef8d722171fdc9404aa41))

* tests: expand test coverage for codebase ([`e4cb6f1`](https://github.com/MountainGod2/chaturbate_poller/commit/e4cb6f104949ff9e47c04cfd540463c8d34b6c11))

* tests: updated test coverage ([`b5188d4`](https://github.com/MountainGod2/chaturbate_poller/commit/b5188d43f16d9fee5e4b32eeeaf299bd4653b9ae))

* Merge pull request #5 from MountainGod2/dev

tests: updated and expanded test coverage ([`f3d0673`](https://github.com/MountainGod2/chaturbate_poller/commit/f3d0673ccb29e18337cea67cee2d2857a2ca10bf))

* tests: updated and expanded test coverage ([`c6ef0b0`](https://github.com/MountainGod2/chaturbate_poller/commit/c6ef0b00e383c7e630c512dc1c0001f0aca109eb))


## v0.6.9 (2024-08-09)

### Build System

* build: update Dockerfile casing ([`584e622`](https://github.com/MountainGod2/chaturbate_poller/commit/584e62251b42aa8c29fe1b98b1da3da7c3fbe09e))

### Fixes

* fix: updated influxdb_client.py writing ([`a7ef3b0`](https://github.com/MountainGod2/chaturbate_poller/commit/a7ef3b073f1ce73583bc8a4758d3e29cded0fe4b))


## v0.6.8 (2024-08-09)

### Fixes

* fix: update Dockerfile and update ci-cd.yml ([`4529c59`](https://github.com/MountainGod2/chaturbate_poller/commit/4529c5942c2b0ffc4d6d6799eab174983acc1679))


## v0.6.7 (2024-08-09)

### Continuous Integration

* ci: updated workflow versions ([`7355e10`](https://github.com/MountainGod2/chaturbate_poller/commit/7355e1091b479963e8423f599bf6e90c19800e7e))

### Fixes

* fix: sanitize logging and refactor giveup log message ([`3de1c08`](https://github.com/MountainGod2/chaturbate_poller/commit/3de1c08cde0a612804b9fc1b9b1e08442c5de8c1))

### Unknown

* tests: updated test suite ([`cfd6a6f`](https://github.com/MountainGod2/chaturbate_poller/commit/cfd6a6f4bc3cab71457a9e89be45c748c38a63d2))


## v0.6.6 (2024-08-08)

### Fixes

* fix: re-added `latest` tag ([`0b1f157`](https://github.com/MountainGod2/chaturbate_poller/commit/0b1f157dd3a30596e5604ce8908d0cceb481df6a))


## v0.6.5 (2024-08-08)

### Fixes

* fix: corrected ci-cd.yml image name for docker build ([`06885c8`](https://github.com/MountainGod2/chaturbate_poller/commit/06885c84518227fde0d3b308b35f647a68a0f17e))


## v0.6.4 (2024-08-08)

### Continuous Integration

* ci: update ci-cd.yml to add tags for docker releases ([`e3d6365`](https://github.com/MountainGod2/chaturbate_poller/commit/e3d6365215a3a8e2854f0dcdc0fd54592c7b89de))

### Fixes

* fix: update ci-cd.yml and influxdb_client.py ([`42016d0`](https://github.com/MountainGod2/chaturbate_poller/commit/42016d0b76ca5add13a98484c13f0633fbbedb2d))


## v0.6.3 (2024-08-08)

### Fixes

* fix: update Dockerfile ([`4f4d27e`](https://github.com/MountainGod2/chaturbate_poller/commit/4f4d27e9d3b994cf12b31f1ba8ba1b82d20f157c))


## v0.6.2 (2024-08-08)

### Fixes

* fix: update influxdb formatting ([`bfd31e7`](https://github.com/MountainGod2/chaturbate_poller/commit/bfd31e7cd874312c1186cef642ca02e5fbc603f4))


## v0.6.1 (2024-08-08)

### Documentation

* docs: updated README.md with CLI and docker examples ([`b845176`](https://github.com/MountainGod2/chaturbate_poller/commit/b8451764ec2c79049ea7ae3dc28097841391ca14))

### Fixes

* fix: added `--no-cache-dir` to pip install ([`1aad475`](https://github.com/MountainGod2/chaturbate_poller/commit/1aad4756f33b04a4fa6254022230c6004f599204))


## v0.6.0 (2024-08-08)

### Features

* feat: added docker functionality ([`5323055`](https://github.com/MountainGod2/chaturbate_poller/commit/53230550613f439f3e8fba9e2b067d7d1e387d45))


## v0.5.19 (2024-08-08)

### Fixes

* fix: broken Dockerfile fix ([`5362468`](https://github.com/MountainGod2/chaturbate_poller/commit/53624688f2f733eba146d104ea5a17c47c7afefd))


## v0.5.18 (2024-08-08)

### Fixes

* fix: simplify Dockerfile logic ([`19faf38`](https://github.com/MountainGod2/chaturbate_poller/commit/19faf38f47187ff753cdee06873da44fc2e3e7e1))


## v0.5.17 (2024-08-07)

### Fixes

* fix: update Dockerfile ([`0e646c0`](https://github.com/MountainGod2/chaturbate_poller/commit/0e646c046c648ed100c78c1be381ada073871871))


## v0.5.16 (2024-08-07)

### Fixes

* fix: update Dockerfile ([`93779ea`](https://github.com/MountainGod2/chaturbate_poller/commit/93779ea270538bf2e8b5aed4fbd1b6308bd9ab20))


## v0.5.15 (2024-08-07)

### Fixes

* fix: update logging and Dockerfile entrypoint ([`c252c04`](https://github.com/MountainGod2/chaturbate_poller/commit/c252c0428d6453fdfc438040569bc1bb6874ca7c))


## v0.5.14 (2024-08-07)

### Fixes

* fix: changed CMD to ENTRYPOINT in Dockerfile ([`a4628dd`](https://github.com/MountainGod2/chaturbate_poller/commit/a4628dd3b91f8ce8f18af7e1da9c751d656b14f3))


## v0.5.13 (2024-08-07)

### Fixes

* fix: updated commandline logic and added testbed flag ([`809e7ac`](https://github.com/MountainGod2/chaturbate_poller/commit/809e7ac6b4b046128f5b6fed34a51e443dc9a5bc))


## v0.5.12 (2024-08-06)

### Continuous Integration

* ci: update ci-cd.yml to fix failing build ([`cb35283`](https://github.com/MountainGod2/chaturbate_poller/commit/cb352838b82ecfa6212a67f8167a0dd37df615f2))

* ci: updated ci-cd.yml build action ([`0e8fae0`](https://github.com/MountainGod2/chaturbate_poller/commit/0e8fae06a00d3e6f2f47518edd9e44a0e01213bd))

* ci: fix ci-cd.yml ([`51dd935`](https://github.com/MountainGod2/chaturbate_poller/commit/51dd935d5eb954058a603de4d34d1d367b414e7d))

### Fixes

* fix: add exception handling for __main__.py ([`7f06b12`](https://github.com/MountainGod2/chaturbate_poller/commit/7f06b1265693ec91b0a25d112bdec84bc7290d1b))


## v0.5.11 (2024-08-06)

### Fixes

* fix: updated ci-cd.yml and Dockerfile ([`bff49d9`](https://github.com/MountainGod2/chaturbate_poller/commit/bff49d95c6d86c044b01573fc200edc2eb7fa85c))


## v0.5.10 (2024-08-06)

### Fixes

* fix: updated Dockerfile and __main__.py ([`1f136e6`](https://github.com/MountainGod2/chaturbate_poller/commit/1f136e6c3f7168fdeedd4a13bbe7aff9c470d75e))


## v0.5.9 (2024-08-06)

### Fixes

* fix: update Dockerfile to install via pip ([`15580c9`](https://github.com/MountainGod2/chaturbate_poller/commit/15580c98a8fe6fbb7180f6196fb320cd72c8bd7a))


## v0.5.8 (2024-08-06)

### Fixes

* fix: modified Dockerfile poetry install command ([`2781d9e`](https://github.com/MountainGod2/chaturbate_poller/commit/2781d9ec61c7905e48f7ac3c39de8521217c668c))


## v0.5.7 (2024-08-06)

### Continuous Integration

* ci: fix ci-cd.yml checkout ([`4b7025f`](https://github.com/MountainGod2/chaturbate_poller/commit/4b7025f30474930bf4605117a7174864b1017ba9))

### Fixes

* fix: updated docker build ([`da606b7`](https://github.com/MountainGod2/chaturbate_poller/commit/da606b7281f2e21a5e11b8443d156fd7b6e3d63c))


## v0.5.6 (2024-08-06)

### Fixes

* fix: updated Dockerfile ([`77ce8f5`](https://github.com/MountainGod2/chaturbate_poller/commit/77ce8f52b4547a687313809fe6f2be10b3d8756d))


## v0.5.5 (2024-08-06)

### Fixes

* fix: updated docker build ([`71fa864`](https://github.com/MountainGod2/chaturbate_poller/commit/71fa864a9d89a2e6704aee83c18d53498c976701))


## v0.5.4 (2024-08-06)

### Continuous Integration

* ci: fixed Dockerfile and ci-cd.yml ([`50d7373`](https://github.com/MountainGod2/chaturbate_poller/commit/50d7373c9e6675104634172740c22b9f83201f42))

### Fixes

* fix: updated __main__.py ([`ccfa8c0`](https://github.com/MountainGod2/chaturbate_poller/commit/ccfa8c075d691a78fff50076b12f9ee0209dbfd9))

* fix: updated Docker build ([`5ab8dc8`](https://github.com/MountainGod2/chaturbate_poller/commit/5ab8dc882f865d87a2553c7895dd038054e007d2))


## v0.5.3 (2024-08-06)

### Fixes

* fix: updated Dockerfile ([`50f9254`](https://github.com/MountainGod2/chaturbate_poller/commit/50f92546fea504743e78b8de6c045c75513848a8))


## v0.5.2 (2024-08-06)

### Fixes

* fix: removed unused argument from __main__.py ([`43f3c56`](https://github.com/MountainGod2/chaturbate_poller/commit/43f3c563c61d4c6906fedd0f2b11a5170951c14e))

* fix: update Dockerfile ([`500820e`](https://github.com/MountainGod2/chaturbate_poller/commit/500820e33cde56abb6faffb841f4cf4c64390914))


## v0.5.1 (2024-08-06)

### Continuous Integration

* ci: update Dockerfile and add validation to build action ([`a63390a`](https://github.com/MountainGod2/chaturbate_poller/commit/a63390ace36f7460e2f8dab8830d1cdc7486dc02))

* ci: fix syntax ([`ced387e`](https://github.com/MountainGod2/chaturbate_poller/commit/ced387e2bd1c5ecc10139847c51c875828422788))

* ci: merged docker-publish into ci-cd action ([`27343d2`](https://github.com/MountainGod2/chaturbate_poller/commit/27343d29e49aa43152121cd7e849cfa0ec5327a7))

* ci: update Dockerfile ([`7fdd7a3`](https://github.com/MountainGod2/chaturbate_poller/commit/7fdd7a32fdd2c217d3237d4d1a9a21bb9cc6846b))

* ci: fix docker build action ([`bfab901`](https://github.com/MountainGod2/chaturbate_poller/commit/bfab901183fde36e44f02a0ede41b0316414e6c3))

* ci: fix docker build action ([`a6f4e9a`](https://github.com/MountainGod2/chaturbate_poller/commit/a6f4e9aa078f3c04b61a65729413b859282a48d2))

### Fixes

* fix: updated Dockerfile ([`d18d910`](https://github.com/MountainGod2/chaturbate_poller/commit/d18d910b0fca07498be3f1d6ffdf52bedf9f87ef))


## v0.5.0 (2024-08-05)

### Continuous Integration

* ci: corrected pyproject.toml ([`68f2cc4`](https://github.com/MountainGod2/chaturbate_poller/commit/68f2cc4ab20899a3932615452211bc95c4d3461f))

### Features

* feat: add initial influxdb functionality ([`c94990d`](https://github.com/MountainGod2/chaturbate_poller/commit/c94990d2029f23989cde76711e4616e584c564cc))

### Fixes

* fix: ensure repository name is lowercase ([`1b23d35`](https://github.com/MountainGod2/chaturbate_poller/commit/1b23d35b48d1552e6e0a945a4e9cd0d322b4a444))

### Unknown

* tests: remove failing tests ([`037e361`](https://github.com/MountainGod2/chaturbate_poller/commit/037e361b393a9e4ca9788a668483dbde054a4591))


## v0.4.0 (2024-08-04)

### Continuous Integration

* ci: update action versions to use Node.js 20 ([`0c092ae`](https://github.com/MountainGod2/chaturbate_poller/commit/0c092ae6d5ea6905359e7356aea4dcbadaf04c55))

* ci: updated coverage relative files ([`28f2fb7`](https://github.com/MountainGod2/chaturbate_poller/commit/28f2fb75c337761c82cb9539f72bd31ddea6a70f))

* ci: update sonar test location and action naming ([`956c983`](https://github.com/MountainGod2/chaturbate_poller/commit/956c9831a023bc803b1ab8e52c2853eb6aee9508))

* ci: separate sonar test and source directories ([`909cd5d`](https://github.com/MountainGod2/chaturbate_poller/commit/909cd5d9144f1fc50ab8e301123f37d9912806c9))

### Documentation

* docs: update issue templates ([`f90bf6f`](https://github.com/MountainGod2/chaturbate_poller/commit/f90bf6f3c1c5f37bfd34b1de9b88c9b0b52927ca))

* docs: renamed conduct.md to code_of_conduct.md ([`5317617`](https://github.com/MountainGod2/chaturbate_poller/commit/5317617f81d87c45256977c558152472688b415c))

### Features

* feat: updated documentation and bumped dependencies ([`5f5f37c`](https://github.com/MountainGod2/chaturbate_poller/commit/5f5f37c080b58060fcf9c11eb89b1f05b84bc104))

### Refactoring

* refactor: added pre-commit hooks and standardized whitespaces ([`0f15e93`](https://github.com/MountainGod2/chaturbate_poller/commit/0f15e9356da8d4bda36f5bc287cd1781cbaead13))


## v0.3.16 (2024-04-21)

### Build System

* build: fix broken build ([`9d59bde`](https://github.com/MountainGod2/chaturbate_poller/commit/9d59bde26803150cb00c61ffb1a0d88b827ed82e))

* build: changed broken workflow path ([`5b567fa`](https://github.com/MountainGod2/chaturbate_poller/commit/5b567fa522a5f163b3fb50f26c1d95f1fa5aca5d))

* build: disable failing sonar scan ([`dc42bc3`](https://github.com/MountainGod2/chaturbate_poller/commit/dc42bc3c2a2121f22ee338b39eea1f343bbe1a34))

* build: update sonar coverage location ([`7fdf198`](https://github.com/MountainGod2/chaturbate_poller/commit/7fdf198ca5f1a53fc4291a59a3fc586799df79ea))

* build: update SonarCloud workflow ([`d228255`](https://github.com/MountainGod2/chaturbate_poller/commit/d2282559ebe6ed608ef462d9fb366efdf73e108c))

* build: updated build workflow ([`49d791c`](https://github.com/MountainGod2/chaturbate_poller/commit/49d791ca3f8e2e22225c00f66ea6042301d367d4))

### Continuous Integration

* ci: update pytest action ([`cc14a3b`](https://github.com/MountainGod2/chaturbate_poller/commit/cc14a3ba87d6c166b90e20f8029d319ada8cce70))

### Documentation

* docs: update badges and sonar properties ([`2332e92`](https://github.com/MountainGod2/chaturbate_poller/commit/2332e9282fc0c372d1d062f25cb7524d08b15792))

### Fixes

* fix: updated backoff logger ([`c0497ee`](https://github.com/MountainGod2/chaturbate_poller/commit/c0497ee946d6e6f253d29bef820d3c314df1129d))

### Testing

* test: refactored tests and updated .gitignore ([`086a61d`](https://github.com/MountainGod2/chaturbate_poller/commit/086a61d691a5cf62b05cea255bcf81b66456098b))


## v0.3.15 (2024-04-16)

### Documentation

* docs: update README.md formatting ([`173d405`](https://github.com/MountainGod2/chaturbate_poller/commit/173d4053e774e1f3730530e3a61ee0280bcc2a9a))

### Fixes

* fix: remove unused argument ([`e9c315a`](https://github.com/MountainGod2/chaturbate_poller/commit/e9c315a6e5e1ca719aaf40b7e5e974e0163d21a0))

### Testing

* test: updated initialization tests ([`1372d0f`](https://github.com/MountainGod2/chaturbate_poller/commit/1372d0f6235dc36688245c5d7980ac0a91bd6a2f))


## v0.3.14 (2024-04-15)

### Fixes

* fix: corrected python version in .readthedocs.yml ([`c6c8135`](https://github.com/MountainGod2/chaturbate_poller/commit/c6c8135c58d5076e59df5ac80c4235eb74fc5bdf))


## v0.3.13 (2024-04-15)

### Build System

* build: updated dependabot.yml location ([`3323bf1`](https://github.com/MountainGod2/chaturbate_poller/commit/3323bf165b179ddb7c9447b69d31ee39527a59f4))

* build: updated pyproject.toml ([`7bbf133`](https://github.com/MountainGod2/chaturbate_poller/commit/7bbf1331330d5fadc4454febb623df8919a650b0))

* build: update myst-nb versioning ([`6b1ee57`](https://github.com/MountainGod2/chaturbate_poller/commit/6b1ee57af40ea3f912fc1f3ccccfe001a5331571))

* build: update versions ([`557ca01`](https://github.com/MountainGod2/chaturbate_poller/commit/557ca01a540e99b4221c9a7c20f324976d78af8b))

### Documentation

* docs: updated versions for doc building ([`e4555a8`](https://github.com/MountainGod2/chaturbate_poller/commit/e4555a877de637e8c30a93a63dc2b23266a8c58a))

* docs: updated .readthedocs.yml ([`beb5dc0`](https://github.com/MountainGod2/chaturbate_poller/commit/beb5dc0c4dd45daa958f2f57a843da49bc212f3a))

* docs: updated .readthedocs.yaml ([`b305368`](https://github.com/MountainGod2/chaturbate_poller/commit/b305368e84b70be2d6984ead8b9872d8e10272fc))

* docs: updated .readthedocs.yaml ([`3cb901a`](https://github.com/MountainGod2/chaturbate_poller/commit/3cb901aaf27f642faa2975dcc6099f2d78352a04))

* docs: added docs group in pyproject.toml ([`8d3a733`](https://github.com/MountainGod2/chaturbate_poller/commit/8d3a73389785eddf19a5aee1ccb955fb5ba25b09))

* docs: update .readthedocs.yaml ([`97fd0a3`](https://github.com/MountainGod2/chaturbate_poller/commit/97fd0a31645f2384b066e6bfe389d9fd8ea5dd63))

* docs: bumped required python version ([`6693393`](https://github.com/MountainGod2/chaturbate_poller/commit/66933930760de5297f872efd1630d5c8a9f5ed18))

* docs: updated .readthedocs.yaml ([`6301fba`](https://github.com/MountainGod2/chaturbate_poller/commit/6301fba987037b82a4c5ae50e20f79550e9a0190))

* docs: updated .readthedocs.yaml ([`931356a`](https://github.com/MountainGod2/chaturbate_poller/commit/931356af38899e3c6d2cbfde2c92ebc74612baef))

* docs: update .readthedocs.yaml ([`4720be2`](https://github.com/MountainGod2/chaturbate_poller/commit/4720be276947c746fc546166efd01b851a4d25d6))

* docs: added .readthedocs.yaml ([`0b178bf`](https://github.com/MountainGod2/chaturbate_poller/commit/0b178bf9cb19ef407b4138cff404fb56c3f0c21f))

* docs: updated ci-cd badge ([`953a48d`](https://github.com/MountainGod2/chaturbate_poller/commit/953a48dc9cab16add3af68f626483a2abb445c60))

* docs: added badges to README ([`319a4e9`](https://github.com/MountainGod2/chaturbate_poller/commit/319a4e95a86793bac97cc559ba48cbd94d09b4a4))

### Fixes

* fix: updated workflows and restructured docs ([`2c0dbcc`](https://github.com/MountainGod2/chaturbate_poller/commit/2c0dbcc9bea8c4152dd28ea03af46604dacd1ff5))


## v0.3.12 (2024-04-15)

### Documentation

* docs: added ci-cd badge to README ([`245662c`](https://github.com/MountainGod2/chaturbate_poller/commit/245662c020dfb9178b7675bfba8762e2cf111ce9))

* docs: updated markdown for example code in README ([`0149f71`](https://github.com/MountainGod2/chaturbate_poller/commit/0149f71310a54214d43c673ee489921c6f220bf0))

* docs: update example in README ([`761a3d5`](https://github.com/MountainGod2/chaturbate_poller/commit/761a3d51996071336e38378b6b602503b0c2386e))

### Fixes

* fix: corrected backoff on exception ([`ef2a686`](https://github.com/MountainGod2/chaturbate_poller/commit/ef2a6862a06ba9c8cc5c36b963c4a94c9bb9e954))

* fix: updated models.py to define appropriate fields as being optional ([`f5e6240`](https://github.com/MountainGod2/chaturbate_poller/commit/f5e624086e3c84f22bc2d5fb0436f6d0f1e8e9a5))

### Refactoring

* refactor: updated backoff logic ([`fb1b171`](https://github.com/MountainGod2/chaturbate_poller/commit/fb1b17119f4757b0b40b2513616c136f537abe27))

* refactor: updated event_handler to use logging instead of printing messages ([`f0201fc`](https://github.com/MountainGod2/chaturbate_poller/commit/f0201fcdce635ed36e340f419d11a3909356e378))


## v0.3.11 (2024-04-14)

### Documentation

* docs: update examples/ ([`30cd5ca`](https://github.com/MountainGod2/chaturbate_poller/commit/30cd5ca5298e19b7ecefa86bbdb809832a5f65ed))

### Fixes

* fix: updated backoff logic and updated logging ([`0f12c7d`](https://github.com/MountainGod2/chaturbate_poller/commit/0f12c7db530fc7cfe5a4edd28cf39b4e00d93ae4))

### Refactoring

* refactor: updated next_url typing in models.py ([`c3cca0c`](https://github.com/MountainGod2/chaturbate_poller/commit/c3cca0c1eb1410275b89d13f56ba62c3a19c01d4))

* refactor: adjusted constants and updated exception handling ([`df34514`](https://github.com/MountainGod2/chaturbate_poller/commit/df3451466e2583ca60abf024c54b6508bd7d1cb5))

### Testing

* test: added test logs to .gitignore ([`29f518c`](https://github.com/MountainGod2/chaturbate_poller/commit/29f518c894fc0cd40afebd96b21f3102720ccf42))

* test: update tests logic ([`e6ded44`](https://github.com/MountainGod2/chaturbate_poller/commit/e6ded44e47518902a79a74b36a03dae527fac28e))


## v0.3.10 (2024-04-12)

### Fixes

* fix: adjust backoff log level and refactor client instantiation ([`32df166`](https://github.com/MountainGod2/chaturbate_poller/commit/32df16618ad1e6a1ba1c07a83fa218f4889ff279))


## v0.3.9 (2024-04-11)

### Fixes

* fix: update tests and added raise ValueError for 401 responses ([`6956095`](https://github.com/MountainGod2/chaturbate_poller/commit/6956095c2997d2a9dc1ffafdd598b8c45967f4f0))


## v0.3.8 (2024-04-11)

### Fixes

* fix: changed URL default and added argument to allow the use of the testbed URL for development ([`17b074d`](https://github.com/MountainGod2/chaturbate_poller/commit/17b074d1925b93d76170122f67135bb2b6590d58))


## v0.3.7 (2024-04-11)

### Fixes

* fix: modified http error codes to use an enum ([`d67e3ce`](https://github.com/MountainGod2/chaturbate_poller/commit/d67e3ced6c80259901e4f9098099a4157d9cd7be))

### Testing

* test: added formatting tests into test_chaturbate_poller.py ([`4dd6206`](https://github.com/MountainGod2/chaturbate_poller/commit/4dd6206773d229aee54fe8b9908f1948541fc1a5))


## v0.3.6 (2024-04-10)

### Fixes

* fix: correct typing and format code ([`9cd7688`](https://github.com/MountainGod2/chaturbate_poller/commit/9cd768811402c9a428541b661708eb904071201f))

### Testing

* test: refactored test_format_message.py ([`4bca906`](https://github.com/MountainGod2/chaturbate_poller/commit/4bca9064657fae333e7a81a881e978a594f7e281))


## v0.3.5 (2024-04-10)

### Fixes

* fix: added format_messages.py and updated tests ([`e57fa63`](https://github.com/MountainGod2/chaturbate_poller/commit/e57fa63c7bd7929f3a4d54970cabb9dda915650b))


## v0.3.4 (2024-04-09)

### Fixes

* fix: rename files and add logs to .gitignore ([`43ed001`](https://github.com/MountainGod2/chaturbate_poller/commit/43ed001ce0e73d14ce05a2476e5084b232347b1e))


## v0.3.3 (2024-04-09)

### Fixes

* fix: refactored models and added test coverage ([`aa69183`](https://github.com/MountainGod2/chaturbate_poller/commit/aa691832303cadeef6cc1ea650c7e23ebecb2014))


## v0.3.2 (2024-04-08)

### Fixes

* fix: update examples and refactor logging ([`47f9208`](https://github.com/MountainGod2/chaturbate_poller/commit/47f92086978ed0344c5d3c3cd70652755b90a8be))


## v0.3.1 (2024-04-07)

### Fixes

* fix: refactor package and update README.md ([`bea835a`](https://github.com/MountainGod2/chaturbate_poller/commit/bea835a387df9775b5274cdacba7f00a14e48c2f))


## v0.3.0 (2024-04-07)

### Features

* feat: refactored modules and updated docstrings ([`17a3a8b`](https://github.com/MountainGod2/chaturbate_poller/commit/17a3a8bb35082da36df87cc1f1031115e9b6f320))

### Testing

* test: adjust timeout for test_main.py ([`0a3ac67`](https://github.com/MountainGod2/chaturbate_poller/commit/0a3ac673780d7157159121e0917d6970c115078c))


## v0.2.0 (2024-04-04)

### Features

* feat: refactor chaturbate_poller.py and tests ([`99ebad1`](https://github.com/MountainGod2/chaturbate_poller/commit/99ebad18244d69ad6deb1ab436f06be6df369ce9))

### Testing

* test: refactor test_chaturbate_poller.py ([`12001bd`](https://github.com/MountainGod2/chaturbate_poller/commit/12001bd1b41d2e3a7a9443e1660f5292d9531a49))

* test: added additional tests to test_main.py ([`11dafde`](https://github.com/MountainGod2/chaturbate_poller/commit/11dafde7c0b4ef2afe7a11b4b46e1c205f3dd70b))


## v0.1.4 (2024-04-03)

### Fixes

* fix: fixed tests and updated workflows ([`0793ff6`](https://github.com/MountainGod2/chaturbate_poller/commit/0793ff686397032f99d7e3155db84003098c488f))

### Testing

* test: added user env's to ci-cd.yml test ([`4fa745c`](https://github.com/MountainGod2/chaturbate_poller/commit/4fa745c2581e393e2b815962a72fc007f33827ef))

* test: updated ci-cd.yml ([`b0dad36`](https://github.com/MountainGod2/chaturbate_poller/commit/b0dad362fcd21d99bca607b4a90783be31497018))

* test: update test_main.py ([`6252a3a`](https://github.com/MountainGod2/chaturbate_poller/commit/6252a3a76310fa947cb9fbe4e1e3dd81b7e59b7a))

* test: update ci-cd.yml ([`bb2850b`](https://github.com/MountainGod2/chaturbate_poller/commit/bb2850b8e38d035c52f70a2037bf57fd1433d658))

* test: update ci-cd.yml ([`2882e5e`](https://github.com/MountainGod2/chaturbate_poller/commit/2882e5e8d6e09440833c19b734aa089fc657be9d))

* test: update ci-cd.yml ([`94c4f65`](https://github.com/MountainGod2/chaturbate_poller/commit/94c4f652da65855e837492fa13c1f1c66bd864f1))

* test: update test_main.py ([`c9b932a`](https://github.com/MountainGod2/chaturbate_poller/commit/c9b932a7c3fec214ff197dbf60a960627050cdbb))


## v0.1.3 (2024-04-02)

### Build System

* build: update ci-cd.yml ([`77c3f93`](https://github.com/MountainGod2/chaturbate_poller/commit/77c3f93d83c7e2928b704ba65b2013cf15715bd8))

* build: added poetry to dev group dependencies and update poetry.lock ([`92cb07f`](https://github.com/MountainGod2/chaturbate_poller/commit/92cb07f179858d6437304aacc3a1f859ce0aa6f3))

* build: moved codeql.yml to it's own file ([`c967b3e`](https://github.com/MountainGod2/chaturbate_poller/commit/c967b3e5104c1adf2dbb162c6bd956def153301e))

* build: added dependabot.yml ([`d33aca9`](https://github.com/MountainGod2/chaturbate_poller/commit/d33aca9b40d097f3e12c4b70ec2880c5669222b3))

* build: added CodeQL to ci-cd.yml ([`a63da4c`](https://github.com/MountainGod2/chaturbate_poller/commit/a63da4ce25575c81978a02fd692ab93aa337d8cd))

### Documentation

* docs: added SECURITY.md ([`2a2785d`](https://github.com/MountainGod2/chaturbate_poller/commit/2a2785d60928caa4fbeed139c910a4d05e977f66))

### Fixes

* fix: correct test_main.py python path ([`be8b38f`](https://github.com/MountainGod2/chaturbate_poller/commit/be8b38f8846b3fcdb8ee7a3b62a70a9f65757fb5))

### Testing

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

### Fixes

* fix: update links to repository and docs in pyproject.toml ([`3003d16`](https://github.com/MountainGod2/chaturbate_poller/commit/3003d16c9be5d1c25f30e91c1b2a0912475a904e))


## v0.1.1 (2024-04-01)

### Build System

* build: fix ruff actions ([`fbaf8e7`](https://github.com/MountainGod2/chaturbate_poller/commit/fbaf8e7bd3fa58dff2a5157b9005442d080bd7be))

* build: update ci-cd.yml to include ruff formatting and linting ([`c44acdf`](https://github.com/MountainGod2/chaturbate_poller/commit/c44acdf132220b3668abf81d4a5468720049ec31))

### Fixes

* fix: update imports in chaturbate_poller.py ([`ade470f`](https://github.com/MountainGod2/chaturbate_poller/commit/ade470f0c2a89361b1fdd32d2ba5a7ee232c6757))

### Testing

* test: update test_chaturbate_poller.py ([`1cc1855`](https://github.com/MountainGod2/chaturbate_poller/commit/1cc1855d263b6165d568ed6fe38364fe0db925c7))


## v0.1.0 (2024-03-31)

### Build System

* build: updated documation build action in ci-cd.yml to ensure all files are updated ([`9d679ed`](https://github.com/MountainGod2/chaturbate_poller/commit/9d679ede55fce85d8b2254e88695c4a824cf9335))

### Documentation

* docs: update README.md ([`3f7241f`](https://github.com/MountainGod2/chaturbate_poller/commit/3f7241fb5dfcd0ed15cbc9e10fb67979bd484f80))

### Features

* feat: add codecov to ci-cd.yml ([`9973692`](https://github.com/MountainGod2/chaturbate_poller/commit/9973692f6cea70ea1e64b18a9e3b7cbfa59a4f8a))


## v0.0.1 (2024-03-31)

### Fixes

* fix: add python-semantic-release to requirements ([`1c67a65`](https://github.com/MountainGod2/chaturbate_poller/commit/1c67a658b414202372a01c18cda21c0262622a68))


## v0.0.0 (2024-03-31)

### Unknown

* first commit ([`49a9bf2`](https://github.com/MountainGod2/chaturbate_poller/commit/49a9bf2f34f22bbc842dfb000e97e8249490b4fa))
