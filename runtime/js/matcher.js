function variable(name) {
    return (name[0] == name[0].toUpperCase()) || name == '_';
}

// TODO: Text node semantics..?
function getChildren(node) {
    if (node.children == undefined) {
        return [];
    }

    return Array(...node.children).filter((child) => (typeof child) != 'Text');
}

function match(node, matchRule) {
    if (matchRule.tag == '_' || matchRule.tag == node.tagName.toLowerCase()) {
        let nodeChildren = getChildren(node);
        // (_,_,[])
        if (matchRule.children.length == 0 && nodeChildren.length == 0) {
            return true;
        }

        // (_,_,Children)
        if (matchRule.children.length == 1 && variable(matchRule.children[0].tag)) {
            return true;
        }

        // Handle nested match rules 
        // (for now, only a single variable or list of nodes can be present.)
        if (matchRule.children.length > 0 && (node.children.length == matchRule.children.length)) {
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

function unify(node, matchRule, rewriteRule, document) {
    console.assert(match(node, matchRule));

    let tag = matchRule.tag;
    if (tag == '_') {
        tag = node.tag;
    }

    // For now, only perform direct tag substitutions
    let element = document.createElement(rewriteRule.tag);
    return element;
}

module.exports = { match, unify };