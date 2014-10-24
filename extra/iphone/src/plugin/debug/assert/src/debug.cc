/* BugEngine <bugengine.devel@gmail.com> / 2008-2014
   see LICENSE for detail */

#include    <stdafx.h>
#include    <minitl/assert.hh>
#include    <cstdio>
#include    <cstdarg>

namespace BugEngine { namespace Debug
{

minitl::AssertionResult AssertionCallback(const char *file,
                                          int        line,
                                          const char *expr,
                                          const char *message)
{
    fprintf(stderr, "%s:%d Assertion failed: %s\n\t", file, line, expr);
    fprintf(stderr, "%s\n", message);

    return minitl::Break;
}

}}
