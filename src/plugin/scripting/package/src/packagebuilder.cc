/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.package/stdafx.h>
#include <buildcontext.hh>
#include <motor/plugin.scripting.package/package.script.hh>
#include <packagebuilder.hh>

int motor_package_parse(void* param);

namespace Motor {

namespace Arena {
minitl::Allocator& packageBuilder()
{
    return resource();
}
}  // namespace Arena

namespace PackageBuilder {

PackageBuilder::PackageBuilder(ref< Folder > dataFolder) : m_dataFolder(dataFolder)
{
}

PackageBuilder::~PackageBuilder()
{
}

ref< Nodes::Package > PackageBuilder::createPackage(const ifilename&                      filename,
                                                    const minitl::Allocator::Block< u8 >& buffer)
{
    BuildContext context(filename, buffer, m_dataFolder);
    motor_package_parse(&context);
    context.result->resolve();
    return context.result;
}

}  // namespace PackageBuilder
}  // namespace Motor
