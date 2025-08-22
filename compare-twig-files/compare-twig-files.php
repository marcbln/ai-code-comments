#!/usr/bin/env php
<?php

require_once __DIR__ . '/vendor/autoload.php';

use Aicoder\TwigAstComparator\TwigAstComparator;

if ($argc !== 3) {
    echo "Usage: php compare-twig-files.php <file1.twig> <file2.twig>\n";
    exit(1);
}

$file1 = $argv[1];
$file2 = $argv[2];

$comparator = new TwigAstComparator();

try {
    if ($comparator->compareFiles($file1, $file2)) {
        echo "true";
        exit(0);
    } else {
        echo "false";
        exit(1);
    }
} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
    exit(1);
}