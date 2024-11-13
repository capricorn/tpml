
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

`A <= B` means `A` subset of `B`.

## Strings

Strings are double-quoted as seen in many other programming languages, e.g. `"foo"`, `"bar"`. They currently do _not_ support
nested quotes (string escapes are unimplemented.)

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