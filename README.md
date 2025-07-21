# OJ-Project

# Authentication
Create accounts app. We only need to care about view and templates. We can use python in-built models here specially for authentication. 

## Registration
``` python
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'auth/register.html', {'form': form})
```

# Editor 

## Adding compilation feature in problems_detail.html or simply RUN function
In problems_detail.html, on clicking run button, we will send the code to the backend and it will return the output. The backend will compile the code and return the output. To do that we add the following sctipt:

``` html
<script>
  document.getElementById("runBtn").addEventListener("click", () => {
    const code = document.getElementById("codeArea").value;
    const input = document.getElementById("inputArea").value;
    const language = "cpp"; // explicitly specify C++

    fetch("/submission/run/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify({ code, input, language }),
    }) // Send the code to the backend
      .then((res) => res.json()) // Parse the JSON response
      .then((data) => { // Handle the response
        document.getElementById("outputArea").value = data.output || data.error;
      });

    function getCookie(name) { // a mannual function to get the CSRF token from cookies
      // This function retrieves the value of a cookie by its name
      let cookieValue = null;
      if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.startsWith(name + "=")) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }
  });
</script>
```

### What is happening
1. We add an event listener to the "Run" button.
2. When the button is clicked, we get the code from the code area, input from the input area, and specify the language (C++ in this case).
3. We send a POST request to the `/submission/run/` endpoint with the code, input, and language as JSON.
4. The backend processes the request, compiles the code, and returns the output or error.

### Headers used:
- `Content-Type`: Specifies the media type of the resource (application/json in this case).
- `X-CSRFToken`: Used to prevent Cross-Site Request Forgery attacks.

## Coming to backend
In the backend, we need to handle the `/submission/run/` endpoint. This will involve creating a view that processes the code, compiles it, and returns the output.

steps:

1. Create a view function in `views.py` to handle the compilation and execution of the code.
2. Use `subprocess` to compile the C++ code and execute it.
3. Return the output or error as a JSON response.
4. Error handling for compilation and execution errors.

run in views.py
``` python
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
            # we make file persist to be used for compilation and running
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
            # Check for compilation errors. If there are any, return them
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

        # a TLE error is raised if the process takes too long to execute
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

```

That's it, now you can run C++ code directly from the problem detail page in your Django application. The output will be displayed in the output area after clicking the "Run" button.

Make sure to update urls.py to include the new view.

