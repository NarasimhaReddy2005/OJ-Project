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

# Problems

```python
class Problem(models.Model):
    DIFFICULTY_CHOICES = [
        (1, 'Easy'),
        (2, 'Medium'),
        (3, 'Hard'),
    ]

    problem_name = models.CharField(max_length=100)
    problem_difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES)
    statement = models.TextField(max_length=3000)
    constraints = models.TextField(max_length=500)
```

If your model define like this then Django automatically adds this method: <br>
`problem.get_problem_difficulty_display()` <br>
And in templates, you just do:<br>
`{{problem.get_problem_difficulty_display}}`

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

Django adds CSRF protection to POST requests for security.

If you want to allow code to be submitted via frontend JavaScript (AJAX) without CSRF tokens (like in your /run/), you decorate it with:

```python
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def run(request):
    ...
```

✅ Use only for trusted endpoints (e.g., internal APIs or testing).
❌ Don't expose to public-facing unauthenticated users without protection.

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

```python
class TestCaseBundle(models.Model):
    problem = models.OneToOneField(Problem, on_delete=models.CASCADE, related_name='testcase_bundle')
    testcases_dir = models.CharField(max_length=255, help_text="Relative to MEDIA_ROOT/testcases/")
    zip_file = models.FileField(upload_to='testcase_zips/', null=True, blank=True)

    def get_full_path(self):
        return os.path.join(settings.MEDIA_ROOT, 'testcases', self.testcases_dir)

    def __str__(self):
        return f"Test cases for {self.problem.problem_name}"
```

`problem = models.OneToOneField(...)`: This creates a one-to-one relationship with the Problem model.<br>
Meaning: Each problem can have only one test case bundle.

`on_delete=models.CASCADE` means: If the problem is deleted, its test case bundle is also deleted.

`related_name='testcase_bundle'` means:<br>
From the Problem instance, you can access its test cases like:

```python
  problem.testcase_bundle
```

`testcases_dir = models.CharField(...)`:
This field stores the relative path (from `MEDIA_ROOT/testcases/`) to the directory where the test case files are extracted.

`MEDIA_ROOT` is a Django settings variable that defines the absolute filesystem path where uploaded user files (like images, PDFs, etc.) will be stored.

For example:<br>
If `testcases_dir = "problem_1"`, then test cases are expected at:
`MEDIA_ROOT/testcases/problem_1/`

Method: `get_full_path(self)`

```python
def get_full_path(self):
    return os.path.join(settings.MEDIA_ROOT, 'testcases', self.testcases_dir)
```

This method returns the absolute filesystem path to the directory that contains the test cases.

Example: `/home/user/myproject/media/testcases/problem_1/`

```python
zip_file = models.FileField(upload_to='testcase_zips/', null=True, blank=True)
```

`FileField` Tells: Django this field will store a file (like .zip).<br>
`upload_to='testcase_zips/'`: Files will be saved under MEDIA_ROOT/testcase_zips/.<br>
`null=True`: The database column can be empty (i.e., no ZIP file uploaded yet).<br>
`blank=True`: Allows leaving this field blank in Django Admin or forms.

This line adds a field to your TestCaseBundle model that allows uploading a ZIP file containing your test case files (.in and .out pairs).

### What Are Signals in Django?

Django signals are a way for certain senders (like model instances) to notify receivers (your custom functions) that something happened.

They follow the Observer pattern — where you observe an event (like saving a model) and run custom logic when that event occurs.

Here we will use signals to automatically extract test cases from a ZIP file when a TestCaseBundle is created or updated.

```python
def extract_zip_to_dir(zip_path, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for name in zip_ref.namelist():
            if '..' in name or name.startswith('/'):
                raise ValueError("Unsafe file path detected in ZIP")
        zip_ref.extractall(dest_dir)

@receiver(post_save, sender=TestCaseBundle)
def auto_extract_zip(sender, instance, **kwargs):
    if instance.zip_file:
        extract_path = instance.get_full_path()
        extract_zip_to_dir(instance.zip_file.path, extract_path)
```

This code defines a function `extract_zip_to_dir` that extracts files from a ZIP archive to a specified directory. It checks for unsafe file paths to prevent directory traversal attacks.

`sender`: The model class that triggered the signal (TestCaseBundle)
`instance`: The specific object (record) that was just saved.

Every thing seems fine, but what if admin unknowingly adds a ZIP containing unsafe paths or invalid files, no matching inputs and outputs, etc.?

To handle this, we can add validation logic in the `extract_zip_to_dir` function to ensure that the ZIP file contains only valid test case files and does not contain any unsafe paths.

```python
def validate_testcase_zip(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # lists all file paths
        file_list = [f for f in zip_ref.namelist() if not f.endswith('/')]

        # Detect root prefix (like powerProblemTestcases/) (not zipfile name)
        common_prefix = os.path.commonprefix(file_list)
        if '/' in common_prefix:
            root_folder = common_prefix.split('/')[0]
        else:
            root_folder = ""

        # Normalize file paths to ignore root folder
        normalized_files = [
            '/'.join(f.split('/')[1:]) if f.startswith(root_folder + '/') else f
            for f in file_list
        ]

        inputs = set()
        outputs = set()

        for file in normalized_files:
            if not (file.startswith("input/") or file.startswith("output/")):
                raise ValidationError("All files must be inside 'input/' or 'output/' folders.")
            if not file.endswith(".txt"):
                raise ValidationError("Only .txt files allowed in input/output folders.")

            basename = os.path.basename(file)
            if file.startswith("input/"):
                inputs.add(basename)
            elif file.startswith("output/"):
                outputs.add(basename)

        if inputs != outputs:
            missing_inputs = outputs - inputs
            missing_outputs = inputs - outputs
            raise ValidationError(
                f"Mismatched test cases:\n"
                f"{'Missing input(s): ' + ', '.join(missing_inputs) if missing_inputs else ''} "
                f"{'Missing output(s): ' + ', '.join(missing_outputs) if missing_outputs else ''}"
            )

```

This function checks the following: (this is how zip is extracted in windows)

```lua
testcases.zip
  testcases/
  ├── input/
  │   ├── 1.txt
  │   ├── 2.txt
  │   └── 3.txt
  ├── output/
  │   ├── 1.txt
  │   ├── 2.txt
  │   └── 3.txt
```

for each f, we split and take form index 1 of file's path and join them eleminating starting.

```python
normalized_files = [
            '/'.join(f.split('/')[1:]) if f.startswith(root_folder + '/') else f
            for f in file_list
        ]
```

This can be then easily used to check starts with "input/" or "output/".

Django expects:<br>
ValidationError → ❌ Fail validation<br>
Anything else (i.e., no exception) → ✅ Valid

IN testcase model we add this

```python
    def save(self, *args, **kwargs):
        # Auto-generate testcases_dir if not set
        if not self.testcases_dir:
            self.testcases_dir = f'problem_{self.problem.id or "new"}'

        # Rename the uploaded zip file based on problem
        if self.zip_file and hasattr(self.zip_file, 'name'):
            base, ext = os.path.splitext(self.zip_file.name)
            slug = slugify(self.problem.problem_name)
            new_name = f"{slug}_{self.problem.id or 'new'}{ext}"
            self.zip_file.name = f"testcase_zips/{new_name}"

        super().save(*args, **kwargs)
```

#### Example:

Say you're uploading a zip for:<br>
Problem ID: 7<br>
Problem Name: "Power of a Number"

Then: testcases_dir = "problem_7" will be automatically filled

Your extracted testcases will be stored in:
`MEDIA_ROOT/testcases/problem_7/`<br>
This helps uniquely identify test cases per problem in the file system and avoids name clashes.

#### Example2

ugly_name_with_spaces_and_numbers123.zip

But the problem name is:
"Power of a Number"

And the problem ID is 7

Then this line:<br>
slug = slugify(self.problem.problem_name) # → "power-of-a-number"

And finally:<br>
`self.zip_file.name = f"testcase_zips/{slug}_{self.problem.id}{ext}"`<br>
Gives: `testcase_zips/power-of-a-number_7.zip`

Again to make it automatically generates file name without raising `name needed` error add `blank=True` to the testcases_dir field in the TestCaseBundle model:

```python
testcases_dir = models.CharField(max_length=255, blank=True, help_text="Relative to MEDIA_ROOT/testcases/")
```

## Extraction

```python
def extract_zip_to_dir(zip_path, dest_dir):
    validate_testcase_zip(zip_path)
    os.makedirs(dest_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        file_list = [f for f in zip_ref.namelist() if not f.endswith('/')]

        # Detect and remove top-level folder if exists
        common_prefix = os.path.commonprefix(file_list)
        if '/' in common_prefix:
            root_folder = common_prefix.split('/')[0]
        else:
            root_folder = ""

        for member in file_list:
            # Remove top-level folder
            relative_path = '/'.join(member.split('/')[1:]) if root_folder else member
            target_path = os.path.join(dest_dir, relative_path)

            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, 'wb') as f:
                f.write(zip_ref.read(member))
```

in admin to link the TestCaseBundle model to the Problem model, we can use Django's admin interface to register the TestCaseBundle model and display it in the Problem admin page.

```python
class TestCaseBundleInline(admin.StackedInline):
    model = TestCaseBundle
    extra = 0

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ['problem_name', 'problem_difficulty']
    inlines = [TestCaseBundleInline]
```

When you use a StackedInline for TestCaseBundle inside ProblemAdmin, and you save both from the Django Admin interface (in one form), Django processes the save in two phases:

Saves the parent Problem object first.
This assigns a valid .id to problem.

Then saves the inline TestCaseBundle, passing the newly saved problem as a foreign key.

This means:<br>
✅ By the time TestCaseBundle.save() is called, self.problem.id is already set, and your code works as expected.

class `TestCaseBundleInline(admin.StackedInline)`:<br>
Tells Django:<br>
“Whenever you open a Problem in the admin panel, also allow editing its associated TestCaseBundle in the same form page.”

StackedInline → makes the layout vertical (stacked).
There's also TabularInline for horizontal row-style layout.

# Submission

Creating a CodeSubmission model

```python
class CodeSubmission(models.Model):
    LANGUAGES = [
        ('cpp', 'C++'),
        ('py', 'Python'),
        ('java', 'Java'),
    ]

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='submissions')
    code = models.TextField()
    language = models.CharField(max_length=10, choices=LANGUAGES)
    submitted_at = models.DateTimeField(auto_now_add=True)
    verdict = models.CharField(max_length=20, blank=True, null=True)
    output = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.problem.problem_name} - {self.language} - {self.verdict}"
```

Before we can implement it lets extract reusable code from run function to execute code and return results into utils.py.

Then lets create a submission view to handle code submissions.

```python
def submit_code(request, problem_id):
    if request.method == 'POST':
        problem = get_object_or_404(Problem, id=problem_id)
        code = request.POST.get('code')
        language = request.POST.get('language')

        # Save the submission
        submission = CodeSubmission.objects.create(
            problem=problem,
            code=code,
            language=language
        )

        # Run and test
        verdict, output = run_code_and_check(code, language, problem.testcase_bundle.get_full_path())

        # Save results
        submission.verdict = verdict
        submission.output = output
        submission.save()

        return JsonResponse({
            'verdict': verdict,
            'output': output
        })

    return JsonResponse({'error': 'Only POST allowed'}, status=405)
```

run_code_and_check function in utils.py

First we sort both input and output directories so we can compare them easily.
We execute every output to given output of corresponding input file.
Whenever we get an error, we return the error status from that testcase.

```python
def run_code_and_check(code, language, testcase_dir):
    input_dir = os.path.join(testcase_dir, "input")
    output_dir = os.path.join(testcase_dir, "output")

    input_files = sorted(os.listdir(input_dir))

    for filename in input_files:
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

        with open(input_path, 'r') as f:
            test_input = f.read()
        with open(output_path, 'r') as f:
            expected_output = f.read().strip()

        actual_output, status = execute_code(code, language, test_input)

        if status != 'success':
            return status.upper(), actual_output  # TIMEOUT, ERROR, etc.

        if actual_output.strip() != expected_output:
            return 'Wrong Answer', actual_output

    return 'Accepted', 'All test cases passed'
```

## Migration behaviour

Skip to `Resetting the Database` section if you are starting fresh.

When you add a new model or change an existing one, Django needs to create or update the database schema accordingly. This is done through migrations.

```bash
python manage.py makemigrations

WARNINGS:
?: (staticfiles.W004) The directory 'C:\Users\laksh\PycharmProjects\OJ\OnlineJudge\static' in the STATICFILES_DIRS setting does not exist.
Was codesubmission.input_data renamed to codesubmission.output (a TextField)? [y/N] N
Was codesubmission.output_data renamed to codesubmission.output (a TextField)? [y/N] N
Was codesubmission.timestamp renamed to codesubmission.submitted_at (a DateTimeField)? [y/N] N
It is impossible to add a non-nullable field 'problem' to codesubmission without specifying a default. This is because the database needs something to populate existing rows.
Please select a fix:
 1) Provide a one-off default now (will be set on all existing rows with a null value for this column)
 2) Quit and manually define a default value in models.py.
Select an option: 1
Please enter the default value as valid Python.
The datetime and django.utils.timezone modules are available, so it is possible to provide e.g. timezone.now as a value.
Type 'exit' to exit this prompt
>>> 1
It is impossible to add the field 'submitted_at' with 'auto_now_add=True' to codesubmission without providing a default. This is because the database needs something to populate existing rows.
 1) Provide a one-off default now which will be set on all existing rows
 2) Quit and manually define a default value in models.py.
Select an option: 1
Please enter the default value as valid Python.
Accept the default 'timezone.now' by pressing 'Enter' or provide another value.
The datetime and django.utils.timezone modules are available, so it is possible to provide e.g. timezone.now as a value.
Type 'exit' to exit this prompt
[default: timezone.now] >>> timezone.now
Migrations for 'submission':
  submission\migrations\0002_remove_codesubmission_input_data_and_more.py
    - Remove field input_data from codesubmission
    - Remove field output_data from codesubmission
    - Remove field timestamp from codesubmission
    + Add field output to codesubmission
    + Add field problem to codesubmission
    + Add field submitted_at to codesubmission
    + Add field verdict to codesubmission
    ~ Alter field language on codesubmission
(.venv) PS C:\Users\laksh\PycharmProjects\OJ\OnlineJudge> python3 manage.py migrate

```

Since you're adding non-nullable fields (problem, submitted_at), Django asks:

“What should be the default value for rows that already exist in the database?”

This is standard behavior to avoid breaking existing rows.

You got messages like:

It is impossible to add a non-nullable field 'problem' without specifying a default.

Even though you said it’s the first time you're implementing submission, Django still checks if the database table already exists, and if it does (perhaps from earlier test runs), it assumes existing rows may exist.

### Resetting the Database

Before problems don't have testcases attached, so we simply flush them (getting rid of them) and create migrations freshly. Now we can simply avoid all the above handling.

```bash
python manage.py flush
```

- This will delete all data in the database and reset it to a clean state.
- Remove old testcase directorys
- Create users and super users, add problems with testcases.

### BUG
Same testcase dir is used by all problems.
On 2 hrs of tracking down, I found that the problem is within problem_detail.html where we are setting the problem_id editor.js which is using `window.problemId` that was not at all set in problem_detail.html.

So on adding this to problem_detail.html, it will set the `window.problemId` variable to the current problem's ID and !PROBLEMO SOLVED!.
``` html
<script>
  window.problemId = {{ problem.id }}; 
</script>
```


