const jsdom = require("jsdom");
const { JSDOM } = jsdom;

function variable(name) {
    return (name[0] == name[0].toUpperCase()) || name == '_';
}

function match(node, matchRule) {
    if (matchRule.tag == '_' || matchRule.tag == node.tagName.toLowerCase()) {
        if (matchRule.children.length == 0 && (node.children == undefined || node.children.length == 0)) {
            return true;
        }

        if (matchRule.children.length == 1 && variable(matchRule.children[0].tag)) {
            return true;
        }
    }

    return false;
}

module.exports = { match };