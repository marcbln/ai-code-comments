<?php

namespace App;

use PhpParser\Node;
use PhpParser\NodeVisitorAbstract;

// hello
class MyNodeVisitor extends NodeVisitorAbstract
{
   // world
    public function beforeTraverse(array $nodes)
    {
        return null;
    }

}
