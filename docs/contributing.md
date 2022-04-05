<!-- NOTE: there is a symlink, so this is *both* /CONTRIBUTING.md and /docs/contributing.md.
           don't use mkdocs-specific stuff, or github-specifc stuff in here,
           because it will break somewhere -->

# Contributing Guide

The scope of this library is pretty large; feel free to volunteer new modules
as long as they fit with the ethos of the project:

- each module should be focused one one task and widely generalizable for many
  teachers
- modules should be composable but not interdependent\*
- modules must include thorough and high quality unit tests
- modules must include documentation

\*_any module can depend on `teacherhelper.sis`. If we add more modules like
that, it would probably make sense to have a `teacherhelper.core` or
`teacherhelper.common` internal API to make that clear`_

Within those limitations, it would be awesome for teachers and
professors to throw their own utility libraries into the pot to create a
library of utilities that meets the library goal: **useful abstractions and CLI
to make teaching more scriptable.**

## Dev Workflows & Makefile

There is a Makefile, but it facilitates pretty normal python development
workflow things. It includes the following rules.

**test (default rule)**

Setup virtual environment if needed, then run unit tests.

**build**

Create source distribution and wheel in `./dist`

**clean**

Delete source distribution in `./dist` and the _egg_info_ file.

**fmt**

Runs `black` code formatter. There is also a **fmt-check** rule, which runs
`black --check` in GitHub Actions.

**serve-docs**

Serve the documentation website on port 8000. This will also check for the
presence of documentation dependencies in requirements.docs.txt, and install
them if needed before starting up the mkdocs server.

**deploy-docs**

Build and push a new documentation website container to Docker Hub and deploy
to kubernetes via terraform. The container tag is derived from the current git
tag. Will use credentials from `~/.aws/credentials` and `~/.kube/config`. This
rule also runs in GitHub Actions for any tagged commit.

**dist-production**

Build the source distribution and upload it to PyPi. Version number is derived
from current git tag. This runs in GitHub Actions for any tagged commit.

**dist-test**

Same as dist-production, but upload to test PyPi instead.

### `.exrc`

There is a vim `.exrc` file in the root of the project which maps `te` to
`:make test <cr>` in normal mode.

## Windows Compatibility

I (jdevries3133, the original author) develop on OS X, I develop for Linux
sometimes... I really don't know the first thing about Windows when it comes to
software development. It is important to me that the library works on Windows,
but I am concerned that some things may be broken. Please feel free to submit
patches for Windows compatibility, or report bugs related to this!

## Housekeeping

### Versioning

This project uses typical semantic versioning. The door is open to new modules
being added; this necessarily means future deprecation and removals if those
things become irrelevant or unmaintained. For a deprecation policy, deprecated
functionality will always emit DeprecationWarnings one major release before
they are removed.

### Contributing Process

Use GitHub issues and pull requests as usual. Be nice. Speaking for myself
(jdevries3133), I will happily engage with any issue or pull request!

### Project Dependencies

This library's setup.cfg already specifies decent number of dependencies. More
can be added, within reason, if they support useful new functionality for the
library as a whole.
