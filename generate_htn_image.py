import re
from graphviz import Digraph

def parse_plan(plan_text: str) -> Digraph:
    lines = plan_text.strip().splitlines()
    data = {}
    order = None
    warnings = []

    dot = Digraph("HTN")
    dot.attr(overlap='false')
    dot.attr(splines='true')
    dot.attr(dpi='300')
    dot.attr(size='10,5')

    for i, line in enumerate(lines):
        l = line.strip()
        if not l:
            continue

        action_match = re.match(r"^(\d+)\s+([\w\s()\-]+)$", l)
        method_match = re.match(r"^(\d+)\s+([\w\s()\-]+?)\s+->\s+([\w\-]+)\s*([\d\s]*)$", l)
        root_match = re.match(r"^root\s*([\d\s]*)$", l)

        if action_match:
            idx, label = action_match.groups()
            data[idx] = (f'{idx}', label, 'box3d', [])
        elif method_match:
            idx, task, method, children = method_match.groups()
            child_list = children.strip().split() if children.strip() else []
            data[idx] = (f'{idx}', task, 'box', child_list)
            data[f"m{idx}"] = (f"m{idx}", method, 'ellipse', [])
        elif root_match:
            order = root_match.group(1).strip().split()
        else:
            warnings.append(f"Ignoring line {i+1}: {l}")

    if order is None:
        raise ValueError("Expected root")

    dot.node("root", shape="point")
    for o in order:
        dot.edge("root", o)

    queue = list(order)
    visited = set()
    # print(f"Queue: {queue}")

    while queue:
        current = queue.pop(0)
        # print(f"Current: {current}")
        if current in visited or current not in data:
            continue
        visited.add(current)

        node_id, label, shape, children = data[current]
        dot.node(node_id, label=label, shape=shape)

        for child in children:
            # dot.edge(node_id, child)
            queue.append(child)

        # If it's a method, add a separate node and edge to show method decomposition
        if current in data and current.startswith("m"):
            continue
        if f"m{current}" in data:
            method_id, method_label, _, _ = data[f"m{current}"]
            dot.node(method_id, label=method_label)
            dot.edge(current, method_id)
            for child in data[current][3]:
                dot.edge(method_id, child)
    # print("graph created", dot.source)
    return dot

# Example usage
if __name__ == "__main__":
    with open("plan.txt", "r") as f:
        plan_content = f.read()

    match = re.search(r"==>\n([^<]*)", plan_content, re.DOTALL)
    input_text = match.group(1).strip() if match else plan_content

    dot_graph = parse_plan(input_text)
    dot_graph.render("htn_plan", format="png", cleanup=True)
    print("Saved as htn_plan.png")
