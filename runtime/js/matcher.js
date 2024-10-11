const jsdom = require("jsdom");
const { JSDOM } = jsdom;

function variable(name) {
    return (name[0] == name[0].toUpperCase()) || name == '_';
}

function match(node, matchRule) {
    if (matchRule.tag == '_' || matchRule.tag == node.tagName.toLowerCase()) {
        // (_,_,[])
        if (matchRule.children.length == 0 && (node.children == undefined || node.children.length == 0)) {
            return true;
        }

        // (_,_,Children)
        if (matchRule.children.length == 1 && variable(matchRule.children[0].tag)) {
            return true;
        }

        // Handle nested match rules 
        // (for now, only a single variable or list of nodes can be present.)
        if (matchRule.children.length > 0 && node.children.length == matchRule.children.length) {
            for (let i = 0; i < matchRule.children.length; i++) {
                if (match(node.children[i], matchRule.children[i]) == false) {
                    return false
                }
            }

            return true;
        }
    }

    return false;
}

module.exports = { match };