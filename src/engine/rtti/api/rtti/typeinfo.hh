/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#ifndef BE_RTTI_TYPEINFO_HH_
#define BE_RTTI_TYPEINFO_HH_
/*****************************************************************************/
#include    <rtti/typeinfo.script.hh>

namespace BugEngine
{

template< typename T >
struct be_api(RTTI) be_typeid
{
    static ref<const RTTI::ClassInfo> const klass();
    static TypeInfo type();
};

template< > ref<const RTTI::ClassInfo> const be_typeid< void >::klass();

}

#include <rtti/typeinfo.inl>

/*****************************************************************************/
#endif
