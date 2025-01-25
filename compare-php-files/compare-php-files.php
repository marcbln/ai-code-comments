<?php

require 'vendor/autoload.php';

use PhpParser\Parser;
use PhpParser\ParserFactory;
use PhpParser\NodeTraverser;
use PhpParser\NodeVisitor\CloningVisitor;
use PhpParser\PhpVersion;
use PhpParser\PrettyPrinter\Standard;
use PhpParser\Comment;

function removeCommentsAndWhitespace(array $stmts): array
{
    $traverser = new NodeTraverser;
    $traverser->addVisitor(new CloningVisitor()); // Clone nodes to avoid modifying the original AST

    // Remove comments
    foreach ($stmts as $stmt) {
        $stmt->setAttribute('comments', []);
    }

    // Normalize whitespace by pretty-printing and re-parsing
    $prettyPrinter = new Standard();
    $code = $prettyPrinter->prettyPrintFile($stmts);

    return createParser()->parse($code);
}

function createParser(): Parser
{
    return (new ParserFactory)->createForVersion(PhpVersion::fromString('8.3'));
}


function comparePhpFiles(string $file1, string $file2): bool
{
    $parser = createParser();

    // Parse the first file
    $stmts1 = $parser->parse(file_get_contents($file1));
    if ($stmts1 === null) {
        throw new RuntimeException("Failed to parse $file1");
    }

    // Parse the second file
    $stmts2 = $parser->parse(file_get_contents($file2));
    if ($stmts2 === null) {
        throw new RuntimeException("Failed to parse $file2");
    }

    // Remove comments and whitespace from both ASTs
    $stmts1 = removeCommentsAndWhitespace($stmts1);
    $stmts2 = removeCommentsAndWhitespace($stmts2);

    // Compare the ASTs
    $prettyPrinter = new Standard();
    return $prettyPrinter->prettyPrintFile($stmts1) === $prettyPrinter->prettyPrintFile($stmts2);
}

// Usage
if ($argc !== 3) {
    echo "Usage: php compare-php-files.php <file1> <file2>\n";
    exit(1);
}

$file1 = $argv[1];
$file2 = $argv[2];

if (!file_exists($file1) || !file_exists($file2)) {
    echo "Error: One or both files do not exist.\n";
    exit(1);
}

echo comparePhpFiles($file1, $file2) ? 'true' : 'false';
echo "\n";

