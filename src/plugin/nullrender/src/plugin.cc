/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#include    <stdafx.h>
#include    <nullrenderer.hh>
#include    <system/plugin.hh>

BE_PLUGIN_REGISTER(nullrender, BugEngine::Graphics::Null::NullRenderer, (weak<const BugEngine::FileSystem> fileSystem), (fileSystem));