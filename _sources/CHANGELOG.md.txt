# Changelog
All notable changes to the hollywood_pub_sub project will be documented in this file

## [0.1.2] - 2025-08-03
### Added
- Include *CHANGELOG.md* and *README.md* in sphinx documentation
- Add linter
### Changed
- Rename CI jobs
- Pass Docker image as container
### Fixed
- Install required group depedencies for each CI job
- Use built Docker image in all CI jobs

## [0.1.1] - 2025-07-31
### Added
- Auto generate sphinx documentation with pdm command
- Add CI job for building sphinx documentation

## [0.1.0] - 2025-07-30
### Added
- Add pre-commit hooks
- Add file *CHANGELOG.md*
- Add CI job for running main with JSON file
### Changed
- Add inheritance between movie database classes
- Use pydantic RootModel for loading JSON file
- When loading movie database JSON file, retrieve composers list from content
- Rework unit tests
- Split CI run-main parent job into 2 children jobs (run with TMDb API key and JSON file)
