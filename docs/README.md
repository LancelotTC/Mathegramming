
# Generate a Python documentation with Sphinx

This is a README to show how to generate a Python documentation with Sphinx.
## Installation

Install the necessary libraries

```bash
  pip install sphinx
  pip install sphinx-rtd-theme
```

## Versions

```bash
  sphinx: 6.1.3
  sphinx-rtd-theme: 1.2.0
```

## Create the documentation

Place the website, instance and main.py in a root directory


```bash
  root-directory
   |instance/
   |website/
   |main.py
```

Create a 'docs' directory (this is where you will store the html files for the documentation)

```bash
  root-directory
   |docs/
   |instance/
   |website/
   |main.py
```

Open the command prompt and go to the docs directory 

```bash
cd root-directory/docs
```

Start Sphinx

```bash
sphinx-quickstart
```

It will ask you a couple of questions. Here is what I wrote (some of the fields are empty on purpose):

```bash
> Separate source and build directories (y/n) [n]:
> Project name: Mathegramming
> Author name(s): Lancelot Tariot Camille
> Project release []: 1.0.0
> Project language [en]:
```

After that, go outside of the docs directory, into the root-directory:

```bash
cd..
```

Then type the following command
```bash
sphinx-apidoc -o docs/ website/
```


Open the  docs/conf.py file and on the very top of the page, write the following:

/!\ import website AFTER the sys.path line

```bash
import os
import sys
sys.path.insert(0, os.path.abspath(".."))
import website
```


On that same file (conf.py), change the 2 following lines:

From:
```bash
extensions = []
```
```bash
html_theme = 'alabaster'
```
To:
```bash
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode'
]
```
```bash
html_theme = 'sphinx_rtd_theme'
```


Finally, open the docs/index.rst file and JUST ABOVE "Indices and tables", put the following line:
```bash
.. include:: website.rst
```

You can now go to your command prompt and inside the root-directory/docs directory, type the following command:

```bash
make html
```

You will now have to open the ```index.html``` file in docs/_build/html

```bash
cd _build/html/
```

## Refresh/update documentation

To refresh/update the documentation, do the following:

1. Go to the root-directory/docs/ directory


```bash
  cd root-directory/docs/
```

2. Run the 2 following lines

This will delete all the files in _build/
```bash
  make clean html
```
This will recreate all the updated files in _build/
```bash
  make html
```


## Authors

- [@lancelot-tariot-camille](https://gitlab.com/lancelot.tariot.camille)

