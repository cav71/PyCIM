
def parents(node, include_node=True, result=None):
    "returns all the parent nodes"
    if not result:
        result = [ node, ]
    parent = node.getparent()
    if parent is None:
        result = [ n for n in reversed(result) ]
        if not include_node:
            return result[:-1]
        else:
            return result
    else:
        result.append(parent)
        return parents(parent, include_node, result)

