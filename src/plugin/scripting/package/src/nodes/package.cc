/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.package/stdafx.h>
#include <motor/meta/property.meta.hh>
#include <motor/plugin.scripting.package/nodes/package.hh>
#include <motor/resource/resourcemanager.hh>

namespace Motor { namespace PackageBuilder { namespace Nodes {

static const istring s_name("name");

Package::Package(ifilename filename, const ref< Folder >& dataFolder)
    : m_filename(minitl::move(filename))
    , m_context(Arena::packageBuilder(), dataFolder)
    , m_plugins(Arena::packageBuilder())
    , m_nodes(Arena::packageBuilder())
{
    m_context.rootNamespace->add(inamespace("motor"), Meta::Value(motor_motor_Namespace()));
}

Package::~Package() = default;

void Package::loadPlugin(const inamespace& plugin, const inamespace& name)
{
    Plugin::Plugin< minitl::pointer > p(plugin, Plugin::Plugin< minitl::pointer >::Preload);
    if(!p)
    {
        motor_notreached();
    }
    else
    {
        m_context.rootNamespace->add(name, Meta::Value(p.pluginNamespace()));
        m_plugins.push_back(minitl::move(p));
    }
}

void Package::insertNode(istring name, const ref< Meta::AST::Node >& object)
{
    for(auto& m_node: m_nodes)
    {
        if(m_node == object)
        {
            motor_error(Log::package(), "Object added twice");
            return;
        }
    }
    m_nodes.push_back(object);
    object->setMetadata(s_name, name);
    m_context.rootNamespace->add(inamespace(name), object);
}

void Package::removeNode(const ref< Meta::AST::Node >& object)
{
    auto name = object->getMetadata(s_name).as< const istring >();
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
    motor_error(Log::package(), "Object does not exist");
}

ref< Meta::AST::Node > Package::findByName(istring name) const
{
    return m_context.rootNamespace->getNode(name);
}

void Package::createObjects(const weak< Resource::ResourceManager >&             manager,
                            minitl::vector< Plugin::Plugin< minitl::pointer > >& plugins,
                            minitl::vector< Meta::Value >&                       values)
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
    plugins = minitl::move(m_plugins);
}

void Package::diffFromPackage(const weak< Package >& /*previous*/,
                              const weak< Resource::ResourceManager >& /*manager*/)
{
    motor_forceuse(this);
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
