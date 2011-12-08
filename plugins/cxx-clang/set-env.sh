#!/bin/sh

export CC="$DXRSRC/plugins/cxx-clang/cc.sh clang $SRCDIR"
export CXX="$DXRSRC/plugins/cxx-clang/cc.sh clang++ $SRCDIR"
export DXR_INDEX_OUTPUT="$OBJDIR"
export DXR_ENV_SET="true"
