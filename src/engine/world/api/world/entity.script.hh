/* BugEngine / 2008-2012  Nicolas MERCIER <mercier.nicolas@gmail.com>
   see LICENSE for detail */

#ifndef BE_WORLD_ENTITY_SCRIPT_HH_
#define BE_WORLD_ENTITY_SCRIPT_HH_
/*****************************************************************************/

namespace BugEngine { namespace World
{

struct be_api(WORLD) Entity
{
    u32 id;


    bool operator ==(const Entity& other) const { return id == other.id; }
    bool operator !=(const Entity& other) const { return id != other.id; }
    bool operator < (const Entity& other) const { return id < other.id; }
};

}}


/*****************************************************************************/
#endif
