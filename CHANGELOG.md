# CHANGELOG

<!-- version list -->

## v1.0.0 (2026-04-12)

- Initial Release

## v9.8.2 (2025-12-15)

### Bug Fixes

- Allow home subdirectories through is_dangerous_path()
  ([`e5548ac`](

- Path traversal vulnerability - use prefix matching in is_dangerous_path()
  ([`9ed15f4`](

- Use Path.is_relative_to() for cross-platform dangerous path detection
  ([`91ffb51`](

- **security**: Handle macOS symlinked system dirs
  ([`ba08308`](

### Chores

- Sync version to config.py [skip ci]
  ([`c492735`](


## v9.8.1 (2025-12-15)

### Bug Fixes

- **providers**: Omit store parameter for OpenRouter responses endpoint
  ([`1f8b58d`](

### Chores

- Sync version to config.py [skip ci]
  ([`69a42a7`](

### Refactoring

- **tests**: Address code review feedback
  ([`0c3e63c`](

- **tests**: Remove unused setUp method
  ([`b6a8d68`](


## v9.8.0 (2025-12-15)

### Chores

- Sync version to config.py [skip ci]
  ([`cb97a89`](

### Features

- Add Claude Opus 4.5 model via OpenRouter
  ([`813ce5c`](

### Testing

- Add comprehensive test coverage for Opus 4.5 aliases
  ([`cf63fd2`](


## v9.7.0 (2025-12-15)

### Chores

- Sync version to config.py [skip ci]
  ([`aa85644`](

### Features

- Re-enable web search for clink codex using correct --enable flag
  ([`e7b9f3a`](


## v9.6.0 (2025-12-15)

### Chores

- Sync version to config.py [skip ci]
  ([`94ff26c`](

### Features

- Support native installed Claude CLI detection
  ([`adc6231`](


## v9.5.0 (2025-12-11)

### Bug Fixes

- Grok test
  ([`39c7721`](

### Chores

- Sync version to config.py [skip ci]
  ([`5c3dd75`](

- Sync version to config.py [skip ci]
  ([`605633b`](

### Documentation

- Cleanup
  ([`74f26e8`](

- Cleanup
  ([`2b22174`](

- Update subheading
  ([`591287c`](

### Features

- GPT-5.2 support
  ([`8b16405`](

- Grok-4.1 support
  ([`514c9c5`](


## v9.4.2 (2025-12-04)

### Bug Fixes

- Rebranding, see [docs/name-change.md](docs/name-change.md) for details
  ([`b2dc849`](

### Chores

- Sync version to config.py [skip ci]
  ([`bcfacce`](


## v9.4.1 (2025-11-21)

### Bug Fixes

- Regression
  ([`aceddb6`](

### Chores

- Sync version to config.py [skip ci]
  ([`c4461a4`](


## v9.4.0 (2025-11-18)

### Bug Fixes

- Failing test for gemini 3.0 pro open router
  ([`19a2a89`](

### Chores

- Sync version to config.py [skip ci]
  ([`d3de61f`](

### Features

- Gemini 3.0 Pro Preview for Open Router
  ([`bbfdfac`](

### Refactoring

- Enable search on codex CLI
  ([`1579d9f`](


## v9.3.1 (2025-11-18)

### Chores

- Sync version to config.py [skip ci]
  ([`d256098`](


## v9.3.0 (2025-11-18)

### Chores

- Sync version to config.py [skip ci]
  ([`3748d47`](


## v9.2.2 (2025-11-18)

### Bug Fixes

- **build**: Include clink resources in package
  ([`e9ac1ce`](

### Chores

- Sync version to config.py [skip ci]
  ([`749bc73`](


## v9.2.1 (2025-11-18)

### Bug Fixes

- **server**: Iterate provider instances during shutdown
  ([`d40fc83`](

### Chores

- Sync version to config.py [skip ci]
  ([`84f6c4f`](


## v9.2.0 (2025-11-18)

### Chores

- Sync version to config.py [skip ci]
  ([`7a1de64`](

### Documentation

- Streamline advanced usage guide by reorganizing table of contents for improved navigation
  ([`698d391`](

- Update .env.example to include new GPT-5.1 model options and clarify existing model descriptions
  ([`dbbfef2`](

- Update advanced usage and configuration to include new GPT-5.1 models and enhance tool parameters
  ([`807c9df`](

### Features

- Add new GPT-5.1 models to configuration files and update model selection logic in OpenAI provider
  ([`8e9aa23`](

- Enhance model support by adding GPT-5.1 to .gitignore and updating cassette maintenance
  documentation for dual-model testing
  ([`f713d8a`](


## v9.1.4 (2025-11-18)

### Bug Fixes

- Replaced deprecated Codex web search configuration
  ([`2ec64ba`](

### Chores

- Sync version to config.py [skip ci]
  ([`4d3d177`](


## v9.1.3 (2025-10-22)

### Bug Fixes

- Reduced token usage, removed parameters from schema that CLIs never seem to use
  ([`3e27319`](

- Telemetry option no longer available in gemini 0.11
  ([`2a8dff0`](

### Chores

- Sync version to config.py [skip ci]
  ([`9e163f9`](

- Sync version to config.py [skip ci]
  ([`557e443`](

### Refactoring

- Improved precommit system prompt
  ([`3efff60`](


## v9.1.2 (2025-10-21)

### Bug Fixes

- Configure codex with a longer timeout
  ([`d2773f4`](

- Handle claude's array style JSON
  ([`d5790a9`](

### Chores

- Sync version to config.py [skip ci]
  ([`04132f1`](


## v9.1.1 (2025-10-17)

### Bug Fixes

- Failing test
  ([`aed3e3e`](

- Handler for parsing multiple generated code blocks
  ([`f4c20d2`](

- Improved error reporting; codex cli would at times fail to figure out how to handle plain-text /
  JSON errors
  ([`95e69a7`](

### Chores

- Sync version to config.py [skip ci]
  ([`942757a`](


## v9.1.0 (2025-10-17)

### Chores

- Sync version to config.py [skip ci]
  ([`3ee0c8f`](

### Features

- Enhance review prompts to emphasize static analysis
  ([`36e66e2`](


## v9.0.4 (2025-10-17)

### Chores

- Sync version to config.py [skip ci]
  ([`8c6f653`](


## v9.0.3 (2025-10-16)

### Bug Fixes

- Remove duplicate -o json flag in gemini CLI config
  ([`3b2eff5`](

### Chores

- Sync version to config.py [skip ci]
  ([`b205d71`](


## v9.0.2 (2025-10-15)

### Bug Fixes

- Update Claude CLI commands to new mcp syntax
  ([`a2189cb`](

### Chores

- Sync version to config.py [skip ci]
  ([`d08cdc6`](


## v9.0.1 (2025-10-14)

### Bug Fixes

- Add JSON output flag to gemini CLI configuration
  ([`eb3dff8`](

### Chores

- Sync version to config.py [skip ci]
  ([`b9408aa`](


## v9.0.0 (2025-10-08)

### Chores

- Sync version to config.py [skip ci]
  ([`23c9b35`](

### Features

- Claude Code as a CLI agent now supported. Mix and match: spawn claude code from within claude
  code, or claude code from within codex.
  ([`4cfaa0b`](


## v8.0.2 (2025-10-08)

### Bug Fixes

- Restore run-server quote trimming regex
  ([`1de4542`](

### Chores

- Sync version to config.py [skip ci]
  ([`728fb43`](


## v8.0.1 (2025-10-08)

### Bug Fixes

- Resolve executable path for cross-platform compatibility in CLI agent
  ([`f98046c`](

### Chores

- Sync version to config.py [skip ci]
  ([`52245b9`](

### Testing

- Fix clink agent tests to mock shutil.which() for executable resolution
  ([`4370be3`](


## v8.0.0 (2025-10-07)

### Chores

- Sync version to config.py [skip ci]
  ([`4c34541`](


## v7.8.1 (2025-10-07)

### Bug Fixes

- Updated model description to fix test
  ([`04f7ce5`](

### Chores

- Sync version to config.py [skip ci]
  ([`c27e81d`](

### Refactoring

- Moved registries into a separate module and code cleanup
  ([`7c36b92`](


## v7.8.0 (2025-10-07)

### Chores

- Sync version to config.py [skip ci]
  ([`3e5fa96`](

### Documentation

- Consensus video
  ([`2352684`](

- Formatting
  ([`7d7c74b`](

- Link to videos from main page
  ([`e8ef193`](

- Update README.md
  ([`7b13543`](

### Features

- All native providers now read from catalog files like OpenRouter / Custom configs. Allows for
  greater control over the capabilities
  ([`2a706d5`](

- Provider cleanup
  ([`9268dda`](

### Refactoring

- New base class for model registry / loading
  ([`02d13da`](


## v7.7.0 (2025-10-07)

### Chores

- Sync version to config.py [skip ci]
  ([`70ae62a`](

### Documentation

- Video
  ([`ed5dda7`](

### Features

- More aliases
  ([`5f0aaf5`](


## v7.6.0 (2025-10-07)

### Chores

- Sync version to config.py [skip ci]
  ([`c1c75ba`](

- Sync version to config.py [skip ci]
  ([`0fa9b66`](

### Documentation

- Info about AI client timeouts
  ([`3ddfed5`](

### Features

- Add support for openai/gpt-5-pro model
  ([`abed075`](


## v7.5.2 (2025-10-06)

### Bug Fixes

- Handle 429 response
  ([`cbe1d79`](

### Chores

- Sync version to config.py [skip ci]
  ([`74fdd36`](


## v7.5.1 (2025-10-06)

### Chores

- Sync version to config.py [skip ci]
  ([`004e379`](


## v7.5.0 (2025-10-06)

### Chores

- Sync version to config.py [skip ci]
  ([`71e7cd5`](

### Documentation

- Video
  ([`775e4d5`](

- Videos
  ([`bb2066c`](

### Features

- Support for GPT-5-Pro highest reasoning model
  ([`a65485a`](


## v7.4.0 (2025-10-06)

### Chores

- Sync version to config.py [skip ci]
  ([`76bf98e`](

### Features

- Improved prompt
  ([`b1e9963`](


## v7.3.0 (2025-10-06)

### Chores

- Sync version to config.py [skip ci]
  ([`e7920d0`](

### Documentation

- Fixed typo
  ([`3ab0aa8`](

- Fixed typo
  ([`c17ce3c`](

- Update apilookup.md
  ([`1918679`](

- Update README.md
  ([`23c6c78`](

### Features

- Codex supports web-search natively but needs to be turned on, run-server script asks if the user
  would like this done
  ([`97ba7e4`](


## v7.2.0 (2025-10-06)

### Chores

- Sync version to config.py [skip ci]
  ([`1854b1e`](

### Documentation

- Updated
  ([`bb57f71`](

### Features

- New tool to perform apilookup (latest APIs / SDKs / language features etc)
  ([`5bea595`](

### Refactoring

- De-duplicate roles to avoid explosion when more CLIs get added
  ([`c42e9e9`](


## v7.1.1 (2025-10-06)

### Bug Fixes

- Clink missing in toml
  ([`1ff77fa`](

### Chores

- Sync version to config.py [skip ci]
  ([`e02e78d`](

### Documentation

- Example for codex cli
  ([`344c42b`](

- Example for codex cli
  ([`c3044de`](

- Update README.md
  ([`2e719ae`](


## v7.1.0 (2025-10-05)

### Chores

- Sync version to config.py [skip ci]
  ([`d54bfdd`](

### Features

- Support for codex as external CLI
  ([`561e4aa`](


## v7.0.2 (2025-10-05)

### Chores

- Sync version to config.py [skip ci]
  ([`f2142a2`](


## v7.0.1 (2025-10-05)

### Bug Fixes

- --yolo needed for running shell commands, documentation added
  ([`15ae3f2`](

### Chores

- Sync version to config.py [skip ci]
  ([`bc4a27b`](

### Documentation

- Updated intro
  ([`fb668c3`](


## v7.0.0 (2025-10-05)

### Chores

- Sync version to config.py [skip ci]
  ([`0d46976`](

- Sync version to config.py [skip ci]
  ([`8296bf8`](

### Documentation

- Instructions for OpenCode
  ([`bd66622`](

- Updated intro
  ([`615873c`](

### Features

- Huge update - Link another CLI (such as `gemini` directly from with Claude Code / Codex).
  ([`a2ccb48`](

### Refactoring

- Fixed test
  ([`9c99b9b`](

- Include file modification dates too
  ([`47973e9`](


## v6.1.0 (2025-10-04)

### Chores

- Sync version to config.py [skip ci]
  ([`18095d7`](

### Documentation

- Updated intro
  ([`aa65394`](

### Features

- Support for Qwen Code
  ([`fe9968b`](


## v6.0.0 (2025-10-04)

### Chores

- Sync version to config.py [skip ci]
  ([`ae8749a`](

### Documentation

- Updated
  ([`e91ed2a`](

### Features

- Azure OpenAI / Azure AI Foundry support. Models should be defined in conf/azure_models.json (or a
  custom path). See .env.example for environment variables or see readme.
  ([`ff9a07a`](

- Breaking change - OpenRouter models are now read from conf/openrouter_models.json while Custom /
  Self-hosted models are read from conf/custom_models.json
  ([`ff9a07a`](

- OpenAI/compatible models (such as Azure OpenAI) can declare if they use the response API instead
  via `use_openai_responses_api`
  ([`3824d13`](

- OpenRouter / Custom Models / Azure can separately also use custom config paths now (see
  .env.example )
  ([`ff9a07a`](

### Refactoring

- Breaking change: `is_custom` property has been removed from model_capabilities.py (and thus
  custom_models.json) given each models are now read from separate configuration files
  ([`ff9a07a`](

- Model registry class made abstract, OpenRouter / Custom Provider / Azure OpenAI now subclass these
  ([`ff9a07a`](


## v5.22.0 (2025-10-04)

### Bug Fixes

- CI test
  ([`bc93b53`](

- Listmodels to always honor restricted models
  ([`4015e91`](

### Chores

- Sync version to config.py [skip ci]
  ([`054e34e`](

- Sync version to config.py [skip ci]
  ([`c0334d7`](

### Features

- Centralized environment handling, ensures PAL_MCP_FORCE_ENV_OVERRIDE is honored correctly
  ([`2c534ac`](

### Refactoring

- Don't retry on 429
  ([`d184024`](

- Improved retry logic and moved core logic to base class
  ([`f955100`](

- Removed subclass override when the base class should be resolving the model name
  ([`06d7701`](


## v5.21.0 (2025-10-03)

### Chores

- Sync version to config.py [skip ci]
  ([`ddb20a6`](


## v5.20.1 (2025-10-03)

### Chores

- Sync version to config.py [skip ci]
  ([`03addcf`](


## v5.20.0 (2025-10-03)

### Chores

- Sync version to config.py [skip ci]
  ([`539bc72`](


## v5.19.0 (2025-10-03)

### Bug Fixes

- Add GPT-5-Codex to Responses API routing and simplify comments
  ([`82b021d`](

### Chores

- Sync version to config.py [skip ci]
  ([`8e32ef3`](

### Documentation

- Bumped defaults
  ([`95d98a9`](

### Features

- Add GPT-5-Codex support with Responses API integration
  ([`f265342`](

### Testing

- Cross tool memory recall, testing continuation via cassette recording
  ([`88493bd`](


## v5.18.3 (2025-10-03)

### Bug Fixes

- External model name now recorded properly in responses
  ([`d55130a`](

### Chores

- Sync version to config.py [skip ci]
  ([`5714e20`](

### Documentation

- Updated docs
  ([`b4e5090`](

### Refactoring

- Generic name for the CLI agent
  ([`e9b6947`](

- Generic name for the CLI agent
  ([`7a6fa0e`](

- Generic name for the CLI agent
  ([`b692da2`](

- Generic name for the CLI agent
  ([`f76ebbf`](

- Generic name for the CLI agent
  ([`c05913a`](

- Generic name for the CLI agent
  ([`0dfaa63`](

### Testing

- Fixed integration tests, removed magicmock
  ([`87ccb6b`](


## v5.18.2 (2025-10-02)

### Bug Fixes

-
  ([`8b3a286`](

### Chores

- Sync version to config.py [skip ci]
  ([`bf2196c`](


## v5.18.1 (2025-10-02)

### Chores

- Sync version to config.py [skip ci]
  ([`e434a26`](


## v5.18.0 (2025-10-02)

### Chores

- Sync version to config.py [skip ci]
  ([`e78fe35`](

### Features

- Added `intelligence_score` to the model capabilities schema; a 1-20 number that can be specified
  to influence the sort order of models presented to the CLI in `auto selection` mode
  ([`6cab9e5`](


## v5.17.4 (2025-10-02)

### Chores

- Sync version to config.py [skip ci]
  ([`a6c9b92`](


## v5.17.3 (2025-10-02)

### Chores

- Sync version to config.py [skip ci]
  ([`722f6f8`](


## v5.17.2 (2025-10-02)

### Chores

- Sync version to config.py [skip ci]
  ([`e47a7e8`](


## v5.17.1 (2025-10-02)

### Bug Fixes

- Baseclass should return MODEL_CAPABILITIES
  ([`82a03ce`](

### Chores

- Sync version to config.py [skip ci]
  ([`7ce66bd`](

### Documentation

- Document custom timeout values
  ([`218fbdf`](

### Refactoring

- Clean temperature inference
  ([`9c11ecc`](

- Cleanup
  ([`6ec2033`](

- Cleanup provider base class; cleanup shared responsibilities; cleanup public contract
  ([`693b84d`](

- Cleanup token counting
  ([`7fe9fc4`](

- Code cleanup
  ([`bb138e2`](

- Code cleanup
  ([`182aa62`](

- Moved image related code out of base provider into a separate utility
  ([`14a35af`](

- Moved temperature method from base provider to model capabilities
  ([`6d237d0`](

- Moved temperature method from base provider to model capabilities
  ([`f461cb4`](

- Removed hard coded checks, use model capabilities instead
  ([`250545e`](

- Removed hook from base class, turned into helper static method instead
  ([`2b10adc`](

- Removed method from provider, should use model capabilities instead
  ([`a254ff2`](

- Renaming to reflect underlying type
  ([`1dc25f6`](


## v5.17.0 (2025-10-02)

### Bug Fixes

- Use types.HttpOptions from module imports instead of local import
  ([`956e8a6`](

### Chores

- Sync version to config.py [skip ci]
  ([`0836213`](

### Code Style

- Apply Black formatting to use double quotes
  ([`33ea896`](

### Features

- Add custom Gemini endpoint support
  ([`462bce0`](

### Refactoring

- Simplify Gemini provider initialization using kwargs dict
  ([`023940b`](


## v5.16.0 (2025-10-01)

### Bug Fixes

- Resolve logging timing and import organization issues
  ([`d34c299`](

### Chores

- Sync version to config.py [skip ci]
  ([`b6c4bca`](

### Code Style

- Fix ruff import sorting issue
  ([`4493a69`](

### Features

- Add configurable environment variable override system
  ([`93ce698`](


## v5.15.0 (2025-10-01)

### Chores

- Sync version to config.py [skip ci]
  ([`b0fe956`](

### Features

- Depending on the number of tools in use, this change should save ~50% of overall tokens used.
  fixes but also refactored
  individual tools to instead encourage the agent to use the listmodels tool if needed.
  ([`d9449c7`](

### Performance Improvements

- Tweaks to schema descriptions, aiming to reduce token usage without performance degradation
  ([`cc8a4df`](

### Refactoring

- Trimmed some prompts
  ([`f69ff03`](


## v5.14.1 (2025-10-01)

### Bug Fixes

-
  ([`696b45f`](

### Chores

- Sync version to config.py [skip ci]
  ([`692016c`](


## v5.14.0 (2025-10-01)

### Chores

- Sync version to config.py [skip ci]
  ([`c0f822f`](

### Features

- Add Claude Sonnet 4.5 and update alias configuration
  ([`95c4822`](

### Testing

- Update tests to match new Claude Sonnet 4.5 alias configuration
  ([`7efb409`](


## v5.13.0 (2025-10-01)

### Bug Fixes

- Add sonnet alias for Claude Sonnet 4.1 to match opus/haiku pattern
  ([`dc96344`](

- Missing "optenai/" in name
  ([`7371ed6`](

### Chores

- Sync version to config.py [skip ci]
  ([`b8479fc`](

### Features

- Add comprehensive GPT-5 series model support
  ([`4930824`](


## v5.12.1 (2025-10-01)

### Bug Fixes

- Resolve consensus tool model_context parameter missing issue
  ([`9044b63`](

### Chores

- Sync version to config.py [skip ci]
  ([`e3ebf4e`](

### Code Style

- Fix trailing whitespace in consensus.py
  ([`0760b31`](

### Refactoring

- Optimize ModelContext creation in consensus tool
  ([`30a8952`](


## v5.12.0 (2025-10-01)

### Bug Fixes

- Removed use_websearch; this parameter was confusing Codex. It started using this to prompt the
  external model to perform searches! web-search is enabled by Claude / Codex etc by default and the
  external agent can ask claude to search on its behalf.
  ([`cff6d89`](

### Chores

- Sync version to config.py [skip ci]
  ([`28cabe0`](

### Features

- Implement semantic cassette matching for o3 models
  ([`70fa088`](


## v5.11.2 (2025-10-01)

### Chores

- Sync version to config.py [skip ci]
  ([`4d6f1b4`](


## v5.11.1 (2025-10-01)

### Bug Fixes

- Remove duplicate OpenAI models from listmodels output
  ([`c29e762`](

### Chores

- Sync version to config.py [skip ci]
  ([`1209064`](

### Testing

- Update OpenAI provider alias tests to match new format
  ([`d13700c`](


## v5.11.0 (2025-08-26)

### Chores

- Sync version to config.py [skip ci]
  ([`9735469`](

### Features

- Codex CLI support
  ([`ce56d16`](


## v5.10.3 (2025-08-24)

### Bug Fixes

- Address test failures and PR feedback
  ([`6bd9d67`](

- Resolve temperature handling issues for O3/custom models
  ([#245](
  [`3b4fd88`](

### Chores

- Sync version to config.py [skip ci]
  ([`d6e6808`](


## v5.10.2 (2025-08-24)

### Bug Fixes

- Another fix for
  ([`a07036e`](

### Chores

- Sync version to config.py [skip ci]
  ([`9da5c37`](


## v5.10.0 (2025-08-22)

### Chores

- Sync version to config.py [skip ci]
  ([`1254205`](

### Features

- Refactored and tweaked model descriptions / schema to use fewer tokens at launch (average
  reduction per field description: 60-80%) without sacrificing tool effectiveness
  ([`4b202f5`](


## v5.9.0 (2025-08-21)

### Documentation

- Update instructions for precommit
  ([`90821b5`](

### Features

- Refactored and improved codereview in line with precommit. Reviews are now either external
  (default) or internal. Takes away anxiety and loss of tokens when Claude incorrectly decides to be
  'confident' about its own changes and bungle things up.
  ([`80d21e5`](

### Refactoring

- Minor prompt tweaks
  ([`d30c212`](


## v5.8.6 (2025-08-20)

### Bug Fixes

- Escape backslashes in TOML regex pattern
  ([`1c973af`](

- Establish version 5.8.6 and add version sync automation
  ([`90a4195`](

- Restore proper version 5.8.6
  ([`340b58f`](

### Chores

- Sync version to config.py [skip ci]
  ([`4f82f65`](


## v1.1.0 (2025-08-20)

### Features

- Improvements to precommit
  ([`2966dcf`](


## v1.0.0 (2025-08-20)

- Initial Release
