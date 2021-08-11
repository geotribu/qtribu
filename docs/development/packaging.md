# Packaging and deployment

## Packaging

This plugin is using the [qgis-plugin-ci](https://github.com/opengisch/qgis-plugin-ci/) tool to perform packaging operations.

```bash
qgis-plugin-ci package 1.3.1
```

## Release a version

Everything is done through the continuous deployment:

1. Fillfull the `CHANGELOG.md`
2. Apply a git tag with the relevant version: `git tag -a 1.3.1 {git commit hash} -m "This version rocks!"`
3. Push tag to main branch: `git push origin 1.3.1`
