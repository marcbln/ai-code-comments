<?php

namespace App;

use PhpParser\NodeVisitorAbstract;

/**
 * Class MyNodeVisitor
 * This class extends NodeVisitorAbstract and is used to traverse and modify PHP nodes.
 * Specifically, it removes comments from nodes during the traversal process.
 */
class MyNodeVisitor extends NodeVisitorAbstract
{
    /**
     * Called before the traversal of a node tree begins.
     *
     * @param array $nodes The array of nodes to be traversed.
     */
    public function beforeTraverse(array $nodes)
    {
        return null;
    }

    /**
     * Called when entering a node.
     *
     * @param \PhpParser\Node $node The node being entered.
     */
    public function enterNode(\PhpParser\Node $node)
    {
        // ---- Check if the node has comments and remove them
        if (isset($node->getAttributes()['comments'])) {
            $node->setAttribute('comments', null);
        }
        return null;
    }

    /**
     * Called when leaving a node.
     *
     * @param \PhpParser\Node $node The node being left.
     */
    public function leaveNode(\PhpParser\Node $node)
    {
        return null;
    }

    /**
     * Called after the traversal of a node tree is complete.
     *
     * @param array $nodes The array of nodes that were traversed.
     */
    public function afterTraverse(array $nodes)
    {
        return null;
    }
}