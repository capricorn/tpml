import { expect, test, assert } from 'vitest';
import { match } from '../matcher';
const jsdom = require("jsdom");
const { JSDOM } = jsdom;

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
    expect(match(dom.window.document.body.firstChild, matchRule)).toBe(true);
});