# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.4.0] - 2024-09-25

### Added

- Slack notifier

### Changed

- Refactored and optimized PostgresRepository, FeatureFlagService, and BaseRepository.
- Implemented proper type hinting across all components.
- Enhanced error handling and logging mechanisms.

## [0.3.1]

### Added

- Fixing the bug in Redis cache data retrieval and ensuring correct fetching of cached data from Redis.

## [0.3.0]

### Added

- Updating enable / disable, update, get based on the code instead of id
- List feature flags based on the offset and skip

## [0.2.0]

### Added

- First release with CRUD operations for feature flags
- Use AsyncSession for database connection and Redis Cluster
