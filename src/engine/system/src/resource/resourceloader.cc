/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#include    <system/stdafx.h>
#include    <system/resource/resourceloader.hh>


namespace BugEngine
{

IResourceLoader::IResourceLoader(weak<pointer> loader)
    :   m_loader(loader)
{
}

IResourceLoader::~IResourceLoader()
{
}

}