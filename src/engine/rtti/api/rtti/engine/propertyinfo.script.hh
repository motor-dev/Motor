/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#ifndef BE_RTTI_ENGINE_PROPERTYINFO_SCRIPT_HH_
#define BE_RTTI_ENGINE_PROPERTYINFO_SCRIPT_HH_
/*****************************************************************************/
#include   <rtti/typeinfo.hh>

namespace BugEngine { namespace RTTI
{

struct PropertyInfo
{
    const char *            name;
    raw<const ClassInfo>    type;
    size_t                  offset;
};

}}

/*****************************************************************************/
#endif
