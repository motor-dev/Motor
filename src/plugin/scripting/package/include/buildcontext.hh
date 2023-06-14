/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_SCRIPTING_PACKAGE_BUILDCONTEXT_HH
#define MOTOR_PLUGIN_SCRIPTING_PACKAGE_BUILDCONTEXT_HH

#include <motor/plugin.scripting.package/stdafx.h>
#include <motor/plugin.scripting.package/nodes/package.hh>

#include <motor/introspect/node/node.hh>
#include <motor/plugin/plugin.hh>

struct FileOffset
{
    int line;
    int column;
    int start;
    int end;
};

union YYSTYPE
{
    const char* id;
    FileOffset  offset;
};

#define YYSTYPE_IS_DECLARED 1
#define YYSTYPE_IS_TRIVIAL  1

namespace Motor { namespace PackageBuilder {

struct BuildContext
{
    ref< Nodes::Package > result;

    BuildContext(const ifilename& filename, const minitl::allocator::block< u8 >& buffer,
                 ref< Folder > folder);
    ~BuildContext();
};

}}  // namespace Motor::PackageBuilder

extern int g_packageOffset;
extern int g_packageLine;
extern int g_packageColumnBefore;
extern int g_packageColumnAfter;
extern int g_packageObjectNestedLevel;

extern const minitl::allocator::block< u8 >* g_buffer;
extern int                                   g_bufferPosition;

#endif
