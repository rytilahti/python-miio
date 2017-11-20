1. Update the version number

nano miio/version.py

2. Generate changelog since the last release

~/.gem/ruby/2.4.0/bin/github_changelog_generator --user rytilahti --project python-miio --since-tag 0.3.0 -o newchanges

3. Copy the changelog block over to CHANGELOG.md and write a short, understandable short changelog

4. Commit modified CHANGELOG.md

5. Tag a release (and add short changelog as a tag commit message)

tag -a 0.3.1

6. Push to git

git push --tags

7. Upload new version to pypi

python setup.py sdist bdist_wheel upload
