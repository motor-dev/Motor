/* BugEngine <bugengine.devel@gmail.com> / 2008-2014
   see LICENSE for detail */

#ifndef BE_WORLD_HELPER_PARTITION_HH_
#define BE_WORLD_HELPER_PARTITION_HH_
/**************************************************************************************************/
#include    <world/stdafx.h>
#include    <rtti/engine/propertyinfo.script.hh>
#include    <rtti/value.hh>
#include    <world/helper/outputstream.hh>


namespace BugEngine { namespace World
{

template< typename T, typename TAIL >
struct Partition;

namespace Helper
{

template< typename T, typename T2, typename TAIL >
struct PartitionProductGetter
{
    static const Kernel::Product<T>& getProduct(const Partition<T2, TAIL>& partition)
    {
        return PartitionProductGetter<T, typename TAIL::Type, typename TAIL::Tail>::getProduct(partition);
    }
};

template< typename T, typename TAIL >
struct PartitionProductGetter<T, T, TAIL>
{
    static const Kernel::Product<T>& getProduct(const Partition<T, TAIL>& partition)
    {
        return partition.stream.product;
    }
};

}

template< typename T, typename TAIL >
struct Partition : public TAIL
{
    enum { Index = TAIL::Index+1 };
    typedef T Type;
    typedef TAIL Tail;
    const OutputStream<T> stream;
    Partition(weak<Task::ITask> task)
        :   TAIL(task)
        ,   stream(task)
    {
    }

    static const istring name();
    template< typename T2 >
    static RTTI::Value getProduct(void* from, bool isConst)
    {
        be_forceuse(isConst);
        const Partition* partition = static_cast<const Partition*>(from);
        return RTTI::Value(RTTI::Value::ByRef(Helper::PartitionProductGetter<T2, T, Tail>::getProduct(*partition)));
    }
    static void buildList(minitl::array< raw<const RTTI::Class> >::iterator index)
    {
        *index = be_typeid<T>::klass();
        Tail::buildList(index + 1);
    }
private:
    Partition(const Partition& other);
    Partition& operator=(const Partition& other);
};


template< typename T, typename TAIL >
const istring Partition<T, TAIL>::name()
{
    return istring(minitl::format<4096u>("%s+%s")
                   | be_typeid<T>::klass()->name
                   | Partition<typename TAIL::Type, typename TAIL::Tail>::name());
}

template< typename T >
struct Partition<T, void>
{
public:
    enum { Index = 0 };
    typedef T Type;
    typedef void Tail;
    const OutputStream<T> stream;
    Partition(weak<Task::ITask> task)
        :   stream(task)
    {
    }
    static const istring name();
    template< typename T2 >
    static RTTI::Value getProduct(void* from, bool isConst)
    {
        be_forceuse(isConst);
        const Partition* partition = static_cast<const Partition*>(from);
        return RTTI::Value(RTTI::Value::ByRef(Helper::PartitionProductGetter<T2, T, Tail>::getProduct(*partition)));
    }
    static void buildList(minitl::array< raw<const RTTI::Class> >::iterator index)
    {
        *index = be_typeid<T>::klass();
    }

private:
    Partition(const Partition& other);
    Partition& operator=(const Partition& other);
};


template< typename T >
const istring Partition<T, void>::name()
{
    return be_typeid<T>::klass()->name;
}


template< typename PARTITION, u32 INDEX, typename T, typename TAIL >
struct PartitionPropertyInfo
{
    static inline void fillProperty(RTTI::Property properties[])
    {
        typedef PartitionPropertyInfo<PARTITION,
                                      INDEX+1,
                                      typename TAIL::Type,
                                      typename TAIL::Tail> PropertyParent;
        RTTI::Property property = {
            {0},
            be_typeid<T>::klass()->name,
            be_typeid<PARTITION>::type(),
            be_typeid< const Kernel::Product<T>& >::type(),
            &PARTITION::template getProduct<T>
        };
        new (&properties[INDEX]) RTTI::Property(property);
        PropertyParent::fillProperty(properties);
    }
};

template< typename PARTITION, u32 INDEX,  typename T >
struct PartitionPropertyInfo<PARTITION, INDEX, T, void>
{
    static inline void fillProperty(RTTI::Property properties[])
    {
        RTTI::Property property = {
            {0},
            be_typeid<T>::klass()->name,
            be_typeid<PARTITION>::type(),
            be_typeid< const Kernel::Product<T>& >::type(),
            &PARTITION::template getProduct<T>
        };
        new (&properties[INDEX]) RTTI::Property(property);
    }
};

template< typename T >
struct Partition_BugHelper
{

    enum
    {
        PropertyCount = 1 + T::Index
    };
    static RTTI::staticarray<const RTTI::Property> getPartitionProperties()
    {
        static byte s_propertyBuffer[PropertyCount * sizeof(RTTI::Property)];
        RTTI::Property* properties = reinterpret_cast<RTTI::Property*>(s_propertyBuffer);

        PartitionPropertyInfo<T,
                              0,
                              typename T::Type,
                              typename T::Tail>::fillProperty(properties);
        RTTI::staticarray<const RTTI::Property> result = { PropertyCount, properties };
        return result;
    }

    static RTTI::Class s_class;
};

template< typename T >
RTTI::Class Partition_BugHelper<T>::s_class = {
    istring("Partition"),
    0,
    0,
    RTTI::ClassType_Object,
    {0},
    be_typeid<void>::klass(),
    {0},
    {0},
    getPartitionProperties(),
    {0, 0},
    {0},
    {0},
    0,
    0
};

template< typename T1 = void, typename T2 = void, typename T3 = void, typename T4 = void, typename T5 = void,
          typename T6 = void, typename T7 = void, typename T8 = void, typename T9 = void, typename T10 = void,
          typename T11 = void, typename T12 = void, typename T13 = void, typename T14 = void, typename T15 = void,
          typename T16 = void, typename T17 = void, typename T18 = void, typename T19 = void, typename T20 = void,
          typename T21 = void, typename T22 = void, typename T23 = void, typename T24 = void, typename T25 = void,
          typename T26 = void, typename T27 = void, typename T28 = void, typename T29 = void, typename T30 = void,
          typename T31 = void, typename T32 = void >
struct MakePartition
{
    typedef Partition< T1, typename MakePartition<T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15,
                                         T16, T17, T18, T19, T20, T21, T22, T23, T24, T25, T26, T27,
                                         T28, T29, T30, T31, T32 >::Result > Result;
};

template<>
struct MakePartition<>
{
    typedef void Result;
};

}}


namespace BugEngine
{

template< typename T, typename TAIL >
struct be_typeid< World::Partition<T, TAIL> >
{
    static inline RTTI::Type  type()  { return RTTI::Type::makeType(klass(), RTTI::Type::Value, RTTI::Type::Mutable, RTTI::Type::Mutable); }
    BE_EXPORT static inline raw<RTTI::Class> ns()
    {
        raw<RTTI::Class> result = { &World::Partition_BugHelper<  World::Partition<T, TAIL> >::s_class };
        return result;
    }
    BE_EXPORT static inline raw<const RTTI::Class> klass()
    {
        return ns();
    }
};


}

/**************************************************************************************************/
#endif
