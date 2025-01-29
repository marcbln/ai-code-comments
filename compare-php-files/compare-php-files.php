<?php

require 'vendor/autoload.php';

use App\PhpCleaner;


function main(string $file1, string $file2, bool $debug)
{
    $cleaner = new PhpCleaner();

    $code1 = $cleaner->removeCommentsAndWhitespace(file_get_contents($file1));
    $code2 = $cleaner->removeCommentsAndWhitespace(file_get_contents($file2));

    $equal = $code1 === $code2;

    if ($debug && !$equal) {
        echo "=== File 1 ($file1) ===\n";
        echo $code1 . "\n\n";
        echo "=== File 2 ($file2) ===\n";
        echo $code2 . "\n\n";

        // Show diff using similar_text
        similar_text($code1, $code2, $percent);
        echo sprintf("Similarity: %.2f%%\n", $percent);
    }

    return $equal;
}

// Parse command line arguments
$options = getopt('', ['debug']);
$debug = isset($options['debug']);

// Remove the processed options from argv
$nonOptionArgv = array_values(array_filter($argv, function ($arg) {
    return !str_starts_with($arg, '--');
}));

if (count($nonOptionArgv) !== 3) {
    echo "Usage: php compare-php-files.php [--debug] <file1> <file2>\n";
    exit(1);
}

$file1 = $nonOptionArgv[1];
$file2 = $nonOptionArgv[2];

echo main($file1, $file2, $debug) ? 'true' : 'false';
echo "\n";

