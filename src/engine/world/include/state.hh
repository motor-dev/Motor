/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#ifndef BE_WORLD_STATE_HH_
#define BE_WORLD_STATE_HH_
/*****************************************************************************/
#include    <world/component.script.hh>
#include    <minitl/container/bitset.hh>

namespace BugEngine { namespace World
{

class Rule;

class State : public minitl::pointer
{
private:
    struct Group
    {
//        Storage storage;
        u32 start;
        u32 end;
        u16 componentMask;
    };
    minitl::array< Group >  m_groups;
public:
    State();
    ~State();
};


}}


/*****************************************************************************/
#endif
