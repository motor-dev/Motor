/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#include    <package/stdafx.h>
#include    <package/nodes/package.hh>
#include    <package/nodes/reference.hh>
#include    <package/nodes/object.hh>
#include    <system/resource/resourcemanager.hh>


namespace BugEngine { namespace PackageBuilder { namespace Nodes
{

Package::Namespace::Namespace()
    :   m_values(packageBuilderArena())
    ,   m_children(packageBuilderArena())
{
}

Package::Namespace::~Namespace()
{
}

BugEngine::Value Package::Namespace::get(const inamespace& name) const
{
    minitl::hashmap<istring, BugEngine::Value>::const_iterator it = m_values.find(name[0]);
    if (it == m_values.end())
    {
        minitl::hashmap< istring, ref<Namespace> >::const_iterator it = m_children.find(name[0]);
        if (it != m_children.end())
        {
            inamespace childname = name;
            childname.pop_front();
            return it->second->get(childname);
        }
        else
        {
            return BugEngine::Value();
        }
    }
    else if (!it->second)
    {
        return BugEngine::Value();
    }
    else
    {
        BugEngine::Value v(it->second);
        for (size_t i = 1; i < name.size(); ++i)
        {
            v = v[name[i]];
            if (!v)
            {
                return v;
            }
        }
        return v;
    }
}

void Package::Namespace::add(const inamespace& name, const BugEngine::Value& value)
{
    if (name.size() == 1)
    {
        bool inserted = m_values.insert(std::make_pair(name[0], value)).second;
        if (!inserted)
        {
            be_notreached();
        }
    }
    else
    {
        minitl::hashmap< istring, BugEngine::Value >::const_iterator it = m_values.find(name[0]);
        if (it != m_values.end())
        {
            be_notreached();
        }
        std::pair< minitl::hashmap< istring, ref<Namespace> >::iterator, bool > result = m_children.insert(std::make_pair(name[0], ref<Namespace>()));
        if (result.second)
        {
            result.first->second = ref<Namespace>::create(packageBuilderArena());
        }
        inamespace childname = name;
        childname.pop_front();
        result.first->second->add(childname, value);
    }
}


Package::Package()
    :   m_plugins(packageBuilderArena())
    ,   m_rootNamespace(ref<Namespace>::create(packageBuilderArena()))
    ,   m_nodes(packageBuilderArena())
    ,   m_values(packageBuilderArena())
{
    m_rootNamespace->add(inamespace("game"), BugEngine::Value(be_game_Namespace()));
}

Package::~Package()
{
}

void Package::insertNode(ref<Object> object)
{
    for (minitl::vector< ref<Object> >::iterator it = m_nodes.begin(); it != m_nodes.end(); ++it)
    {
        if (*it == object)
        {
            be_error("Object added twice");
            return;
        }
    }
    m_nodes.push_back(object);
}

void Package::removeNode(ref<Object> object)
{
    minitl::vector< ref<Object> >::iterator it = m_nodes.begin();
    while (it != m_nodes.end())
    {
        if (*it == object)
        {
            m_nodes.erase(it);
            return;
        }
        ++it;
    }
    be_error("Object does not exist");
}

ref<Object> Package::findByName(istring name) const
{
    minitl::vector< ref<Object> >::const_iterator it = m_nodes.begin();
    while (it != m_nodes.end())
    {
        if ((*it)->name() == name)
        {
            return *it;
        }
        ++it;
    }
    return ref<Object>();
}

const BugEngine::Value& Package::getValue(weak<const Object> object) const
{
    size_t index = 0;
    for (minitl::vector< ref<Object> >::const_iterator it = m_nodes.begin(); it != m_nodes.end(); ++it, ++index)
    {
        if ((*it) == object)
        {
            be_assert_recover(index < m_values.size(), "access to a value not yet created", return m_empty);
            be_assert(m_values[index], "access to a value not yet created");
            return m_values[index];
        }
    }
    return m_empty;
}

void Package::loadPlugin(inamespace plugin)
{
    Plugin<void*> p(plugin, Plugin<void*>::Preload);
    if (!p)
    {
        be_notreached();
    }
    else
    {
        m_plugins.push_back(p);
        m_rootNamespace->add(plugin, BugEngine::Value(p.pluginNamespace()));
    }
}

void Package::addReference(weak<Reference> reference)
{
    m_references.push_back(*reference);
    resolveReference(reference);
}

void Package::resolveReference(weak<Reference> reference)
{
    inamespace name = reference->m_name;
    if (name.size())
    {
        reference->m_value = m_rootNamespace->get(name);
        if (!reference->m_value && name.size() == 1)
        {
            reference->m_object = findByName(name[0]);
            if (!reference->m_object)
            {
                be_notreached();
            }
        }
    }
}

void Package::binarySave() const
{
}

void Package::textSave() const
{
}

void Package::createObjects(weak<const ResourceManager> manager)
{
    m_values.resize(m_nodes.size());
    for(size_t i = 0; i < m_nodes.size(); ++i)
    {
        m_values[i] = m_nodes[i]->create();
        if (be_typeid<const Resource>::type() <= m_values[i].type())
        {
            manager->load(m_values[i].type().metaclass, m_values[i].as< weak<const Resource> >());
        }
    }
}

void Package::deleteObjects(weak<const ResourceManager> manager)
{
    for(size_t i = m_values.size(); i > 0; --i)
    {
        if (be_typeid<const Resource>::type() <= m_values[i-1].type())
        {
            manager->unload(m_values[i-1].type().metaclass, m_values[i-1].as< weak<const Resource> >());
        }
    }
    m_values.clear();
}

}}}