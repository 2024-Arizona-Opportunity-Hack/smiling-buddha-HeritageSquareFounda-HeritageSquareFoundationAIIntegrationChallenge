import { TransformComponent, TextNode } from "llamaindex";

export class AddFileName extends TransformComponent {
  async transform(nodes: TextNode[]): Promise<TextNode[]> {
    for (const node of nodes) {
      node.text = node.metadata["dDRive_DocName"] + " " + node.text
    }

    return nodes;
  }
}