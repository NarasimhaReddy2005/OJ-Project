import os
import subprocess
import tempfile
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

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

@csrf_exempt
def run(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    try:
        data = json.loads(request.body)
        code = data.get('code', '')
        user_input = data.get('input', '')
        language = data.get('language', 'cpp')

        handler = LANGUAGE_HANDLERS.get(language)
        if not handler:
            return JsonResponse({'error': f'Language "{language}" not supported.'}, status=400)

        source_ext = handler['source_ext']

        # For Java, always create a file named Main.java
        if language == 'java':
            temp_dir = tempfile.mkdtemp()
            source_path = os.path.join(temp_dir, 'Main.java')
            with open(source_path, 'w', encoding='utf-8') as source_file:
                source_file.write(code)
        else:
            temp_file = tempfile.NamedTemporaryFile(suffix=source_ext, delete=False, mode='w', encoding='utf-8')
            source_path = temp_file.name
            temp_file.write(code)
            temp_file.close()

        if handler['compile_cmd']:
            executable_path = source_path.replace(source_ext, '')
            if os.name == 'nt' and language == 'cpp':
                executable_path += '.exe'
        else:
            executable_path = source_path

        # Compile
        if handler['compile_cmd']:
            compile_cmd = handler['compile_cmd'](source_path, executable_path)
            compile_process = subprocess.run(
                compile_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )
            if compile_process.returncode != 0:
                return JsonResponse({'error': compile_process.stderr.decode()}, status=400)

        # Run
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

        return JsonResponse({'output': output if output else error or 'No output'})

    except subprocess.TimeoutExpired:
        return JsonResponse({'error': 'Execution timed out'}, status=408)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        try:
            # Clean up
            if language == 'java':
                if os.path.exists(source_path):
                    os.remove(source_path)
                class_file = os.path.join(os.path.dirname(source_path), 'Main.class')
                if os.path.exists(class_file):
                    os.remove(class_file)
                os.rmdir(os.path.dirname(source_path))
            else:
                if os.path.exists(source_path):
                    os.remove(source_path)
                if os.path.exists(executable_path) and executable_path != source_path:
                    os.remove(executable_path)
        except Exception:
            pass
