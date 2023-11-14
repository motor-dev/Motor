/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.package/stdafx.h>
#include <buildcontext.hh>

int motor_package_lex_destroy();

const minitl::allocator::block< u8 >* g_buffer                   = nullptr;
int                                   g_bufferPosition           = 0;
int                                   g_packageOffset            = 0;
int                                   g_packageLine              = 0;
int                                   g_packageColumnBefore      = 0;
int                                   g_packageColumnAfter       = 0;
int                                   g_packageObjectNestedLevel = 0;
static i_u32                          s_useCount                 = i_u32::create(0);

namespace Motor { namespace PackageBuilder {

BuildContext::BuildContext(const ifilename& filename, const minitl::allocator::block< u8 >& buffer,
                           const ref< Folder >& folder)
    : result(scoped< Nodes::Package >::create(Arena::packageBuilder(), filename, folder))
{
    motor_assert(s_useCount++ == 0, "non reentrant parser used by two threads");
    g_buffer              = &buffer;
    g_bufferPosition      = 0;
    g_packageOffset       = 0;
    g_packageLine         = 0;
    g_packageColumnBefore = g_packageColumnAfter = 0;
    g_packageObjectNestedLevel                   = 0;
}

BuildContext::~BuildContext()
{
    motor_package_lex_destroy();
    g_buffer         = nullptr;
    g_bufferPosition = 0;
    --s_useCount;
}

}}  // namespace Motor::PackageBuilder
