// swig/Python/snowboy-detect-swig.i

// Copyright 2016  KITT.AI (author: Guoguo Chen)

%module snowboydetect

// Suppress SWIG warnings.
#pragma SWIG nowarn=SWIGWARN_PARSE_NESTED_CLASS
%include "std_string.i"

%{
#include "snowboy-detect.h"
%}

%include "snowboy-detect.h"

%begin %{
#define SWIG_PYTHON_STRICT_BYTE_CHAR
%}
