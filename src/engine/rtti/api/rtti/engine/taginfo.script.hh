/* BugEngine / 2008-2012  Nicolas MERCIER <mercier.nicolas@gmail.com>
   see LICENSE for detail */

#ifndef BE_RTTI_ENGINE_TAGINFO_SCRIPT_HH_
#define BE_RTTI_ENGINE_TAGINFO_SCRIPT_HH_
/*****************************************************************************/
#include    <rtti/value.hh>

namespace BugEngine { namespace RTTI
{

struct be_api(RTTI) Tag
{
    raw<Tag> const next;
    Value tag;
};

}}

/*****************************************************************************/
#endif

