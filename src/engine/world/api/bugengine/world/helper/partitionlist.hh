/* BugEngine <bugengine.devel@gmail.com> / 2008-2014
   see LICENSE for detail */

#ifndef BE_WORLD_HELPER_PARTITIONLIST_HH_
#define BE_WORLD_HELPER_PARTITIONLIST_HH_
/**************************************************************************************************/
#include <bugengine/world/stdafx.h>
#include <bugengine/rtti/engine/propertyinfo.script.hh>
#include <bugengine/rtti/value.hh>
#include <bugengine/world/helper/partition.hh>

namespace BugEngine { namespace World {

template < typename T, typename TAIL >
struct PartitionList : public TAIL
{
    enum
    {
        Index = TAIL::Index + 1
    };
    typedef T    Type;
    typedef TAIL Tail;
    T            m_partition;
    PartitionList(weak< Task::ITask > task) : TAIL(task), m_partition(task)
    {
    }
    static void
    addPartition(minitl::vector< minitl::array< raw< const RTTI::Class > > >& partitions)
    {
        partitions.push_back(
           minitl::array< raw< const RTTI::Class > >(Arena::temporary(), T::Index + 1));
        T::buildList(partitions.back().begin());
        Tail::addPartition(partitions);
    }

private:
    PartitionList(const PartitionList& other);
    PartitionList& operator=(const PartitionList& other);
};

template < typename T >
struct PartitionList< T, void >
{
    enum
    {
        Index = 0
    };
    typedef T    Type;
    typedef void Tail;
    T            m_partition;
    PartitionList(weak< Task::ITask > task) : m_partition(task)
    {
    }
    static void
    addPartition(minitl::vector< minitl::array< raw< const RTTI::Class > > >& partitions)
    {
        partitions.push_back(
           minitl::array< raw< const RTTI::Class > >(Arena::temporary(), T::Index + 1));
        T::buildList(partitions.back().begin());
    }

private:
    PartitionList(const PartitionList& other);
    PartitionList& operator=(const PartitionList& other);
};

namespace Helper {

template < typename T, typename T2, typename TAIL >
struct PartitionGetter
{
    static const T& getPartition(const PartitionList< T2, TAIL >& list)
    {
        return PartitionGetter< T, typename TAIL::Type, typename TAIL::Tail >::getPartition(list);
    }
};

template < typename T, typename TAIL >
struct PartitionGetter< T, T, TAIL >
{
    static const T& getPartition(const PartitionList< T, TAIL >& list)
    {
        return list.m_partition;
    }
};

template < typename PARTITIONLIST, u32 INDEX, typename T, typename TAIL >
struct PartitionListPropertyInfo
{
    static inline void fillProperty(RTTI::Property properties[])
    {
        typedef PartitionListPropertyInfo< PARTITIONLIST, INDEX + 1, typename TAIL::Type,
                                           typename TAIL::Tail >
                       PropertyParent;
        RTTI::Property property = {{0},
                                   T::name(),
                                   be_type< PARTITIONLIST >(),
                                   be_type< const T& >(),
                                   &PARTITIONLIST::template getPartition< T >};
        new(&properties[INDEX]) RTTI::Property(property);
        PropertyParent::fillProperty(properties);
    }
};

template < typename PARTITIONLIST, u32 INDEX, typename T >
struct PartitionListPropertyInfo< PARTITIONLIST, INDEX, T, void >
{
    static inline void fillProperty(RTTI::Property properties[])
    {
        RTTI::Property property = {{0},
                                   T::name(),
                                   be_type< PARTITIONLIST >(),
                                   be_type< const T& >(),
                                   &PARTITIONLIST::template getPartition< T >};
        new(&properties[INDEX]) RTTI::Property(property);
    }
};

}  // namespace Helper

template < typename T1 = void, typename T2 = void, typename T3 = void, typename T4 = void,
           typename T5 = void, typename T6 = void, typename T7 = void, typename T8 = void,
           typename T9 = void, typename T10 = void, typename T11 = void, typename T12 = void,
           typename T13 = void, typename T14 = void, typename T15 = void, typename T16 = void,
           typename T17 = void, typename T18 = void, typename T19 = void, typename T20 = void,
           typename T21 = void, typename T22 = void, typename T23 = void, typename T24 = void,
           typename T25 = void, typename T26 = void, typename T27 = void, typename T28 = void,
           typename T29 = void, typename T30 = void, typename T31 = void, typename T32 = void >
struct MakePartitionList
{
    typedef PartitionList<
       T1, typename MakePartitionList< T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15,
                                       T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27,
                                       T28, T29, T30, T31, T32 >::Result >
       Result;
};

template <>
struct MakePartitionList<>
{
    typedef void Result;
};

}}  // namespace BugEngine::World

/**************************************************************************************************/
#endif