/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.package/stdafx.h>
#include <motor/meta/engine/propertyinfo.meta.hh>
#include <motor/plugin.scripting.package/nodes/package.hh>
#include <motor/resource/resourcemanager.hh>

namespace Motor { namespace PackageBuilder { namespace Nodes {

static const istring s_name("name");

Package::Package(const ifilename& filename, ref< Folder > dataFolder)
    : m_filename(filename)
    , m_context(Arena::packageBuilder(), dataFolder)
    , m_plugins(Arena::packageBuilder())
    , m_nodes(Arena::packageBuilder())
{
    m_context.rootNamespace->add(inamespace("motor"), Meta::Value(motor_motor_Namespace()));
}

Package::~Package()
{
}

void Package::loadPlugin(inamespace plugin, inamespace name)
{
    Plugin::Plugin< void* > p(plugin, Plugin::Plugin< void* >::Preload);
    if(!p)
    {
        motor_notreached();
    }
    else
    {
        m_plugins.push_back(p);
        m_context.rootNamespace->add(name, Meta::Value(p.pluginNamespace()));
    }
}

void Package::insertNode(const istring name, ref< Meta::AST::Node > object)
{
    for(minitl::vector< ref< Meta::AST::Node > >::iterator it = m_nodes.begin();
        it != m_nodes.end(); ++it)
    {
        if(*it == object)
        {
            motor_error("Object added twice");
            return;
        }
    }
    m_nodes.push_back(object);
    object->setMetadata(s_name, name);
    m_context.rootNamespace->add(inamespace(name), object);
}

void Package::removeNode(ref< Meta::AST::Node > object)
{
    istring name = object->getMetadata(s_name).as< const istring >();
    m_context.rootNamespace->remove(inamespace(name), object);

    minitl::vector< ref< Meta::AST::Node > >::iterator it = m_nodes.begin();
    while(it != m_nodes.end())
    {
        if(*it == object)
        {
            m_nodes.erase(it);
            return;
        }
        ++it;
    }
    motor_error("Object does not exist");
}

ref< Meta::AST::Node > Package::findByName(istring name) const
{
    return m_context.rootNamespace->getNode(name);
}

void Package::createObjects(weak< Resource::ResourceManager > manager,
                            minitl::vector< Meta::Value >&    values)
{
    values.resize(m_nodes.size());
    for(size_t i = 0; i < m_nodes.size(); ++i)
    {
        m_nodes[i]->eval(motor_type< void >(), values[i]);
        if(values[i].isA(motor_type< const Resource::IDescription >()))
        {
            manager->load(values[i].type().metaclass,
                          values[i].as< weak< const Resource::IDescription > >());
        }
    }
}

void Package::diffFromPackage(weak< Package > /*previous*/,
                              weak< Resource::ResourceManager > /*manager*/)
{
    motor_unimplemented();
    // minitl::swap(previous->m_values, m_values);
    // for(size_t i = 0; i < m_nodes.size(); ++i)
    //{
    //    motor_forceuse(manager);
    //    motor_forceuse(previous);
    //}
}

const ifilename& Package::filename() const
{
    return m_filename;
}

bool Package::success() const
{
    return m_context.errorCount == 0;
}

void Package::resolve()
{
    for(minitl::vector< ref< Meta::AST::Node > >::const_iterator it = m_nodes.begin();
        it != m_nodes.end(); ++it)
    {
        (*it)->resolve(m_context);
    }
}

}}}  // namespace Motor::PackageBuilder::Nodes
