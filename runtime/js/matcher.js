const TEXT_NODE = 3;

function variable(name) {
    return (name[0] == name[0].toUpperCase()) || name == '_';
}

// TODO: Text node semantics..?
function getChildren(node) {
    if (node.children == undefined) {
        return [];
    }

    return Array(...node.children).filter((child) => child.nodeType != TEXT_NODE);
}

function matchSet(jsSet, setMatchRule) {
    // If setMatchRule contains 'nodeType: ellipsis' then it's a fuzzy match
    // Otherwise, strict set equality
    let fuzzyMatch = (setMatchRule.members.filter(m => m.nodeType == 'ellipsis').length > 0);
    if (fuzzyMatch) {
        let members = new Set(setMatchRule.members
            .filter(m => m.nodeType != 'ellipsis')
            .map(m => m.value)); // All values in this case should be strings

        // The js set should at least include all of the members (ie a superset of the match rule)
        return members.isSubsetOf(jsSet);
    } else {
        let members = new Set(setMatchRule.members
            .map(m => m.value)); // All values in this case should be strings

        // Strict equality
        return (jsSet.difference(members).size == 0);
    }
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

// Return variables in node via matchRule (dictionary keyed by variable name in matchRule)
function extract_variables(node, matchRule) {
    let vars = {};
    // Variable extraction applies to the left node in unification
    // The tag itself is a variable
    let nodeTypeVariable = (matchRule.tag[0].toUpperCase() == matchRule.tag[0]);
    if (nodeTypeVariable) {
        vars[matchRule.tag] = node.tagName.toLowerCase();
    }

    return vars;
}

// TODO: Load a tpml dict as a JS dict
function reify_dict(dict_ast) {}

function unify(node, matchRule, rewriteRule, document) {
    console.assert(match(node, matchRule));

    let tag = matchRule.tag;
    if (tag == '_') {
        tag = node.tag;
    }

    // For now, only perform direct tag substitutions
    let element = document.createElement(rewriteRule.tag);

    for (const child of node.childNodes) {
        element.appendChild(child);
    }

    return [element, getChildren(node)];
}

function unify_tree(root_node, matchRule, rewriteRule, document) {
    let children = getChildren(root_node);

    if (match(root_node, matchRule)) {
        let new_node;
        [new_node, children] = unify(root_node, matchRule, rewriteRule, document);
        root_node.replaceWith(new_node);
    }

    for (const child of children) {
        unify_tree(child, matchRule, rewriteRule, document);
    }
}

module.exports = { match, matchSet, unify, unify_tree, extract_variables };