#!/usr/bin/env bash

PWD=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

FILE1=$PWD/test-files/test1.php
FILE2=$PWD/test-files/test2.php

echo "Comparing $(basename $FILE1) and $(basename $FILE2)"
php $PWD/compare-php-files.php $FILE1 $FILE2
