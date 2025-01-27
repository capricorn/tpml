const TEXT_NODE = 3;

function variable(name) {
    return (name[0] == name[0].toUpperCase()) || name == '_';
}

function type_unpack(tag) {
    return tag == 'unpack';
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

    // If attributes contains a single Variable element extract
    // the entire set as a var
    if (matchRule.attrs.length == 1 && (matchRule.attrs[0].tag[0].toUpperCase() == matchRule.attrs[0].tag[0])) {
        vars[matchRule.attrs[0].tag] = extract_node_attrs(node);
    }

    return vars;
}

// Return a dictionary containing the html node attributes.
function extract_node_attrs(node) {
    let attrs = {};
    for (const attr of node.attributes) {
        let values = attr.value.split(' ');
        if (values.length > 1) {
            attrs[attr.name] = values;
        } else {
            attrs[attr.name] = attr.value;
        }
    }

    return attrs;
}

function resolveVariableIndex(vars, varIndexAST) {
    return vars[varIndexAST.var][varIndexAST.index];
}

// new_entries_map: js object
function map_insert(map, new_entries_map) {
    let newMap = new Map(map);

    for (const [key,value] of new_entries_map) {
        newMap.set(key, value);
    }

    return newMap;
}

function clearNodeAttributes(node) {
    for (const attr of node.attributes) {
        node.removeAttribute(attr.name)
    }
}

function replaceNodeAttributes(node, newAttrsMap) {
    clearNodeAttributes(node);
    for (const [key,value] of newAttrsMap) {
        node.setAttribute(key, value);
    }
}

// TODO: Load a tpml dict as a JS dict
function reify_dict_as_map(dict_ast_entries, vars) {
    // Given a dictionary ast in rewriteRule,
    // instantiate it as a js dict unpacking and inserting any
    // vars in the process. 
    // A dict is simply a list containing (for now...):
    // 1. (String,String)
    // 2. (String,[String])
    // 3. Var
    // 4. Unpack(Var)

    let map = new Map();
    for (const entry of dict_ast_entries) {
        if (entry.tag && variable(entry.tag)) {
            //console.assert(false, 'Unimplemented');
            // A variable in this context is expected to be a dict itself.
            // (In this case the expectation is totally concrete, ie no vars, unpacking etc)
            map = map_insert(map, Object.entries(vars[entry.tag]));
        } else if (type_unpack(entry.tag)) {
            // TODO
            console.assert(false, 'Unimplemented');
        } else {
            // If it isn't a variable or unpack of a variable, the key is a string.
            console.assert(entry.length == 2, `Bad [String,String] len: ${entry.length}`);
            console.assert(entry[0].tag == 'string', `Bad [String,String] value type: ${entry[0].value}`);

            // TODO: The val (in this case) may be a list of strings; this
            // needs handled specially; for now, disallow
            console.assert(entry[1].tag == 'string');

            let [key,val] = entry;
            map.set(key.value, val.value);
        }
    }

    return map;
}

function unify(node, matchRule, rewriteRule, document) {
    console.assert(match(node, matchRule));

    let tag = matchRule.tag;
    if (tag == '_') {
        tag = node.tag;
    }

    

    // For now, only perform direct tag substitutions
    // TODO: Stop creating a new element--this will likely break the page.
    let element = document.createElement(rewriteRule.tag);

    // Attributes rewriting
    // TODO: Handle wildcard
    let vars = extract_variables(node, matchRule);
    let newAttrs = reify_dict_as_map(rewriteRule.attrs, vars);
    replaceNodeAttributes(element, newAttrs);

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

module.exports = { 
    match, 
    matchSet, 
    unify, 
    unify_tree, 
    extract_variables, 
    extract_node_attrs, 
    reify_dict_as_map ,
    resolveVariableIndex
};