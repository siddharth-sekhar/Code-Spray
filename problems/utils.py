import subprocess
import tempfile
import os
import shutil
import time
import errno
import platform

#
LANGUAGE_CONFIG = {
    'c': {
        'source_file': 'main.c',
        'exe_file': 'main_exe.exe',
        'compile_cmd': ['gcc', 'main.c', '-o', 'main_exe.exe'],
        'run_cmd': ['./main_exe.exe'] if platform.system() != 'Windows' else ['main_exe.exe'],
    },
    'cpp': {
        'source_file': 'main.cpp',
        'exe_file': 'main_exe.exe',
        'compile_cmd': ['g++', 'main.cpp', '-o', 'main_exe.exe'],
        'run_cmd': ['./main_exe.exe'] if platform.system() != 'Windows' else ['main_exe.exe'],
    },
    'java': {
        'source_file': 'Main.java',
        'compile_cmd': ['javac', 'Main.java'],
        'run_cmd': ['java', 'Main'],
    },
    'python': {
        'source_file': 'main.py',
        'run_cmd': ['python', 'main.py'],
    },
}

def find_compiler(compiler_name):
    """Try to find the compiler in common locations"""
    if platform.system() == 'Windows':

        common_paths = [
            r'C:\MinGW\bin',
            r'C:\mingw64\bin',
            r'C:\TDM-GCC-64\bin',
            r'C:\Program Files\mingw-w64\x86_64-8.1.0-posix-seh-rt_v6-rev0\mingw64\bin',
            r'C:\Program Files (x86)\mingw-w64\i686-8.1.0-posix-dwarf-rt_v6-rev0\mingw32\bin',
        ]
        
        for path in common_paths:
            compiler_path = os.path.join(path, f'{compiler_name}.exe')
            if os.path.exists(compiler_path):
                return compiler_path

    try:
        result = subprocess.run(['which', compiler_name] if platform.system() != 'Windows' else ['where', compiler_name], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip().split('\n')[0]
    except:
        pass
    
    return compiler_name

def compile_and_run(code: str, lang: str, input_data: str):
    """
    Compiles and runs code submitted by the user.
    :param code: The source code submitted.
    :param lang: One of 'c', 'cpp', 'java', 'python'
    :param input_data: Sample input for the program.
    :return: Tuple of (stdout, stderr)
    """
    if lang not in LANGUAGE_CONFIG:
        return '', f" Language '{lang}' not supported."

    config = LANGUAGE_CONFIG[lang].copy()

    # Find the correct compiler
    if 'compile_cmd' in config:
        if lang in ['c', 'cpp']:
            compiler_name = 'gcc' if lang == 'c' else 'g++'
            found_compiler = find_compiler(compiler_name)
            config['compile_cmd'] = [found_compiler] + config['compile_cmd'][1:]

    tmpdir = tempfile.mkdtemp()
    try:
        source_path = os.path.join(tmpdir, config['source_file'])

        # Write user-submitted code to file
        with open(source_path, 'w', encoding='utf-8') as code_file:
            code_file.write(code)

        # ---------------------
        # 1. Compilation Phase
        # ---------------------
        if 'compile_cmd' in config:
            try:
                compile_result = subprocess.run(
                    config['compile_cmd'],
                    cwd=tmpdir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=10
                )
                if compile_result.returncode != 0:
                    stderr_output = compile_result.stderr.decode('utf-8', errors='ignore')
                    return '', f" Compilation Error:\n{stderr_output}"
            except FileNotFoundError:
                return '', f" Compiler not found. Please install {lang.upper()} compiler."
            except subprocess.TimeoutExpired:
                return '', "⏱ Compilation Time Limit Exceeded"

        # ---------------------
        # 2. Execution Phase
        # ---------------------
        try:
            # For Windows, check if executable exists
            if platform.system() == 'Windows' and 'exe_file' in config:
                exe_path = os.path.join(tmpdir, config['exe_file'])
                if not os.path.exists(exe_path):
                    return '', f" Executable not found at {exe_path}. Compilation may have failed."
            
            # Update run command to use full path for Windows executables
            if platform.system() == 'Windows' and 'exe_file' in config:
                exe_path = os.path.join(tmpdir, config['exe_file'])
                run_cmd = [exe_path]
            else:
                run_cmd = config['run_cmd']
            
            run_result = subprocess.run(
                run_cmd,
                cwd=tmpdir,
                input=input_data.encode('utf-8'),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )

            stdout = run_result.stdout.decode('utf-8', errors='ignore').strip()
            stderr = run_result.stderr.decode('utf-8', errors='ignore').strip()
            
            # If there's stderr but no stdout, it might be an error
            if stderr and not stdout:
                return '', f" Runtime Error:\n{stderr}"
            
            return stdout, stderr

        except subprocess.TimeoutExpired:
            return '', "⏱️ Time Limit Exceeded"
        except FileNotFoundError as e:
            return '', f" File not found error: {str(e)}"

    except Exception as e:
        return '', f" Unexpected error: {str(e)}"

    finally:
        try:
            shutil.rmtree(tmpdir)
        except PermissionError as e:
            # Handle Windows locked file case gracefully
            for _ in range(5):
                time.sleep(0.2)
                try:
                    shutil.rmtree(tmpdir)
                    break
                except PermissionError as retry_err:
                    if retry_err.errno != errno.EACCES:
                        raise
            else:
                # Could not delete temp folder after retries — log or ignore
                pass
