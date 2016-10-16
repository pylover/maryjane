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
 

### maryjane.yaml

You can set any variable anywhere, and access from anywhere: see `file1` and `bag.count`. All `UPPER-CASED` keys are reserved for directives.

Currently the `INCLUDE`, `PY`, `SHELL`, `ECHO`, `WATCH`, `WATCH-ALL`, `NO-WATCH` and `SASS` are supported. See the example for details:

Multiline expressions are started, and terminated by `$$`. They should preserve indent. 

```yaml

PY:
  - from os.path import split, exists, basename
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

title: $$
  A simple multi-line
  text.A simple multi-line
  # not commented
  text. $$

text_files:

  file1: {static}/file1.txt
  files:
    - {static}/file2.txt
    - {static}/file3.txt
    - {static}/misc/no-watch-file.txt
    - {static}/misc/file1.txt

  outfile: {temp}/out.txt
  outdir: {dirname(outfile)}

  ECHO: Concatenating {basename(file1)}, {', '.join(basename(f) for f in files)} -> {basename(outfile)}.
  PY:
    - $$
      if not exists(outdir):
        mkdir(outdir)
      $$

    - $$
      for i in range(5):
        bag.count += i
      $$

  SHELL:
    - touch {outfile}
    - cat {file1} {' '.join(files)} > {outfile}
  PY: bag.count += 1

  ECHO: Watching for {static}
  WATCH-ALL: {static}
  NO-WATCH: {static}/misc/no-watch-file.txt


styles:
  ECHO: Compiling index.sass > index.css
  SASS: {sass}/index.sass > {temp}/index.css

  ECHO: Watching for {sass}
  WATCH: {sass}


ECHO: Watching for {here}
WATCH: {here}/maryjane.yaml

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
Compiling index.sass > index.css

```

#### Build & Watch:

```shell
$ maryjane -w
```

```
Concatenating file1.txt, file1.txt, file2.txt -> out.txt.
Watching for /home/vahid/workspace/maryjane/test_stuff/static
Compiling index.sass > index.css
Watching for /home/vahid/workspace/maryjane/test_stuff/sass
Watching for /home/vahid/workspace/maryjane/test_stuff
```

After change in `test_stuff/sass` directory:

```
Compiling index.sass > index.css
Watching for /home/vahid/workspace/maryjane/test_stuff/sass
```

After change in `test_stuff/static` directory:

```
Concatenating file1.txt, file1.txt, file2.txt -> out.txt.
Watching for /home/vahid/workspace/maryjane/test_stuff/static

```

After change in `test_stuff/` directory:

```
Concatenating file1.txt, file1.txt, file2.txt -> out.txt.
Watching for /home/vahid/workspace/maryjane/test_stuff/static
Compiling index.sass > index.css
Watching for /home/vahid/workspace/maryjane/test_stuff/sass
Watching for /home/vahid/workspace/maryjane/test_stuff

```

Check out `../temp/out.txt` to see the result.

### Another Example:

```yaml


PY:
  - from os.path import relpath

maryjane: 4
version: 0.1.0
title: myproject

ECHO: Loading project: {title} v{version} by maryjane: {maryjane}

root: {here}/myproject
public: {root}/public
lib: {public}/lib
crlf: \n

PY: $$
  def rel(p):
    return relpath(p, here)
  $$

styles:
  ECHO: $$
    #########
    ## CSS ##
    ######### $$
  sass: {root}/sass
  css: {public}/css
  input: {sass}/index.sass
  output: {css}/index.css

  ECHO: $$
    Building:
        - {rel(input)}
      Into:
        - {rel(output)}
    $$

  SASS: {input} > {output}

  ECHO: Watching for SASS files on: {rel(sass)}
  WATCH: {sass}

scripts:
  ECHO: $$
    #################
    ## Javascripts ##
    ################# $$

  javascripts: {root}/javascripts
  bootstrap: {here}/../bootstrap/js/src

  inputs:
    - {lib}/jquery.min.js

    # Bootstrap
    - {bootstrap}/util.js
    - {bootstrap}/alert.js
    - {bootstrap}/button.js
    - {bootstrap}/carousel.js
    - {bootstrap}/collapse.js
    - {bootstrap}/dropdown.js
    - {bootstrap}/modal.js
    - {bootstrap}/scrollspy.js
    - {bootstrap}/tab.js
    - {bootstrap}/tooltip.js
    - {bootstrap}/popover.js

    - {javascripts}/index.js

  output: {public}/javascript/index.js

  ECHO: $$
    Concatenating:
        - {(crlf + '    - ').join(rel(f) for f in inputs)}
      Into:
        - {rel(output)}
    $$

  ECHO: Watching for javascript files on: {rel(javascripts)}
  WATCH: {javascripts}

WATCH: maryjane.yaml

```

Output:

```

Loading project: myproject v0.1.0 by maryjane: 4

#########
## CSS ##
######### 

Building:
    - myproject/sass/index.sass
  Into:
    - myproject/public/css/index.css

Watching for SASS files on: myproject/sass

#################
## Javascripts ##
################# 

Concatenating:
    - myproject/public/lib/jquery.min.js
    - ../bootstrap/js/src/util.js
    - ../bootstrap/js/src/alert.js
    - ../bootstrap/js/src/button.js
    - ../bootstrap/js/src/carousel.js
    - ../bootstrap/js/src/collapse.js
    - ../bootstrap/js/src/dropdown.js
    - ../bootstrap/js/src/modal.js
    - ../bootstrap/js/src/scrollspy.js
    - ../bootstrap/js/src/tab.js
    - ../bootstrap/js/src/tooltip.js
    - ../bootstrap/js/src/popover.js
    - myproject/javascripts/index.js
  Into:
    - myproject/public/javascript/index.js

Watching for javascript files on: myproject/javascripts


```

After changing javascript files:

```
#################
## Javascripts ##
################# 

Concatenating:
    - myproject/public/lib/jquery.min.js
    - ../bootstrap/js/src/util.js
    - ../bootstrap/js/src/alert.js
    - ../bootstrap/js/src/button.js
    - ../bootstrap/js/src/carousel.js
    - ../bootstrap/js/src/collapse.js
    - ../bootstrap/js/src/dropdown.js
    - ../bootstrap/js/src/modal.js
    - ../bootstrap/js/src/scrollspy.js
    - ../bootstrap/js/src/tab.js
    - ../bootstrap/js/src/tooltip.js
    - ../bootstrap/js/src/popover.js
    - myproject/javascripts/index.js
  Into:
    - myproject/public/javascript/index.js

Watching for javascript files on: myproject/javascripts


```


### Change Log

#### 4.2.0b1

- Multiline python code and text: #7
- Optional SASS Compiler: #6
- Watcher: #2
- Internal YAML-like parser: #1
