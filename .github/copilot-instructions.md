<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->
- [x] Verify that the copilot-instructions.md file in the .github directory is created.

- [x] Clarify Project Requirements
	<!-- Python workspace with virtual environment and start script specified by user. -->

- [x] Scaffold the Project
	<!-- Created Python project structure with main.py, requirements.txt, start.sh, and README.md -->

- [x] Customize the Project
	<!-- Skipped - Hello World project as requested -->

- [x] Install Required Extensions
	<!-- No extensions specified by project setup info -->

- [x] Compile the Project
	<!-- Virtual environment created and dependencies installed successfully -->

- [x] Create and Run Task
	<!-- Created and executed "Run Python App" task successfully -->

- [x] Launch the Project
	<!-- Project launched successfully via task execution -->

- [x] Ensure Documentation is Complete
	<!-- README.md and copilot-instructions.md created and contain current project information -->

## Project-Specific Guidelines

### File Organization Rules
- **Test data files**: Always place test data files in `inputs/` or `outputs/` folders
- **Input test files**: Create in `inputs/` folder (e.g., `inputs/test_simple.txt`)
- **Output test files**: Create in `outputs/` folder (e.g., `outputs/test_result.txt`)
- **Unit test scripts**: Place in root directory or `tests/` folder (e.g., `test_timestamp_adjuster.py`)
- **Never create test data files in root directory** - they may accidentally get committed to git
- Use descriptive names for test files to identify their purpose

### Development Practices
- All test data should use the established folder structure
- Unit test scripts belong in `/tests/` directory with proper module organization
- Follow the existing naming conventions for consistency
- Respect the .gitignore configuration for inputs/* and outputs/*

### Test-Driven Development Rules
- **ALWAYS run tests after making code changes**: Execute `./run_tests.sh` after any modification to main.py, config.py, or test files
- **Test validation is mandatory**: All 26 unit tests must pass before considering any change complete
- **Test organization**: Use the modular test structure in `/tests/` directory:
  - `test_parsing.py` - Timestamp parsing functionality
  - `test_formatting.py` - Timestamp formatting functionality  
  - `test_adjustment.py` - Timestamp adjustment logic
  - `test_config.py` - Configuration management
  - `test_file_processing.py` - File I/O operations
  - `test_integration.py` - End-to-end testing
- **Create new tests**: When adding new functionality, create corresponding test cases in the appropriate test module
- **Fix broken tests**: If tests fail after changes, investigate and fix both the code and tests as needed
- **Test coverage**: Maintain comprehensive test coverage for all core functionality

### Code Quality Standards
- Maintain compatibility with existing YAML configuration system
- Preserve backward compatibility for CLI interface
- Follow Python best practices and type hints where applicable
- Ensure proper error handling and user feedback
