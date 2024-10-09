
Some early examples (currently no attribute or text support):

Remove all spans:

```
(span,[],Children) = ()
```

Make all spans bold:

```
(span,[],Children) = (b,[],[(span,[],Children)])
```

### Running commands

An example:

```bash
poetry run python -m tpml.main '(span,[],Children) = (b,[],[(span,[],Children)])' --html tests/data/ask-hn-oct-24.html | tee /tmp/out.html
```
