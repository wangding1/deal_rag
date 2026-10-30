"""飞书代码块语言枚举，数值对应 code.style.language / TextStyle.language。"""

from enum import IntEnum, unique


@unique
class CodeLanguage(IntEnum):
    """飞书 Docx CodeLanguage；枚举成员不表示解析或高亮已实现。

    未列出的编号仍可作为 int 保留，勿随意映射为 PLAIN_TEXT 而丢失原值。
    """

    PLAIN_TEXT = 1  # PlainText · 纯文本
    ABAP = 2  # ABAP
    ADA = 3  # Ada
    APACHE = 4  # Apache
    APEX = 5  # Apex
    ASSEMBLY = 6  # Assembly
    BASH = 7  # Bash
    C_SHARP = 8  # CSharp
    C_PLUS_PLUS = 9  # C++
    C = 10  # C
    COBOL = 11  # COBOL
    CSS = 12  # CSS
    COFFEE_SCRIPT = 13  # CoffeeScript
    D = 14  # D
    DART = 15  # Dart
    DELPHI = 16  # Delphi
    DJANGO = 17  # Django
    DOCKERFILE = 18  # Dockerfile
    ERLANG = 19  # Erlang
    FORTRAN = 20  # Fortran
    FOX_PRO = 21  # FoxPro
    GO = 22  # Go
    GROOVY = 23  # Groovy
    HTML = 24  # HTML
    HTML_BARS = 25  # HTMLBars
    HTTP = 26  # HTTP
    HASKELL = 27  # Haskell
    JSON = 28  # JSON
    JAVA = 29  # Java
    JAVASCRIPT = 30  # JavaScript
    JULIA = 31  # Julia
    KOTLIN = 32  # Kotlin
    LATEX = 33  # LateX
    LISP = 34  # Lisp
    LOGO = 35  # Logo
    LUA = 36  # Lua
    MATLAB = 37  # MATLAB
    MAKEFILE = 38  # Makefile
    MARKDOWN = 39  # Markdown
    NGINX = 40  # Nginx
    OBJECTIVE = 41  # Objective
    OPEN_EDGE_ABL = 42  # OpenEdgeABL
    PHP = 43  # PHP
    PERL = 44  # Perl
    POST_SCRIPT = 45  # PostScript
    POWER_SHELL = 46  # PowerShell
    PROLOG = 47  # Prolog
    PROTO_BUF = 48  # ProtoBuf
    PYTHON = 49  # Python
    R = 50  # R
    RPG = 51  # RPG
    RUBY = 52  # Ruby
    RUST = 53  # Rust
    SAS = 54  # SAS
    SCSS = 55  # SCSS
    SQL = 56  # SQL
    SCALA = 57  # Scala
    SCHEME = 58  # Scheme
    SCRATCH = 59  # Scratch
    SHELL = 60  # Shell
    SWIFT = 61  # Swift
    THRIFT = 62  # Thrift
    TYPESCRIPT = 63  # TypeScript
    VB_SCRIPT = 64  # VBScript
    VISUAL = 65  # Visual
    XML = 66  # XML
    YAML = 67  # YAML
    CMAKE = 68  # CMake
    DIFF = 69  # Diff
    GHERKIN = 70  # Gherkin
    GRAPHQL = 71  # GraphQL
    OPENGL_SHADING_LANGUAGE = 72  # OpenGL Shading Language
    PROPERTIES = 73  # Properties
    SOLIDITY = 74  # Solidity
    TOML = 75  # TOML
