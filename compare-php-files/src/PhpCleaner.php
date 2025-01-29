<?php

namespace App;

use PhpParser\NodeTraverser;
use PhpParser\NodeVisitor\CloningVisitor;
use PhpParser\Parser;
use PhpParser\ParserFactory;
use PhpParser\PhpVersion;
use PhpParser\PrettyPrinter\Standard;
use PhpParser\Comment;

class PhpCleaner
{
    private Parser $parser;

    public function __construct()
    {
        $this->parser = (new ParserFactory)->createForVersion(PhpVersion::fromString('8.3'));

    }

    public function removeCommentsAndWhitespace($code): string
    {
        // Parse the code into an AST
        $ast = $this->parser->parse($code);

        // Create a traverser and add a visitor to strip docblocks
        $traverser = new NodeTraverser();
        $traverser->addVisitor(new MyNodeVisitor());

        // Traverse and modify the AST
        $ast = $traverser->traverse($ast);

        // Pretty-print the modified AST back to PHP code
        $prettyPrinter = new Standard();
        $newCode = $prettyPrinter->prettyPrintFile($ast);

        return $newCode;
    }

}