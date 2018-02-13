1. Update the version number

```bash
nano miio/version.py
```

2. Generate changelog since the last release

```bash
# gem install github_changelog_generator --pre
export CHANGELOG_GITHUB_TOKEN=token
~/.gem/ruby/2.4.0/bin/github_changelog_generator --user rytilahti --project python-miio --since-tag 0.3.0 -o newchanges
```

3. Copy the changelog block over to CHANGELOG.md and write a short and understandable summary.

4. Commit the changed files

```
git commit -av
```

5. Tag a release (and add short changelog as a tag commit message)

```bash
git tag -a 0.3.1
```

6. Push to git

```bash
git push --tags
```

7. Upload new version to pypi

```bash
python setup.py sdist bdist_wheel upload
```

8. Click the "Draft a new release" button on github, select the new tag and copy & paste the changelog into the description.
