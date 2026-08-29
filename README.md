# GitHub Actions Fixes

Python and Node.js scripts that detect and repair GitHub Actions problems — empty secrets in fork PRs, silent cache misses and redundant billed runs.

Every fix is safe by default. The scripts start in a dry run mode that reports what they would do, so you can read the plan before anything writes.

By **[Allan Niñal](https://github.com/allanninal)** — AI Solutions Engineer. I build AI powered tools, data products, and AWS automation.
Full write ups with diagrams for each fix live at **[allanninal.dev/ci](https://www.allanninal.dev/ci/)**.

[![Follow on GitHub](https://img.shields.io/github/followers/allanninal?label=Follow%20%40allanninal&style=social)](https://github.com/allanninal)
[![Tests](https://github.com/allanninal/github-actions-fixes/actions/workflows/tests.yml/badge.svg)](https://github.com/allanninal/github-actions-fixes/actions/workflows/tests.yml)

## The fixes

- [a cache miss that is really a rate limit](./cache-miss-is-really-a-rate-limit/) — https://www.allanninal.dev/ci/cache-miss-is-really-a-rate-limit/
- [GITHUB_TOKEN is read-only and the error just says 403](./github-token-is-read-only-by-default/) — https://www.allanninal.dev/ci/github-token-is-read-only-by-default/
- [three pushes run three full pipelines and you pay for all of them](./redundant-runs-on-rapid-pushes/) — https://www.allanninal.dev/ci/redundant-runs-on-rapid-pushes/
- [secrets are empty strings in fork pull requests](./secrets-are-empty-in-fork-pull-requests/) — https://www.allanninal.dev/ci/secrets-are-empty-in-fork-pull-requests/

## How to run one

Each folder holds the same script in Python and in Node.js, plus its test. Set the environment variables named in that folder's README, keep `DRY_RUN=true` for the first pass, and read what it reports before letting it write.

## License

MIT. Use it, change it, ship it.
