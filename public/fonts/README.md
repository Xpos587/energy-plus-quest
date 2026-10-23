# Prototype typography

All font assets required by the interface are included in this archive and
loaded locally by the application. No external font service is required.

The `normalidad-proxy-*.woff2` files contain Roboto Condensed (regular, medium
and bold), licensed under the bundled `OFL-Roboto.txt`. They are the existing
prototype/cutscene font, not copies of the commercial Normalidad family.
CSS names the bundled font accurately; Verdana remains the system fallback.

`roboto-condensed-semibold.woff2` is the weight-600 instance of Google Fonts'
[Roboto Condensed variable font](https://github.com/google/fonts/tree/main/ofl/robotocondensed),
used as `Quest Choice` for the approved Figma choice labels. It uses the same
bundled OFL license. This avoids substituting weight 700 for SemiBold.
