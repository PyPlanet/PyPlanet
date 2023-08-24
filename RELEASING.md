# Release Checklist for PyPlanet core + contrib apps.

## Main Release

* [ ] Bring the ``master`` branch up to date.
* [ ] ~~Check the Travis CI build status of the ``master`` branch.~~
* [ ] ~~Make sure we update the version number according to Semver 2.0.0.~~
* [ ] Update `CHANGELOG.rst`, you can use the GitHub compare or milestone overview to see the changes.
* [ ] Bump version with `bumpversion --new-version 0.6.0 final` (this will commit the changes directly, you still have to push!).
* [ ] (Only when manually updating, not using bumpversion) Update documentation version `conf.py` and internal version in `__init__.py` in PyPlanet root folder.
* [ ] Run build commands with `make build` and test the cli with pip installation.
* [ ] For new major or minor versions: Create new branch for the big releases (if major/minor update, not for bugfix):
```
    $ git checkout -b release/2.9.x
    $ git tag 2.9.0
    $ git push --all
    $ git push --tags
```
* [ ] OR: For bugfix releases, checkout the existing release branch and update:
```
    $ git checkout release/2.9.x
    $ git tag 2.9.2
    $ git push --all
    $ git push --tags
```
* [ ] Create and upload source distributions e.g.:
```
    $ make build
    $ make publish
```
* [ ] Create/update release notes on GitHub releases page.
