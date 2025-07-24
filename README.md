# OJ-Project

# Authentication

Create accounts app. We only need to care about view and templates. We can use python in-built models here specially for authentication.

## Registration

```python
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

```html
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
      .then((data) => {
        // Handle the response
        document.getElementById("outputArea").value = data.output || data.error;
      });

    function getCookie(name) {
      // a mannual function to get the CSRF token from cookies
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

```python
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

## adding functionality to run different languages as well

In problems_detail.html, we can add a dropdown to select the language. The selected language will be sent to the backend along with the code and input.

```html
<label for="languageSelect"><strong>Language:</strong></label>
<select
  id="languageSelect"
  style="margin-bottom: 10px; width: 150px; padding: 5px"
>
  <option value="cpp">C++</option>
  <option value="python">Python</option>
  <option value="java">Java</option>
</select>
```

in vanilla.js, we can get the selected language and send it to the backend.

```javascript
const language = document.getElementById("languageSelect").value;
```

and a style

```css
#languageSelect {
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 14px;
}
```

In views.py, we need to handle different languages. We can use the same logic as before but with different commands for compilation and execution based on the selected language.

```python
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
        'compile_cmd': lambda src, exe: ['javac', src],
        'run_cmd': lambda src: ['java', 'Main'],
        'run_dir': lambda src: os.path.dirname(src),
        'env': None,
    }
    # More languages...
}
```

for source_path

```py
source_ext = handler['source_ext']
with tempfile.NamedTemporaryFile(suffix=source_ext, delete=False) as source_file:
    source_file.write(code.encode())
    source_path = source_file.name
```

The tempfile module in Python is part of the standard library and is used to create temporary files and directories that can be used during runtime and automatically cleaned up afterward.

for executable path

```py
executable_path = source_path.replace(source_ext, '') if handler['compile_cmd'] else source_path
```

Remove extension from source_path to get the executable path for compiled languages. For interpreted languages like Python, it remains the same as source_path.

Compile if needed (python like languages do not need compilation)

```py
if handler['compile_cmd']:
    compile_cmd = handler['compile_cmd'](source_path, executable_path)
    compile_process = subprocess.run(
        compile_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10
    )
    if compile_process.returncode != 0:
        return JsonResponse({'error': compile_process.stderr.decode()})
```

Here `handler['compile_cmd']` is a lambda function defined per language.

For example, for C++:
`'compile_cmd': lambda src, exe: ['g++', src, '-o', exe]`

It gets called as:
`compile_cmd = ['g++', source_path, '-o', executable_path]`

So, it's equivalent to running this in terminal:
`g++ temp.cpp -o temp`

If the compilation fails, we return the error message.

For running the code, we use the run command defined in the handler:

```py
run_cmd = handler['run_cmd'](executable_path)
cwd = handler['run_dir'](source_path) if handler.get('run_dir') else None  # specially for java
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
```

cleaning up temporary files

```py
if language == 'java':
    class_file = source_path.replace('.java', '.class')
    if os.path.exists(class_file):
        os.remove(class_file)
```

# The Editor

In base (Base1.html in this case), we are going to use Codemirror for the code editor. It is a versatile code editor that can be easily integrated into web applications. It is an open-source project and is widely used in many web applications for code editing.

To use it lets import it in head of base1.html

```html
<!-- CodeMirror CSS -->
<link
  rel="stylesheet"
  href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/codemirror.min.css"
/>
<link
  rel="stylesheet"
  href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/theme/dracula.min.css"
/>

<!-- CodeMirror JS -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/codemirror.min.js"></script>

<!-- C++ and Python modes -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/mode/clike/clike.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/mode/python/python.min.js"></script>
```

here is the documentation for CodeMirror: https://codemirror.net/doc/manual.html

It says:

```text
for example, replace a textarea with a real editor:

`var myCodeMirror = CodeMirror(function(elt) {
  myTextArea.parentNode.replaceChild(elt, myTextArea);
}, {value: myTextArea.value});`

However, for this use case, which is a common way to use CodeMirror, the library provides a much more powerful shortcut:

var myCodeMirror = CodeMirror.fromTextArea(myTextArea);
```

So using `var myCodeMirror = CodeMirror.fromTextArea(myTextArea);` we can replace the textarea with a CodeMirror editor.

```js
var myCodeMirror = CodeMirror.fromTextArea(
  document.getElementById("codeArea"),
  {
    lineNumbers: true,
    theme: "github",
    mode: "text/x-c++src", // default to C++
    matchBrackets: true,
    autoCloseBrackets: true,
    indentUnit: 4,
    tabSize: 4,
    indentWithTabs: false,
  }
);
```

Now also we need to set mode of code that colors based on significance of that part of code. For example, keywords will be colored differently than variables.

Add these in base

```html
<!-- Language modes -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.15/mode/clike/clike.min.js"></script>
<!-- C, C++, Java -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.15/mode/python/python.min.js"></script>
```

Also the mode of the editor is set to C++ by default. We can change it based on the selected language. So we add an event listener to the language select dropdown to change the mode of the editor.

```js
const languageModeMap = {
  cpp: "text/x-c++src",
  java: "text/x-java",
  python: "python",
};

document
  .getElementById("languageSelect")
  .addEventListener("change", function () {
    const selectedLang = this.value;
    myCodeMirror.setOption(
      "mode",
      languageModeMap[selectedLang] || "text/plain"
    );
  });
```

Since the script is becoming long, we can move it to a separate file. Create a new file `editor.js` in the static directory and include it in the base template. This is useful at production level to keep the code organized and maintainable.

At very top of problem_detail.html, we can include the static file:

```html
<!-- Load static files -->
{% load static %}
```

Then we can include the script file:
At very top

```html
<!-- keep extending etc first-->
{% load static %}
```

Then just above the closing `</body>` tag, we can add:

```html
<script src="{% static 'js/editor.js' %}"></script>
```

Also in settings.py, we need to set the static URL and directories:

```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
```

`static/` (without a leading slash) tells Django to look for static files relative to the current page's URL, which confuses the URL resolver.

`/static/` tells Django:<br>
“Always look for static files starting from the root of the site.”

Also shifting css to same static directory. Path "static/css/problem_detail.css".

Also for code use `const code = myCodeMirror.getValue();` instead of `document.getElementById("codeArea").value;` to get the code from the CodeMirror editor.

# Adding the "Testcases"

Create a new model for TestCase in `models.py` to store the test cases for each problem. This will allow us to manage test cases separately and associate them with specific problems.

For this we are going to use a very practical and scalable idea, and widely used in real-world online judges (like Codeforces, AtCoder, etc.). Which is to store test cases as files (e.g., input1.txt, output1.txt) instead of as database entries.
