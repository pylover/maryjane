# MaryJane

[<img src="http://img.shields.io/pypi/v/maryjane.svg">](https://pypi.python.org/pypi/maryjane)


Simple Task runner and build tool.



### Python 3.6 or higher required.

The [Formatted string literals](https://docs.python.org/3.6/whatsnew/3.6.html#pep-498-formatted-string-literals) are introduced in version 3.6.

It's used to evaluate the values between `{}`, see the example:

### Install

```shell
$ pip install marynaje
```

If you whant to compile SASS using `libsass` and it's python wrapper:
 

```shell
$ pip install libsass
```
 

#### maryjane.yaml

You can set any variable anywhere, and access from anywhere: see `file1` and `bag.count`

```yaml

PY:
  - from os.path import split, exists
  - from os import mkdir

title: Test Project
version: 0.1.0

empty:

static: {here}/static
sass: {here}/sass
temp: {here}/../temp

bag:
  count: 0
  avg: .34
  INCLUDE: {here}/simple.dict.yaml

task1:

  file1: {static}/file1.txt
  files:
    - {static}/file1.txt
    - {static}/file2.txt

  outfile: {temp}/out.txt

  ECHO: Concatenating {split(file1)[1]}, {', '.join(split(f)[1] for f in files)} -> {split(outfile)[1]}.
  SHELL:
    - mkdir -p $(dirname {outfile})
    - cat {file1} {' '.join(files)} > {outfile}
  PY: bag.count += 1


SASS: {sass}/index.sass > {temp}/index.css

WATCH: {here}
WATCH_ALL: {static}
NO_WATCH: {here}/temp

```

    
#### simple.dict.yaml

```yaml
item1:
    item2: value2
```

#### Build

```shell
$ maryjane
```

```
Concatenating file1.txt, file1.txt, file2.txt -> out.txt.
Watching for /home/vahid/workspace/maryjane/test_stuff
Watching for /home/vahid/workspace/maryjane/test_stuff/sass
Watching for /home/vahid/workspace/maryjane/test_stuff/static

```

#### Build & Watch:

```shell
$ maryjane -w
```

```
Concatenating file1.txt, file1.txt, file2.txt -> out.txt.
Watching for /home/vahid/workspace/maryjane/test_stuff
Watching for /home/vahid/workspace/maryjane/test_stuff/sass
Watching for /home/vahid/workspace/maryjane/test_stuff/static

Reloading
Concatenating file1.txt, file1.txt, file2.txt -> out.txt.
Watching for /home/vahid/workspace/maryjane/test_stuff
Watching for /home/vahid/workspace/maryjane/test_stuff/sass
Watching for /home/vahid/workspace/maryjane/test_stuff/static

```

Check out `../temp/out.txt` to see the result.
