import argparse
import git
import os
import shutil
import subprocess
import json
from rich import print
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

secret_file = open("secret.txt", "r")
list = secret_file.readlines()
secret_code = list[0]

def clone_repository(repo_url, dest_folder, api_key=None):
    if api_key:
        repo_url = repo_url.replace("https://", f"https://{api_key}@")

    repo_name = repo_url.split('/')[-1].replace('.git', '')
    username = repo_url.split('/')[-2]
    temp_clone_path = os.path.join(dest_folder, repo_name)  
    if not os.path.exists(temp_clone_path):
        try:
            with Progress(SpinnerColumn(), TextColumn("[bold blue]{task.description}"), console=console) as progress:
                clone_task = progress.add_task(f"Cloning repository '{repo_name}'...", total=None)
                git.Repo.clone_from(repo_url, temp_clone_path)
                progress.remove_task(clone_task)
            console.print(f"[green]Repository '{repo_name}' cloned successfully.[/green]")
        except Exception as e:
            console.print(f"[red]Failed to clone repository: {e}[/red]")
    else:
        console.print(f"[yellow]Repository '{repo_name}' already exists in '{dest_folder}'.[/yellow]")

    return temp_clone_path, username, repo_name

def update_include_paths(file_path, dest_folder):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    updated_lines = []
    for line in lines:
        include_file = None
        delimiters = ('', '')  
        if line.startswith('#include "'):
            include_file = os.path.basename(line.split('"')[1])
            delimiters = ('"', '"')
        elif line.startswith('#include <'):
            include_file = os.path.basename(line.split('<')[1].split('>')[0])
            delimiters = ('<', '>')

        if include_file:
            for root, _, files in os.walk(dest_folder):
                if include_file in files:
                    include_path = os.path.abspath(os.path.join(root, include_file))
                    updated_line = f'#include {delimiters[0]}{include_path}{delimiters[1]}\n'
                    updated_lines.append(updated_line)
                    break
            else:
                updated_lines.append(line)
        else:
            updated_lines.append(line)

    with open(file_path, 'w') as file:
        file.writelines(updated_lines)


def extract_headers_and_sources(username, repo_name, repo_path, include_folder):
    dest_path = os.path.join(include_folder, username, repo_name)
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)

    console.print(f"[bold blue]Extracting header and source files from '{repo_name}' to '{username}/{repo_name}'...[/bold blue]")

    exclude_keywords = ["test", "example", "demo", "unit", "custom", "mock", "sample", "temp", "tmp", 
                        "draft", "experimental", "doc", "docs", "cmake", "build", "bak"]
    exclude_includes_keywords = ["test"]

    def should_exclude_by_include(file_path):
        """Return True if any include directive in file references excluded keywords."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.strip().startswith("#include"):
                    if any(keyword in line.lower() for keyword in exclude_includes_keywords):
                        return True
        return False

    header_files = []  # Track copied header files for later source file check

    with Progress(SpinnerColumn(), TextColumn("[bold blue]{task.description}"), console=console) as progress:
        # First pass: Copy header files
        copy_task = progress.add_task("Copying header files...", total=None)
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith(('.h', '.hpp')) and not any(keyword in file.lower() for keyword in exclude_keywords):
                    source_path = os.path.join(root, file)
                    if should_exclude_by_include(source_path):
                        console.print(f"[yellow]Skipping header '{file}' due to 'test' in include headers.[/yellow]")
                        continue
                    dest_file_path = os.path.join(dest_path, file)
                    shutil.copy2(source_path, dest_file_path)
                    header_files.append(file)  # Keep track of copied headers
                    console.print(f"[green]Copied header '{file}' to '{dest_path}'.[/green]")
        progress.remove_task(copy_task)

        # Second pass: Copy source files that match the header files
        copy_task = progress.add_task("Copying matching source files...", total=None)
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith(('.c', '.cpp', '.cc')):
                    base_name = os.path.splitext(file)[0]
                    if base_name in {os.path.splitext(h)[0] for h in header_files}:
                        source_path = os.path.join(root, file)
                        dest_file_path = os.path.join(dest_path, file)
                        shutil.copy2(source_path, dest_file_path)
                        console.print(f"[green]Copied source '{file}' to '{dest_path}' corresponding to header file '{base_name}'.[/green]")
        progress.remove_task(copy_task)

    # Update include paths after all files have been copied
    console.print("[bold blue]Updating include paths...[/bold blue]")
    for file in os.listdir(dest_path):
        file_path = os.path.join(dest_path, file)
        update_include_paths(file_path, dest_path)
    console.print(f"[green]Include paths updated for all copied files in '{dest_path}'.[/green]")

    console.print(f"[red]Deleting temporary cloned repository at '{repo_path}'...[/red]")
    shutil.rmtree(repo_path)
    console.print(f"[red]Deleted cloned repository at '{repo_path}'.[/red]")

def create_build_system(username, repo_name, include_folder):
    build_dir = os.path.join(os.getcwd(), "build", repo_name)
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)

    console.print(f"[bold blue]Choose a build system for '{username}/{repo_name}':[/bold blue]")
    console.print("1. CMake 2. Makefile")
    choice = console.input("[bold blue]Enter choice (1 or 2): [/bold blue]")
    compiler = console.input("[bold blue]Enter the C++ compiler to use (e.g., g++, clang++): [/bold blue]")

    if choice == '1':
        cmake_content = f"""
cmake_minimum_required(VERSION 3.10)
project({repo_name})
set(CMAKE_CXX_COMPILER {compiler})
include_directories("{include_folder}/{username}/{repo_name}")
file(GLOB SOURCES "{include_folder}/{username}/{repo_name}/*.cpp" "{include_folder}/{username}/{repo_name}/*.c")
add_library({repo_name} STATIC ${{SOURCES}})
        """
        cmake_file_path = os.path.join(build_dir, "CMakeLists.txt")
        with open(cmake_file_path, 'w') as f:
            f.write(cmake_content)
        console.print(f"[green]CMakeLists.txt created in '{build_dir}' for '{username}/{repo_name}'.[/green]")
    elif choice == '2':
        makefile_content = f"""
CXX = {compiler}
CXXFLAGS = -Wall -Wextra -std=c++14 -I../../{include_folder}/{username}/{repo_name}

SOURCES = $(wildcard ../../{include_folder}/{username}/{repo_name}/*.cpp ../../{include_folder}/{username}/{repo_name}/*.c)
OBJECTS = $(SOURCES:.cpp=.o)
OBJECTS := $(OBJECTS:.c=.o)

lib{repo_name}.a: $(OBJECTS)
\tar rcs $@ $(OBJECTS)

%.o: %.cpp
\t$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
\trm -f $(OBJECTS) lib{repo_name}.a
        """
        makefile_path = os.path.join(build_dir, "Makefile")
        with open(makefile_path, 'w') as f:
            f.write(makefile_content)
        console.print(f"[green]Makefile created in '{build_dir}' for '{username}/{repo_name}'.[/green]")
    else:
        console.print(f"[red]Invalid choice. Skipping build system creation for '{username}/{repo_name}'.[/red]")

def record_package(username, repo_name):
    package_record = "packages.json"
    if not os.path.exists(package_record):
        with open(package_record, 'w') as f:
            json.dump({}, f)

    with open(package_record, 'r') as f:
        packages = json.load(f)

    package_key = f"{username}/{repo_name}"
    if package_key not in packages:
        packages[package_key] = {"version": "latest"}

    with open(package_record, 'w') as f:
        json.dump(packages, f, indent=4)

    console.print(f"[green]Package '{package_key}' recorded successfully.[/green]")

def uninstall_package(username, repo_name, include_folder):
    try:
        repo_path = os.path.join(include_folder, username, repo_name)
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
            console.print(f"[red]Removed '{username}/{repo_name}' from include folder.[/red]")

        package_record = "packages.json"
        if os.path.exists(package_record):
            with open(package_record, 'r') as f:
                packages = json.load(f)

            package_key = f"{username}/{repo_name}"
            if package_key in packages:
                del packages[package_key]

            with open(package_record, 'w') as f:
                json.dump(packages, f, indent=4)

        console.print(f"[green]Package '{username}/{repo_name}' uninstalled successfully.[/green]")
    except Exception as e:
        console.print(f"[red]Failed to uninstall package: {e}[/red]")


def build_package(repo_name):
    build_path = os.path.join(os.getcwd(), "build", repo_name)

    if not os.path.exists(build_path):
        console.print(f"[red]Build path '{build_path}' does not exist.[/red]")
        return

    try:
        os.chdir(build_path)
        
        if os.path.exists("Makefile"):
            console.print("[bold blue]Building with Makefile...[/bold blue]")
            subprocess.run(["make"], check=True)
        elif os.path.exists("CMakeLists.txt"):
            console.print("[bold blue]Building with CMake...[/bold blue]")
            subprocess.run(["cmake", "."], check=True)
            subprocess.run(["make"], check=True)
        else:
            console.print("[red]No Makefile or CMakeLists.txt found in the build directory.[/red]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Failed to build package: {e}[/red]")
    except Exception as e:
        console.print(f"[red]An error occurred: {e}[/red]")
    finally:
        os.chdir(os.getcwd())


def download_specific_library(library_name, dest_folder):
    if library_name.lower() == "nlohmann":
        url = "https://github.com/nlohmann/json"
        temp_dest_path = os.path.join(dest_folder, f"{library_name}_temp")
        final_dest_path = os.path.join(dest_folder, library_name)
        
        if not os.path.exists(final_dest_path):
            console.print(f"[bold blue]Downloading '{library_name}' from '{url}'...[/bold blue]")
            clone_repository(url, temp_dest_path, secret_code)
            
            single_include_path = os.path.join(temp_dest_path, "json", "single_include")
            if os.path.exists(single_include_path):
                os.makedirs(final_dest_path, exist_ok=True)
                
                for item in os.listdir(single_include_path):
                    source_path = os.path.join(single_include_path, item)
                    dest_path = os.path.join(final_dest_path, item)
                    if os.path.isdir(source_path):
                        shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                    else:
                        shutil.copy2(source_path, dest_path)
                        
                console.print(f"[green]Copied contents from 'json/single_include' to '{final_dest_path}'.[/green]")
            else:
                console.print(f"[red]The path 'json/single_include' does not exist in the cloned repository.[/red]")
            
            shutil.rmtree(temp_dest_path)
            console.print(f"[red]Deleted temporary cloned repository at '{temp_dest_path}'.[/red]")
        else:
            console.print(f"[yellow]Library '{library_name}' already exists in '{dest_folder}'.[/yellow]")


def main():
    parser = argparse.ArgumentParser(description="C++ Package Manager")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    install_parser = subparsers.add_parser('install', help='Install a C++ package from a GitHub repository URL')
    install_parser.add_argument('library', type=str, help='Library name or GitHub URL')
    install_parser.add_argument('-u', action='store_true', help='Flag to indicate GitHub URL')
    install_parser.add_argument('--include-folder', type=str, default='include', help='Folder to store header and source files')

    uninstall_parser = subparsers.add_parser('uninstall', help='Uninstall a previously installed package')
    uninstall_parser.add_argument('repo_name', type=str, help='Name of the repository to uninstall')
    uninstall_parser.add_argument('--include-folder', type=str, default='include', help='Folder to remove header and source files from')

    list_parser = subparsers.add_parser('list', help='List all installed packages')

    args = parser.parse_args()

    if args.command == 'install':
        if args.u:
            temp_clone_path, username, repo_name = clone_repository(args.library, args.include_folder, api_key=secret_code)
            extract_headers_and_sources(username, repo_name, temp_clone_path, args.include_folder)
            create_build_system(username, repo_name, args.include_folder)
            record_package(username, repo_name)
            build_package(repo_name)
        else:
            download_specific_library(args.library, args.include_folder)
            record_package(args.library, args.library)

    elif args.command == 'uninstall':
        repo_name = args.repo_name.split('/')[-1]
        username = args.repo_name.split('/')[0]
        uninstall_package(username, repo_name, args.include_folder)
    elif args.command == 'list':
        pass
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
