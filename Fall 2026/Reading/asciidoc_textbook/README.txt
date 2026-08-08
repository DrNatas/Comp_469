CS 188 Asciidoctor conversion
=============================

Main file:
  textbook.adoc

Images:
  images/

Build HTML with:
  asciidoctor -b html5 textbook.adoc

Build a standalone HTML file with embedded images, if desired:
  asciidoctor -a data-uri -b html5 textbook.adoc

Fixes in this revision
----------------------
The initial conversion contained equation continuation lines beginning with "= ".
In Asciidoctor book mode, those lines were parsed as top-level Part headings, which
caused "invalid part" errors and cascading "section title out of sequence" warnings.
Those equation lines are now escaped so they remain ordinary text.

Two explicit numbered-list continuations that Asciidoctor interpreted as new lists
now include start attributes, avoiding the list-index warnings seen in the original
build output.

Stray C0 control characters introduced by PDF text extraction were also replaced
with printable delimiters.

Static validation performed on this revision:
  - no unescaped single-equals headings outside the document title / literal blocks
  - no section-level jumps among actual section headings
  - all 112 image references resolve to files in images/
  - common delimited blocks are balanced
  - no stray C0 control characters remain

Note: Asciidoctor itself is not installed in the conversion environment, so the exact
CLI build could not be executed here. The syntax faults matching the reported errors
were corrected directly.
