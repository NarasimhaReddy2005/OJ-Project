import os
import subprocess
import tempfile
from django.conf import settings

LANGUAGE_HANDLERS = {
    'cpp': {
        'source_ext': '.cpp',
        'compile_cmd': lambda src, exe: ['g++', src, '-o', exe],
        'run_cmd': lambda exe: [exe],
        'run_dir': None,
        'env': None,
    },
    'python': {
        'source_ext': '.py',
        'compile_cmd': None,
        'run_cmd': lambda src: ['python3', src],
        'run_dir': None,
        'env': None,
    },
    'java': {
        'source_ext': '.java',
        'compile_cmd': lambda src, _: ['javac', src],
        'run_cmd': lambda _: ['java', 'Main'],
        'run_dir': lambda src: os.path.dirname(src),
        'env': None,
    }
}


def execute_code(code, language, user_input):
    handler = LANGUAGE_HANDLERS.get(language)
    if not handler:
        return 'error', f'Language "{language}" not supported.'

    source_ext = handler['source_ext']
    executable_path = None

    try:
        if language == 'java':
            temp_dir = tempfile.mkdtemp()
            source_path = os.path.join(temp_dir, 'Main.java')
            with open(source_path, 'w', encoding='utf-8') as f:
                f.write(code)
        else:
            temp_file = tempfile.NamedTemporaryFile(suffix=source_ext, delete=False, mode='w', encoding='utf-8')
            source_path = temp_file.name
            temp_file.write(code)
            temp_file.close()

        if handler['compile_cmd']:
            executable_path = source_path.replace(source_ext, '')
            if os.name == 'nt' and language == 'cpp':
                executable_path += '.exe'
            compile_cmd = handler['compile_cmd'](source_path, executable_path)
            result = subprocess.run(compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
            if result.returncode != 0:
                return 'compile_error', result.stderr.decode()
        else:
            executable_path = source_path

        run_cmd = handler['run_cmd'](executable_path)
        cwd = handler['run_dir'](source_path) if handler.get('run_dir') else None
        env = handler.get('env')

        run_process = subprocess.run(
            run_cmd,
            input=user_input.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
            cwd=cwd,
            env=env
        )

        output = run_process.stdout.decode().strip()
        error = run_process.stderr.decode().strip()

        return 'success', output if output else error or 'No output'

    except subprocess.TimeoutExpired:
        return 'timeout', 'Execution timed out'
    except Exception as e:
        return 'error', str(e)
    finally:
        try:
            if language == 'java':
                if os.path.exists(source_path):
                    os.remove(source_path)
                class_file = os.path.join(os.path.dirname(source_path), 'Main.class')
                if os.path.exists(class_file):
                    os.remove(class_file)
                os.rmdir(os.path.dirname(source_path))
            else:
                if source_path and os.path.exists(source_path):
                    os.remove(source_path)
                if executable_path and os.path.exists(executable_path) and executable_path != source_path:
                    os.remove(executable_path)
        except Exception:
            pass

def run_code_and_check(code, language, testcase_dir):
    import os

    input_dir = os.path.join(testcase_dir, "input")
    output_dir = os.path.join(testcase_dir, "output")

    input_files = sorted(os.listdir(input_dir))
    failed_cases = []

    for filename in input_files:
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

        with open(input_path, 'r') as f:
            test_input = f.read()
        with open(output_path, 'r') as f:
            expected_output = f.read().strip()

        status, actual_output = execute_code(code, language, test_input)

        if status != 'success':
            return status.upper(), (
                f"❌ Test case: {filename}\n"
                f"⚠️ Status: {status}\n"
                f"💬 Error:\n{actual_output.strip()}"
            )

        if actual_output.strip() != expected_output:
            failed_cases.append(
                f"❌ Test case: {filename}\n"
                f"🧪 Input:\n{test_input.strip()}\n"
                f"🎯 Expected:\n{expected_output}\n"
                f"💥 Got:\n{actual_output.strip()}"
            )

    if failed_cases:
        return "Wrong Answer", "\n\n".join(failed_cases)

    return "Accepted", "✅ All test cases passed!"

