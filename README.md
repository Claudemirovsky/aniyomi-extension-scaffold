# Aniyomi Extension Scaffold
A fork of [Aniyomi Extension Scaffold](https://github.com/tora-o/aniyomi-extension-scaffold) modified to suit my needs, but in the end it still is a script that scaffolds the creation of extensions for aniyomi/tachiyomi.

## Usage

### Interactive mode (inputs):

```bash
$ python creator.py
Choose the extension type:
    1. Anime extension / Aniyomi
    2. Manga extension / Tachiyomi

Enter your choice: 2

Source name: Example
Source language: pt-BR
Base URL: https://example.com

Choose the base class:
    1. HttpSource / API/JSON oriented
    2. ParsedHttpSource / JSoup/CSS oriented

Enter your choice: 2

Creating src/pt/example/AndroidManifest.xml
Creating src/pt/example/build.gradle
Creating src/pt/example/src/eu/kanade/tachiyomi/extension/pt/example/Example.kt
Creating src/pt/example/src/eu/kanade/tachiyomi/extension/pt/example/ExampleUrlActivity.kt
```

### CLI-mode
```bash
$ python creator.py --anime -p -n "Example" -l "en" -b "https://example.org"

Creating src/en/example/AndroidManifest.xml
Creating src/en/example/build.gradle
Creating src/en/example/src/eu/kanade/tachiyomi/animeextension/en/example/Example.kt
Creating src/en/example/src/eu/kanade/tachiyomi/animeextension/en/example/ExampleUrlActivity.kt

$ python creator.py --help
usage: creator.py [-h] [-a] [-m] [-n NAME] [-l LANG] [-b BASE_URL]
                  [-p | --parsed | --no-parsed]

options:
  -h, --help            show this help message and exit
  -a, --anime           Creates a anime extension. Takes precedence over
                        --manga.
  -m, --manga           Creates a manga extension.
  -n NAME, --name NAME  Name of the source
  -l LANG, --lang LANG  Language of the source
  -b BASE_URL, --base-url BASE_URL
                        Base URL of the source
  -p, --parsed, --no-parsed
                        Use ParsedHttpSource as base to the main class
```

### Mixed mode

```bash
$ python creator.py --manga -b https://example.org --no-parsed
Source name: Example LTD
Source language: de

Creating src/de/exampleltd/AndroidManifest.xml
Creating src/de/exampleltd/build.gradle
Creating src/de/exampleltd/src/eu/kanade/tachiyomi/extension/de/exampleltd/ExampleLTD.kt
Creating src/de/exampleltd/src/eu/kanade/tachiyomi/extension/de/exampleltd/ExampleLTDUrlActivity.kt
```
