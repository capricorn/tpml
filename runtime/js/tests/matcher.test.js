import { expect, test, assert } from 'vitest';
import { match, unify, unify_tree } from '../matcher';
import { html_beautify } from 'js-beautify';
const jsdom = require("jsdom");
const { JSDOM } = jsdom;

function beautify(html) {
    let options = {
        "indent_size": "4",
        "indent_char": " ",
        "max_preserve_newlines": "-1",
        "preserve_newlines": false,
        "keep_array_indentation": false,
        "break_chained_methods": false,
        "indent_scripts": "normal",
        "brace_style": "collapse",
        "space_before_conditional": true,
        "unescape_strings": false,
        "jslint_happy": false,
        "end_with_newline": false,
        "wrap_line_length": "0",
        "indent_inner_html": true,
        "comma_first": false,
        "e4x": false,
        "indent_empty_lines": false
    };

    return html_beautify(html, options)
}

test('Match wildcard tag', () => {
    const doc = `
        <html>
            <body>
                <p></p>
                <p></p>
            </body>
        </html>
    `;

    // Match nodes with any tag and any number of children
    const matchRule = {
        tag: "_",
        attrs: [],
        children: [ { tag: "_", attrs: [], children: [] } ]
    };

    let dom = new JSDOM(doc);
    expect(match(dom.window.document, matchRule)).toBe(true);
});

test('Match wildcard tag with children literal', () => {
    const doc = `
        <html>
            <body>
                <p></p>
                <p></p>
            </body>
        </html>
    `;

    // Match nodes with any tag and no children
    const matchRule = {
        tag: "_",
        attrs: [],
        children: []
    };

    let dom = new JSDOM(doc);
    expect(match(dom.window.document, matchRule)).toBe(false);
    // TODO: Why is this undefined?
    // assert(dom.window.document.body.firstChild.children != undefined);
    // No children so this node matches.
    expect(match(dom.window.document.body.querySelector('p'), matchRule)).toBe(true);
});

test('Fail exact match nested node', () => {
    const doc = `
        <html>
            <body>
                <p></p>
                <p></p>
            </body>
        </html>
    `;

    // Match nodes with any tag and no children
    const matchRule = {
        tag: "body",
        attrs: [],
        children: [
            {
                tag: "p",
                attrs: [],
                children: []
            }
        ]
    };

    let dom = new JSDOM(doc);
    expect(match(dom.window.document.body, matchRule)).toBe(false);
});

test('Exact match nested node', () => {
    const doc = `
        <html>
            <body>
                <p></p>
            </body>
        </html>
    `;

    // Match nodes with any tag and no children
    const matchRule = {
        tag: "body",
        attrs: [],
        children: [
            {
                tag: "p",
                attrs: [],
                children: []
            }
        ]
    };

    let dom = new JSDOM(doc);
    expect(match(dom.window.document.body, matchRule)).toBe(true);
});

test('Unify: change tag name', () => {
    const doc = `
        <html>
            <body>
                <p></p>
            </body>
        </html>
    `;

    const matchRule = {
        tag: 'p',
        attrs: [],
        children: []
    };

    const rewriteRule = {
        tag: 'span',
        attrs: [],
        children: []
    };

    let dom = new JSDOM(doc);
    let [result, children] = unify(dom.window.document.body.querySelector('p'), matchRule, rewriteRule, dom.window.document);
    expect(children.length).toBe(0);
    expect(result.tagName.toLowerCase()).toBe('span');
});

test('unify_tree: bold to italic', () => {
    const doc = `
        <html>
            <head></head>
            <body>
                <b>hello</b>
                <p></p>
            </body>
        </html>
    `;

    const transformedDoc = `
        <html>
            <head></head>
            <body>
                <i>hello</i>
                <p></p>
            </body>
        </html>
    `;

    const matchRule = {
        tag: 'b',
        attrs: [],
        children: [
            {
                tag: '_',
                attrs: [],
                children: []
            }
        ]
    };

    const rewriteRule = {
        tag: 'i',
        attrs: [],
        children: [
            {
                tag: '_',
                attrs: [],
                children: []
            }
        ]
    };

    let dom = new JSDOM(doc);
    unify_tree(dom.window.document.documentElement, matchRule, rewriteRule, dom.window.document);
    let result = dom.window.document.documentElement.outerHTML;

    expect(beautify(transformedDoc)).toBe(beautify(result));
})

test('Unify: delete node', () => {
    // TODO: Delete all <p> nodes i.e. (p,[],_) = ()
    // Above is regardless of child nodes of <p>
});