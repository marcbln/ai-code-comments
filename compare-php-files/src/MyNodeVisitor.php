<?php

namespace App;

use PhpParser\NodeVisitorAbstract;

class MyNodeVisitor extends NodeVisitorAbstract
{
    public function beforeTraverse(array $nodes)
    {
        return null;
    }

    public function enterNode(\PhpParser\Node $node)
    {
        // Remove the docComment property from the node
        if (isset($node->getAttributes()['comments'])) {
            $node->setAttribute('comments', null);
        }
        return null;
    }

    public function leaveNode(\PhpParser\Node $node)
    {
        return null;
    }

    public function afterTraverse(array $nodes)
    {
        return null;
    }
}