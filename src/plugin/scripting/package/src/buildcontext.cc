/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#include    <package/stdafx.h>
#include    <buildcontext.hh>

int be_package_lex_destroy();

const BugEngine::Allocator::Block<u8>* g_buffer = 0;
int g_bufferPosition = 0;
int g_packageLine = 0;
int g_packageColumnBefore = 0;
int g_packageColumnAfter = 0;
static i_u32 s_useCount = 0;

namespace BugEngine { namespace PackageBuilder
{

BuildContext::BuildContext(const Allocator::Block<u8>& buffer)
    :   result(ref<Nodes::Package>::create(packageBuilderArena()))
{
    be_assert(s_useCount++ == 0, "non reentrant parser used by two threads");
    g_buffer = &buffer;
    g_bufferPosition = 0;
    g_packageLine = 0;
    g_packageColumnBefore = g_packageColumnAfter = 0;
}

BuildContext::~BuildContext()
{
    be_package_lex_destroy();
    g_buffer = 0;
    g_bufferPosition = 0;
    --s_useCount;
}

}}