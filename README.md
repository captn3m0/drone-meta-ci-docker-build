# drone-meta-ci-docker-build

# What does it do?

drone-meta-ci-docker-build saves time by automating the slow and boring part of waiting
and triggering multiple builds on the base images.

# How it Works?

The image layer configuration is defined in `config.yml` which uses "roles"
defined inside `roles` directory. A script (`render.py`) generates the following:

1.  Dockerfiles for each of the final images.
2.  `drone.yml` with correct deployment triggers (so building a leaf node triggers a base rebuild)
3.  `hadolint` is run against all of the generated Dockerfiles

The builds to any specific layer can be triggered using drone deploys. It also ensures
that builds are testable by generating non-master builds in a separate namespace.

---

# CONTRIBUTING

## Guidelines

-   Make sure your editor supports `editorconfig`
-   Run `python render.py` once and try a build locally
-   Make sure that tests are passing
-   Make sure that your branch name doesn't contain a slash
-   File a PR with your changes (usually only to `config.yml` and the `roles` directory)
-   If you are using a `COPY/ADD` command inside a role, use the complete path to the file: `COPY roles/role-name/files/asset.tar.gz /tmp`

## Builds vs Deploys

drone-meta-ci-docker-build uses builds to test the Dockerfiles and deploys to actually build them and push them to Docker Hub. In order to trigger a deploy (and build a new image), do the following:

1.  Setup your Drone Token
2.  Run `drone deploy [build_id] [pipeline]`

Where build_id is the build number (integer) for a green build on Drone and pipeline is one of the entries in `config.yml`. For eg, to trigger a build for `php-7.0-nginx`, you can run (assuming a build id=`143`):

`drone deploy captn3m0/drone-meta-ci-docker-build 143 python-3.6`

Note that you do not need to trigger a deploy to any of the base layers, they will automatically get rebuilt (if required).

## Pull Request Flow

Any commits to a non-master branch will result in tags getting prefixed with your branch name.

So if you push a branch called `pip-upgrade`, and trigger a deploy to `python-3.6`.
The following tags will get published on Docker Hub:

-   `captn3m0/drone-meta-ci-docker-build:pip-upgradepython-3.6`
-   `captn3m0/drone-meta-ci-docker-build:pip-upgradebase3.7`

You can now use the above in your application PR flow to test out the changes.

---

The codebase is roughly split into three parts:

## Build Code

This is the code that installs your dependencies and
does the useful stuff. For eg: `apk add php`. This is where most of the PRs should be

The following files:

1.  `roles/` directory
2.  `config.yml` file

## Generated Code

The following files are generated and are NOT TO BE EDITED BY HAND

-   `.drone.yml`
-   `*.Dockerfile`

You can generate both of them by running `python render.py` or just the dockerfiles
by running `python render.py docker`.

## Scaffold Code

This is the code that takes stuff from "Build Code" and converts it to "Generated"

-   `render.py`
-   `drone.yml` (base template for generating .drone.yml)
-   `step.yml` (template for generating each build step in .drone.yml)

## Extras

There are a few extra files in the repo:

-   `.editorconfig`: <http://editorconfig.org/>
-   `.hadoint.yml`: Used for running the Docker Lint in builds
