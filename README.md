# C++ Package Manager

A lightweight C++ package manager designed to streamline the process of cloning, extracting, organizing, and managing C++ libraries from GitHub repositories or custom sources. This tool allows developers to manage library dependencies efficiently with options for customization in include paths, build system creation, and installation management.

## Features

- Clone repositories from GitHub with optional API keys for private repositories.
- Automatically extract header and source files from the repository, excluding test, example, and other irrelevant files.
- Update `#include` paths in extracted files to ensure compatibility with the specified project structure.
- Supports both CMake and Makefile build systems with user-configurable options.
- Install, list, and uninstall C++ libraries, tracking installed libraries in `packages.json`.
- Download specific libraries (e.g., `nlohmann`) from known URLs if only the library name is provided.

## Requirements

- Python 3.6+
- [GitPython](https://pypi.org/project/GitPython/) for handling Git operations
- [Rich](https://pypi.org/project/rich/) for enhanced console output
- `git` CLI installed on your system

To install the dependencies, run:
```bash
pip install gitpython rich
```
## Installation
```bash
git clone https://github.com/Inas1234/Mlin_Pkg.git
cd Mlin_Pkg
```
## Usage
### Commands
The package manager provides three main commands: `install`, `uninstall`, and `list`.
### Install a Library
To install a library, you can specify either a GitHub URL or a known library name (e.g., `nlohmann`).
#### Example 1: Installing from GitHub URL
```bash
python main.py install -u <github_repo_url> --include-folder <include_folder>
```
- `-u`: Indicates a GitHub URL (required for GitHub repositories).
- `--include-folder`: (Optional) Specifies the folder to store headers and sources. Default is `include`.
#### Example 2: Installing by Library Name
```bash
python main.py install nlohmann --include-folder <include_folder>
```
This command downloads the `nlohmann` library from its official URL, extracts it, and organizes the files in the specified include folder.

### Uninstall a Library
To uninstall a previously installed library:

```bash
python main.py uninstall <username/repo_name> --include-folder <include_folder>
```
- `<username/repo_name>`: The unique identifier of the library.
- `--include-folder`: (Optional) Specifies the folder where the library was installed. Default is `include`.
### List Installed Libraries
To list all installed libraries:

```bash
python main.py list
```
### Customizing the Build System
During installation, the tool prompts for your preferred build system:

- `CMake`: Generates a `CMakeLists.txt` file for managing dependencies.
- `Makefile`: Creates a `Makefile` with customizable compiler and flags.
Both options automatically set up the include paths and library linking for easy integration into your project.

## Configuration
- `secret.txt`: Stores API keys for accessing private repositories. The first line should contain the API key. This is optional you can but it is not necessary to have the file.
- `packages.json`: Tracks installed packages and versions for easy management and updates.
## Example Workflow
Install a library:

```bash
python main.py install -u https://github.com/user/repo.git
```
Uninstall the library:

```bash
python main.py uninstall user/repo
```
List all installed libraries:

```bash
python main.py list
```
## Contributing
Feel free to contribute to this project by submitting a pull request. Make sure to include tests for any new features or fixes and adhere to the project's coding style.

## License
This project is licensed under the MIT License. See [LICENSE](https://github.com/Inas1234/Mlin_Pkg/blob/main/LICENSE.txt) for details.







