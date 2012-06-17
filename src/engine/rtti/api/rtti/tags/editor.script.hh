/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#ifndef BE_RTTI_TAGS_EDITOR_SCRIPT_HH_
#define BE_RTTI_TAGS_EDITOR_SCRIPT_HH_
/*****************************************************************************/

namespace BugEngine { namespace EditHint
{

struct be_api(RTTI) Extension
{
    const istring ext;
    Extension(const istring& ext) : ext(ext) { }
};

struct be_api(RTTI) Temporary
{
    Temporary() { }
};

struct be_api(RTTI) OutputNode
{
    OutputNode() { }
};

}}

/*****************************************************************************/
#endif

