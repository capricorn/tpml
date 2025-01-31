
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

### Emit Javascript

An example: highlighting all `<b>` elements:

```bash
poetry run python -m tpml.main --js '(b,[],Children) = (mark,[],Children)'
```

Output:

```javascript
(()=>{var s=(e,r)=>()=>(r||e((r={exports:{}}).exports,r),r.exports);var u=s((C,g)=>{function o(e){return e[0]==e[0].toUpperCase()||e=="_"}function f(e){return e.children==null?[]:Array(...e.children).filter(r=>r.nodeType!=3)}function d(e,r){if(r.tag=="_"||r.tag==e.tagName.toLowerCase()){let i=f(e);if(r.children.length==0&&i.length==0||r.children.length==1&&o(r.children[0].tag))return!0;if(r.children.length>0&&e.children.length==r.children.length){for(let n=0;n<r.children.length;n++)if(d(e.children[n],r.children[n])==!1)return!1;return!0}}return!1}function h(e,r,i,n){console.assert(d(e,r));let l=r.tag;l=="_"&&(l=e.tag);let t=n.createElement(i.tag);for(let a of e.childNodes)t.appendChild(a);return[t,f(e)]}function c(e,r,i,n){let l=f(e);if(d(e,r)){let t;[t,l]=h(e,r,i,n),e.replaceWith(t)}for(let t of l)c(t,r,i,n)}g.exports={match:d,unify:h,unify_tree:c};c(window.document.documentElement,{tag:"b",attrs:[],children:[{tag:"Children",attrs:[],children:[]}]},{tag:"mark",attrs:[],children:[{tag:"Children",attrs:[],children:[]}]},window.document)});u();})();
```

### Emit bookmarklet

(NB. Chrome will strip the `javscript:` prefix if you paste this directly into the URL bar.)

```bash
poetry run python -m tpml.main --bookmarklet '(b,[],Children) = (mark,[],Children)'
```

Output:

```javascript
javascript:(()=>{var s=(e,r)=>()=>(r||e((r={exports:{}}).exports,r),r.exports);var u=s((C,g)=>{function o(e){return e[0]==e[0].toUpperCase()||e=="_"}function f(e){return e.children==null?[]:Array(...e.children).filter(r=>r.nodeType!=3)}function d(e,r){if(r.tag=="_"||r.tag==e.tagName.toLowerCase()){let i=f(e);if(r.children.length==0&&i.length==0||r.children.length==1&&o(r.children[0].tag))return!0;if(r.children.length>0&&e.children.length==r.children.length){for(let n=0;n<r.children.length;n++)if(d(e.children[n],r.children[n])==!1)return!1;return!0}}return!1}function h(e,r,i,n){console.assert(d(e,r));let l=r.tag;l=="_"&&(l=e.tag);let t=n.createElement(i.tag);for(let a of e.childNodes)t.appendChild(a);return[t,f(e)]}function c(e,r,i,n){let l=f(e);if(d(e,r)){let t;[t,l]=h(e,r,i,n),e.replaceWith(t)}for(let t of l)c(t,r,i,n)}g.exports={match:d,unify:h,unify_tree:c};c(window.document.documentElement,{tag:"b",attrs:[],children:[{tag:"Children",attrs:[],children:[]}]},{tag:"mark",attrs:[],children:[{tag:"Children",attrs:[],children:[]}]},window.document)});u();})();
```

# Semantics

## Special notation

### Sets

`A <= B` means `A` subset of `B`.
`|A|` is set cardinality.
`A = B` is set equality.

### Lists

Lists are zero-indexed.

`L[k]` returns the value at index $k$.
`L[k:]` slices the list to include all elements on and after index `k`. 
`L[:k]` slices the list to include all elements up to but excluding index `k`. 
`|L|` is the list length.

Any negative $k$ indexes as `|L|+k`; `L[-1] = L[|L|-1]`, etc.

## Strings

Strings are double-quoted as seen in many other programming languages, e.g. `"foo"`, `"bar"`. They currently do _not_ support
nested quotes (string escapes are unimplemented.)

## Variables

A variable is any alphanumeric sequence beginning with the regex `[A-Z]`. Examples: `Foo`, `Bar`.

## Set patterns

A set consists of curly braces and elements delimited by a comma. The valid elements are: strings, `_`, `...`. For example, 
`{ "foo", "bar", _, ... }`.

### Matching

A match is defined as: `match(SetPattern,Set) -> bool` where `SetPattern` is a pattern defined above and `Set` is a set consisting of strings elements.

### Strict set matching

A set containing only strings applies strict set matching. `match(SetPattern,Set) := (SetPattern = Set)`.
Some examples:

```
match({"foo","bar"},{"foo","bar"}) ; true.
match({"baz"},{"foo"}) ; false.
```

### Fuzzy set matching

If a set contains `...` as an element it is treated as a _fuzzy_ set. The pattern set is then matched using `<=` rather than `=`; 
that is `match(SetPattern,Set) := (SetPattern-{...}) <= Set`. For example:

```
match({"foo",...}, {"foo","bar"})   ; true
match({...}, {})    ; true
match({...}, {"baz"})    ; true
```

An ellipsis may occur multiple times in a set; any extras are effectively ignored.

### Wildcard set matching

If `_` occurs in a set, it guarantees that there must at least exist an element to occupy its slot.
This item _is_ allowed to occur multiple times in a set; it effectively encodes a _size_ requirement of
the set. For example:

```
match({_,_},{"foo","bar"})  ; true
match({_,_},{"foo"})    ; false
match({_,"baz"}, {"baz","bar"}) ; true
```

That is, `match(SetPattern,Set) := (SetPattern-{_}) <= Set AND |(SetPattern-{_})| = |Set|`

## List patterns

Lists consist of square brackets containing comma-delimited elements. For example, `["foo", "bar"]`. They work just like
tuples in mathematics: duplicate elements are allowed and order matters. Matching is described with for strings. 

### Strict list matching

A list that contains only strings matches on order and length:

```
match(["foo","bar"], ["foo","bar"]) ; true
match(["foo","bar"], ["foo"])   ; false
```

In this case `match(ListPattern,List) := ListPattern = List`.

### Fuzzy list matching

A list that contains `...` is a fuzzy list. This is currently defined if `...` occurs as the first or last element of a list; that is,
as a suffix or prefix match:

```
match([...,"foo"], ["bar","baz","foo"]) ; true
match(["baz",...], ["baz"]) ; true
```

If `ListPattern[0] = ...`, then: `match(ListPattern,List) := ListPattern[1:] = List`
If `ListPattern[-1] = ...`, then: `match(ListPattern,List) := ListPattern[:-1] = List`

### Wildcard list matching

### Variable list matching