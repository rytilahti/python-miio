1. Set release information

```bash
export PREVIOUS_RELEASE=$(git describe --abbrev=0)
export NEW_RELEASE=0.5.1
```

2. Update the version number

```
poetry version $NEW_RELEASE
```

2. Generate changelog since the last release

```bash
# gem install github_changelog_generator --pre
export CHANGELOG_GITHUB_TOKEN=token
~/.gem/ruby/2.4.0/bin/github_changelog_generator --user rytilahti --project python-miio --since-tag $PREVIOUS_RELEASE --future-release $NEW_RELEASE -o newchanges
```

3. Copy the changelog block over to CHANGELOG.md and write a short and understandable summary.

4. Commit the changed files

```
git commit -av
```

5. Tag a release (and add short changelog as a tag commit message)

```bash
git tag -a $NEW_RELEASE
```

6. Push to git

```bash
git push --tags
```

7. Upload new version to pypi

If not done already, create an API key for pypi (https://pypi.org/manage/account/token/) and configure it:
```
poetry config pypi-token.pypi <token>
```

To build & release:

```bash
poetry build
poetry publish
```

8. Click the "Draft a new release" button on github, select the new tag and copy & paste the changelog into the description.
