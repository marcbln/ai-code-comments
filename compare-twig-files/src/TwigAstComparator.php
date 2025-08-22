<?php

namespace Aicoder\TwigAstComparator;

use Twig\Environment;
use Twig\Loader\ArrayLoader;
use Twig\Node\Node;
use Twig\NodeTraverser;
use Twig\NodeVisitor\NodeVisitorInterface;

class TwigAstComparator
{
    private Environment $twig;

    public function __construct()
    {
        $this->twig = new Environment(new ArrayLoader());
    }

    public function compareFiles(string $file1, string $file2): bool
    {
        if (!file_exists($file1) || !file_exists($file2)) {
            throw new \InvalidArgumentException("One or both files do not exist.");
        }

        $content1 = file_get_contents($file1);
        $content2 = file_get_contents($file2);

        return $this->compareContents($content1, $content2);
    }

    public function compareContents(string $content1, string $content2): bool
    {
        // Normalize content by removing comments and extra whitespace
        $normalized1 = $this->normalizeContent($content1);
        $normalized2 = $this->normalizeContent($content2);
        
        // If normalized content is identical, they're equivalent
        if ($normalized1 === $normalized2) {
            return true;
        }
        
        // Otherwise, compare AST structure
        try {
            $ast1 = $this->parseTwig($normalized1);
            $ast2 = $this->parseTwig($normalized2);
            return $this->compareNodes($ast1, $ast2);
        } catch (\Exception $e) {
            // If parsing fails, fall back to normalized content comparison
            return $normalized1 === $normalized2;
        }
    }

    private function normalizeContent(string $content): string
    {
        // Remove Twig comments {# ... #}
        $content = preg_replace('/\{#.*?#\}/s', '', $content);
        
        // Remove HTML comments <!-- ... -->
        $content = preg_replace('/<!--.*?-->/s', '', $content);
        
        // Normalize whitespace
        $content = preg_replace('/\s+/', ' ', $content);
        $content = trim($content);
        
        return $content;
    }

    private function parseTwig(string $content): Node
    {
        try {
            $tokens = $this->twig->tokenize(new \Twig\Source($content, 'template'));
            return $this->twig->parse($tokens);
        } catch (\Exception $e) {
            throw new \RuntimeException("Failed to parse Twig content: " . $e->getMessage());
        }
    }

    private function compareNodes(Node $node1, Node $node2): bool
    {
        // Compare node types
        if (get_class($node1) !== get_class($node2)) {
            return false;
        }

        // Compare child nodes
        $children1 = iterator_to_array($node1);
        $children2 = iterator_to_array($node2);

        if (count($children1) !== count($children2)) {
            return false;
        }

        foreach ($children1 as $index => $child1) {
            if (!isset($children2[$index])) {
                return false;
            }
            $child2 = $children2[$index];
            if (!$this->compareNodes($child1, $child2)) {
                return false;
            }
        }

        return true;
    }
}