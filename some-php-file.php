<?php

namespace App;

use PhpParser\Node;
use PhpParser\NodeVisitorAbstract;

class MyNodeVisitor extends NodeVisitorAbstract
{
    public function beforeTraverse(array $nodes)
    {
        return null;
    }
}
