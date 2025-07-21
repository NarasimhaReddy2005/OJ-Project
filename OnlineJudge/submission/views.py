import os
import subprocess
import tempfile
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def run(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code', '')
            user_input = data.get('input', '')

            # Save C++ code to a temporary .cpp file
            with tempfile.NamedTemporaryFile(suffix=".cpp", delete=False) as source_file:
                source_file.write(code.encode())
                source_file_path = source_file.name

            # Compile the code
            executable_path = source_file_path.replace(".cpp", "")
            compile_process = subprocess.run(
                ['g++', source_file_path, '-o', executable_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )

            if compile_process.returncode != 0:
                return JsonResponse({'error': compile_process.stderr.decode()})

            # Run the compiled executable
            run_process = subprocess.run(
                [executable_path],
                input=user_input.encode(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )

            output = run_process.stdout.decode()
            error = run_process.stderr.decode()

            return JsonResponse({'output': output if output else error})

        except subprocess.TimeoutExpired:
            return JsonResponse({'error': 'Execution timed out'})
        except Exception as e:
            return JsonResponse({'error': str(e)})
        finally:
            # Cleanup files
            if os.path.exists(source_file_path):
                os.remove(source_file_path)
            if os.path.exists(executable_path):
                os.remove(executable_path)

    return JsonResponse({'error': 'Invalid request method'}, status=400)
