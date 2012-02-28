/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#ifndef BE_PACKAGE_NODES_PACKAGE_HH_
#define BE_PACKAGE_NODES_PACKAGE_HH_
/*****************************************************************************/
#include    <system/plugin.hh>

namespace BugEngine { namespace PackageBuilder { namespace Nodes
{

class Object;
class Reference;

class Package : public minitl::refcountable
{
    friend class Reference;
private:
    class Namespace : public minitl::refcountable
    {
    private:
        minitl::hashmap<istring, BugEngine::Value>  m_values;
        minitl::hashmap<istring, ref<Namespace> >   m_children;
    public:
        Namespace();
        ~Namespace();

        Value get(const inamespace& name) const;
        void add(const inamespace& name, const Value& value);
    };
private:
    minitl::vector< Plugin<void*> >     m_plugins;
    ref<Namespace>                      m_rootNamespace;
    minitl::vector< ref<Object> >       m_nodes;
    minitl::intrusive_list<Reference>   m_references;
    minitl::vector<Value>               m_values;
    Value                               m_empty;
private:
    void addReference(weak<Reference> reference);
    void resolveReference(weak<Reference> reference);
public:
    Package();
    ~Package();

    void insertNode(ref<Object> object);
    void removeNode(ref<Object> object);
    ref<Object> findByName(istring name) const;
    const BugEngine::Value& getValue(weak<const Object> object) const;

    void loadPlugin(inamespace pluginName);

    void binarySave() const;
    void textSave() const;

    void createObjects(weak<const ResourceManager> manager);
    void deleteObjects(weak<const ResourceManager> manager);
};

}}}

/*****************************************************************************/
#endif